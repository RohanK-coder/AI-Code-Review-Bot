from __future__ import annotations

from typing import Any

from app.services.chunker import summarize_chunks


SYSTEM_POLICY = '''You are a senior software engineer reviewing a GitHub pull request.
Return strict JSON only.
Be conservative. Only create comments when there is a real issue.
Prefer bugs, security risks, broken edge cases, incorrect assumptions, performance traps, missing tests, or maintainability risks.
Do not nitpick style.
Each comment must map to a real changed file and a plausible changed line.
'''


def build_review_prompt(
    repo: str,
    pr_number: int,
    head_sha: str,
    changed_files: list[dict[str, Any]],
    memory: list[dict[str, Any]],
) -> str:
    file_sections: list[str] = []
    for file in changed_files:
        file_sections.append(
            f"PATH: {file['path']}\n"
            f"STATUS: {file['status']}\n"
            f"ADDITIONS: {file['additions']}\n"
            f"DELETIONS: {file['deletions']}\n"
            f"PATCH:\n{file['patch']}\n"
            f"CONTEXT:\n{summarize_chunks(file['chunks'])}"
        )

    memory_section = "None"
    if memory:
        memory_section = "\n\n".join(
            f"Past review on {item.get('path', 'unknown')}: "
            f"{item.get('issue', '')} | suggestion: {item.get('suggestion', '')}"
            for item in memory
        )

    changed_files_section = "\n\n".join(file_sections)

    return f"""
{SYSTEM_POLICY}

REPOSITORY: {repo}
PR_NUMBER: {pr_number}
HEAD_SHA: {head_sha}

PAST REVIEW MEMORY:
{memory_section}

CHANGED FILES:
{changed_files_section}

Output JSON with:
- summary: short paragraph
- verdict: approve | comment | request_changes
- confidence: 0..1
- memory_used: boolean
- comments: list of objects with fields path, line, severity, category, title, body, suggestion

Rules:
- Max 8 comments.
- Avoid duplicate comments.
- Only use line numbers >= 1.
- If no real issues, return an empty comments list and verdict approve or comment.
""".strip()