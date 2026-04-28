from app.services.chunker import chunk_code


def test_chunk_code_returns_chunks():
    text = '\n'.join([f'line {i}' for i in range(1, 120)])
    chunks = chunk_code('demo.py', text, max_lines=40)
    assert len(chunks) >= 2
    assert chunks[0].start_line == 1
