from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="", tags=["status"])


@router.get("/")
async def root():
    return JSONResponse(status_code=200, content={"status": "ok"})
