import json

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import verify_github_signature
from app.services.review_service import ReviewService

router = APIRouter(prefix='/api')


@router.post('/webhooks/github')
async def github_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    body = await verify_github_signature(request)
    event = request.headers.get('X-GitHub-Event', '')
    payload = json.loads(body.decode('utf-8'))

    if event != 'pull_request':
        return {'ok': True, 'ignored': True, 'reason': f'Unsupported event: {event}'}

    service = ReviewService(db)
    return service.handle_pull_request_event(payload)
