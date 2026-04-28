import hashlib
import hmac

from fastapi import HTTPException, Request, status

from app.core.config import settings


async def verify_github_signature(request: Request) -> bytes:
    body = await request.body()
    signature = request.headers.get('X-Hub-Signature-256', '')
    if not settings.github_webhook_secret:
        raise HTTPException(status_code=500, detail='Missing GITHUB_WEBHOOK_SECRET')
    expected = 'sha256=' + hmac.new(
        settings.github_webhook_secret.encode('utf-8'),
        body,
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid webhook signature')
    return body
