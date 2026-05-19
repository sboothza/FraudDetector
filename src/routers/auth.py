import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import create_access_token
from dependencies import get_db
from exceptions import UnauthorizedError
from repositories.user_repository import UserRepository
from schemas import LoginRequest, TokenResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    session: Session = Depends(get_db),
) -> TokenResponse:
    user_repo = UserRepository(session)
    user = user_repo.verify_username_password(credentials.username, credentials.password)
    if user is None:
        logger.info("Failed login for user '%s'", credentials.username)
        raise UnauthorizedError("Incorrect username or password")

    logger.info("Successful login for user '%s'", user.username)
    access_token = create_access_token(
        subject=user.username,
        roles=[role.name for role in user.roles],
    )
    return TokenResponse(access_token=access_token)
