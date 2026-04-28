from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings


class GitHubClient:
    def __init__(self, repo_full_name: str) -> None:
        if not settings.github_token:
            raise ValueError('Missing GITHUB_TOKEN')
        self.repo_full_name = repo_full_name
        self.base_url = f'https://api.github.com/repos/{repo_full_name}'
        self.headers = {
            'Authorization': f'Bearer {settings.github_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        with httpx.Client(timeout=30.0, headers=self.headers) as client:
            response = client.get(f'{self.base_url}{path}', params=params)
            response.raise_for_status()
            return response.json()

    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        with httpx.Client(timeout=30.0, headers=self.headers) as client:
            response = client.post(f'{self.base_url}{path}', json=payload)
            response.raise_for_status()
            return response.json() if response.content else {}

    def get_pull_request_files(self, pr_number: int) -> list[dict[str, Any]]:
        page = 1
        files: list[dict[str, Any]] = []
        while True:
            batch = self._get(f'/pulls/{pr_number}/files', params={'per_page': 100, 'page': page})
            if not batch:
                break
            files.extend(batch)
            page += 1
        return files

    def create_inline_comment(
        self,
        pr_number: int,
        body: str,
        commit_id: str,
        path: str,
        line: int,
    ) -> Any:
        payload = {
            'body': body,
            'commit_id': commit_id,
            'path': path,
            'line': line,
            'side': 'RIGHT',
        }
        return self._post(f'/pulls/{pr_number}/comments', payload)

    def create_pr_review(self, pr_number: int, body: str, event: str = 'COMMENT') -> Any:
        payload = {'body': body, 'event': event}
        return self._post(f'/pulls/{pr_number}/reviews', payload)
