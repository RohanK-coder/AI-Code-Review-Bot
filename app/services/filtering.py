from __future__ import annotations

SKIP_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.pdf', '.lock', '.svg', '.map', '.min.js', '.min.css'
}

SKIP_PATH_PARTS = {'node_modules', 'dist', 'build', '.next', '.turbo', 'coverage', 'vendor'}


def should_review_file(path: str, status: str, patch: str | None) -> bool:
    if status == 'removed':
        return False
    if patch is None:
        return False
    if any(part in path.split('/') for part in SKIP_PATH_PARTS):
        return False
    for ext in SKIP_EXTENSIONS:
        if path.endswith(ext):
            return False
    return True
