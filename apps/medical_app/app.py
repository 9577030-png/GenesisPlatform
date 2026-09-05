import logging

import uvicorn

from medical_app.config import settings


logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
    uvicorn.run(
        "medical_app.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )