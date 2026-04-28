from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

try:
    from tree_sitter_languages import get_parser
except Exception:  # pragma: no cover
    get_parser = None


LANGUAGE_BY_EXTENSION = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'tsx',
    '.java': 'java',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
    '.c': 'c',
    '.h': 'c',
    '.cpp': 'cpp',
    '.hpp': 'cpp',
}


@dataclass
class CodeChunk:
    path: str
    start_line: int
    end_line: int
    content: str


def detect_language(path: str) -> str | None:
    for extension, language in LANGUAGE_BY_EXTENSION.items():
        if path.endswith(extension):
            return language
    return None


def chunk_code(path: str, patch: str, max_lines: int = 80) -> list[CodeChunk]:
    language = detect_language(path)
    if get_parser and language:
        try:
            return _chunk_with_tree_sitter(path, patch, language, max_lines=max_lines)
        except Exception:
            pass
    return _chunk_by_lines(path, patch, max_lines=max_lines)


def _chunk_with_tree_sitter(path: str, text: str, language: str, max_lines: int = 80) -> list[CodeChunk]:
    parser = get_parser(language)
    tree = parser.parse(bytes(text, 'utf-8'))
    root = tree.root_node
    lines = text.splitlines()
    chunks: list[CodeChunk] = []

    for node in root.children:
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        if end_line - start_line + 1 > max_lines:
            continue
        snippet = '\n'.join(lines[start_line - 1:end_line])
        if snippet.strip():
            chunks.append(CodeChunk(path=path, start_line=start_line, end_line=end_line, content=snippet))

    if not chunks:
        return _chunk_by_lines(path, text, max_lines=max_lines)
    return chunks[:12]


def _chunk_by_lines(path: str, text: str, max_lines: int = 80) -> list[CodeChunk]:
    lines = text.splitlines()
    chunks: list[CodeChunk] = []
    for i in range(0, len(lines), max_lines):
        start = i + 1
        end = min(i + max_lines, len(lines))
        snippet = '\n'.join(lines[i:end])
        if snippet.strip():
            chunks.append(CodeChunk(path=path, start_line=start, end_line=end, content=snippet))
    return chunks[:12]


def summarize_chunks(chunks: Iterable[CodeChunk]) -> str:
    parts = []
    for chunk in chunks:
        parts.append(f'FILE: {chunk.path} LINES {chunk.start_line}-{chunk.end_line}\n{chunk.content}')
    return '\n\n'.join(parts)
