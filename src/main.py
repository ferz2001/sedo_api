import asgi_correlation_id
import uvicorn

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from api.v1 import domain
from core.config import settings


app = FastAPI(
    title=settings.app_name,
    docs_url='/api/v1/docs',
    openapi_url='/api/v1/openapi.json',
    default_response_class=ORJSONResponse
)

app.include_router(domain.router, prefix='/api/v1/domain', tags=['billing'])

app.add_middleware(asgi_correlation_id.CorrelationIdMiddleware)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
    )
