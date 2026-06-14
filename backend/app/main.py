from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import agents, courses, health, product


app = FastAPI(
    title="EduAgent Backend",
    description="Stage 1 mock backend for the EduAgent MVP.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(courses.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(product.router)
app.include_router(product.router, prefix="/api")
