from fastapi import Request, status
from fastapi.responses import JSONResponse
from backend.app.utils.logger import logger

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception at {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred while processing your request.",
            "detail": str(exc)
        }
    )
