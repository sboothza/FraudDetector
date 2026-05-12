from fastapi import APIRouter, HTTPException, status

from auth import create_access_token
from dependencies import CreateSession
from repositories.user_repository import UserRepository
from schemas import LoginRequest, TokenResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest) -> TokenResponse:
    session = CreateSession()
    user_repo = UserRepository(session)
    user = user_repo.verify_username_password(credentials.username, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user.username,
        roles=[role.name for role in user.roles],
    )
    return TokenResponse(access_token=access_token)
