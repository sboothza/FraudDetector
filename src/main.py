from fastapi import Depends, FastAPI
from auth import get_current_subject
from configuration import CONNECTION_STRING, TIME_WINDOW
from routers import auth as auth_router, process as process_router
from schemas import ApiResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils import parse_timedelta



app = FastAPI(title="Fraudulent Transaction API", version="1.0.0")

app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(process_router.router, prefix="/process", tags=["process"])

@app.get("/", response_model=ApiResponse)
async def index(_: str = Depends(get_current_subject)):
    """Health check endpoint."""
    return ApiResponse(
        code=200,
        message="Fraudulent Transaction API",
        success=True,
        data={},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
