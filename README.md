# Real-Time AI Code Review Bot (Gemini + FastAPI + Qdrant)

A production-ready starter for automatic pull request reviews using:

- **Gemini API** for code review generation and embeddings
- **FastAPI** for GitHub webhook ingestion
- **Qdrant** for semantic memory of past reviews
- **PostgreSQL** for durable review history
- **Tree-sitter** for AST-aware code chunking
- **GitHub REST API** for inline PR comments
- **GitHub Actions** for CI

## Important reality check

You can run the AI layer with only a **Gemini API key**, but to make the bot work end-to-end on GitHub you still need **GitHub credentials** too:

- `GITHUB_WEBHOOK_SECRET` to verify GitHub webhooks
- `GITHUB_TOKEN` or a GitHub App installation token to read PR files and post comments

So Gemini can replace Claude/OpenAI in the architecture, but it cannot replace GitHub authentication.

## Architecture

1. GitHub opens or updates a PR
2. GitHub sends a webhook to FastAPI
3. FastAPI fetches changed files and diffs
4. Tree-sitter extracts AST-aware chunks for context
5. Gemini embeddings are generated for codebase memory and stored in Qdrant
6. Similar past reviews are retrieved from Qdrant
7. Gemini generates structured review JSON
8. Bot posts inline PR comments and persists the run to PostgreSQL

## What changed from your screenshot

Your original card used:

- Claude 3.5 Sonnet API
- OpenAI Embeddings

This build swaps those for Gemini:

- `GEMINI_MODEL=gemini-2.5-flash` for review generation
- `GEMINI_EMBEDDING_MODEL=gemini-embedding-001` by default for text embeddings

The Gemini API supports generation and embeddings through the Google GenAI SDK, and Google recommends that SDK as the official production library.

## Quick start

### 1. Clone and configure

```bash
cp .env.example .env
```

Fill in:

- `GEMINI_API_KEY`
- `GITHUB_WEBHOOK_SECRET`
- `GITHUB_TOKEN`

### 2. Start locally

```bash
docker compose up --build
```

### 3. Expose your webhook

Use a tunnel like ngrok and point GitHub webhooks to:

```text
POST /api/webhooks/github
```

### 4. Create the webhook in GitHub

- Content type: `application/json`
- Secret: your `GITHUB_WEBHOOK_SECRET`
- Events:
  - Pull requests
  - Pull request review comments (optional)
  - Push (optional, for pre-indexing)

## Local development without Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

You still need PostgreSQL and Qdrant running.

## Deployment

### Railway

- Create one service for the app from this repo
- Add PostgreSQL plugin
- Add Qdrant separately or use hosted Qdrant
- Set the environment variables from `.env.example`

### Fly.io

- `fly launch`
- Attach Postgres or use external Postgres
- Use hosted Qdrant or a separate volume-backed service

## Directory layout

```text
app/
  api/               # HTTP routes
  clients/           # Gemini, GitHub, Qdrant wrappers
  core/              # config, db, logging, security
  models/            # SQLAlchemy models
  schemas/           # Pydantic schemas
  services/          # review, chunking, embeddings, comments
  main.py
```

## Notes on Gemini

Google's official docs show the Gemini API supports both generation and embeddings. The docs also list newer embedding models such as Gemini Embedding 2, while `gemini-embedding-001` remains available for text-focused use cases.

This starter defaults to `gemini-embedding-001` for predictable text embeddings, but you can switch to a newer Gemini embedding model later.

## Security checklist

- Verify webhook HMAC signatures
- Use a least-privilege GitHub token or GitHub App
- Limit max diff size and max file count
- Skip binary and generated files
- Store minimal code context in memory if your repo is sensitive

## Testing

```bash
pytest
```
# AI-Code-Review-Bot
