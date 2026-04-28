from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.clients.gemini_client import GeminiClient
from app.clients.github_client import GitHubClient
from app.clients.qdrant_client import MemoryClient
from app.core.config import settings
from app.models.review_run import ReviewRun
from app.schemas.review import ReviewResponse
from app.services.chunker import chunk_code
from app.services.filtering import should_review_file
from app.services.prompt_builder import build_review_prompt


class ReviewService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.gemini = GeminiClient()
        self.memory = MemoryClient()

    def handle_pull_request_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        action = payload.get('action')
        if action not in {'opened', 'synchronize', 'reopened', 'ready_for_review'}:
            return {'ok': True, 'ignored': True, 'reason': f'Unsupported action: {action}'}

        repository = payload['repository']['full_name']
        pr = payload['pull_request']
        pr_number = pr['number']
        head_sha = pr['head']['sha']

        github = GitHubClient(repository)
        files = github.get_pull_request_files(pr_number)
        reviewable_files = []

        for file in files[: settings.max_diff_files]:
            path = file['filename']
            patch = file.get('patch')
            status = file.get('status', 'modified')
            if not should_review_file(path, status, patch):
                continue
            trimmed_patch = (patch or '')[: settings.max_diff_chars_per_file]
            chunks = chunk_code(path, trimmed_patch)
            reviewable_files.append(
                {
                    'path': path,
                    'status': status,
                    'additions': file.get('additions', 0),
                    'deletions': file.get('deletions', 0),
                    'patch': trimmed_patch,
                    'chunks': chunks,
                }
            )

        if not reviewable_files:
            return {'ok': True, 'ignored': True, 'reason': 'No reviewable files'}

        memory_hits = self._retrieve_memory(reviewable_files)
        prompt = build_review_prompt(repository, pr_number, head_sha, reviewable_files, memory_hits)
        review_data = self.gemini.generate_structured_review(prompt)
        review = ReviewResponse.model_validate(review_data)
        comments_posted = self._post_comments(github, pr_number, head_sha, review)
        self._persist_run(repository, pr_number, head_sha, review, comments_posted)
        self._write_memory(repository, pr_number, review)

        return {
            'ok': True,
            'repository': repository,
            'pr_number': pr_number,
            'summary': review.summary,
            'comments_posted': comments_posted,
            'verdict': review.verdict,
        }

    def _retrieve_memory(self, reviewable_files: list[dict[str, Any]]) -> list[dict[str, Any]]:
        hits: list[dict[str, Any]] = []
        for file in reviewable_files[:5]:
            vector = self.gemini.embed_text(f"{file['path']}\n{file['patch'][:4000]}")
            hits.extend(self.memory.search_memory(vector, limit=2))
        unique_hits = []
        seen = set()
        for item in hits:
            key = (item.get('path'), item.get('issue'))
            if key in seen:
                continue
            seen.add(key)
            unique_hits.append(item)
        return unique_hits[:6]

    def _post_comments(self, github: GitHubClient, pr_number: int, head_sha: str, review: ReviewResponse) -> int:
        posted = 0
        fallback_messages = []
        for comment in review.comments:
            body = f"**{comment.title}**\n\n{comment.body}"
            if comment.suggestion:
                body += f"\n\nSuggested change:\n```suggestion\n{comment.suggestion}\n```"
            try:
                github.create_inline_comment(
                    pr_number=pr_number,
                    body=body,
                    commit_id=head_sha,
                    path=comment.path,
                    line=comment.line,
                )
                posted += 1
            except Exception:
                fallback_messages.append(f"- `{comment.path}:{comment.line}` **{comment.title}** — {comment.body}")

        if fallback_messages and settings.inline_comment_fallback_to_pr_review:
            github.create_pr_review(pr_number, body='\n'.join(fallback_messages), event='COMMENT')

        if posted == 0:
            github.create_pr_review(pr_number, body=review.summary, event='COMMENT')
        return posted

    def _persist_run(self, repository: str, pr_number: int, head_sha: str, review: ReviewResponse, comments_posted: int) -> None:
        row = ReviewRun(
            repository=repository,
            pr_number=pr_number,
            head_sha=head_sha,
            status='completed',
            review_json=json.dumps(review.model_dump()),
            summary=review.summary,
            comments_posted=comments_posted,
            used_memory=review.memory_used,
        )
        self.db.add(row)
        self.db.commit()

    def _write_memory(self, repository: str, pr_number: int, review: ReviewResponse) -> None:
        for comment in review.comments:
            text = f"repo={repository}\npr={pr_number}\npath={comment.path}\ntitle={comment.title}\nbody={comment.body}\nsuggestion={comment.suggestion or ''}"
            vector = self.gemini.embed_text(text)
            self.memory.upsert_memory(
                vector,
                {
                    'repository': repository,
                    'pr_number': pr_number,
                    'path': comment.path,
                    'issue': comment.title,
                    'body': comment.body,
                    'suggestion': comment.suggestion or '',
                },
            )
