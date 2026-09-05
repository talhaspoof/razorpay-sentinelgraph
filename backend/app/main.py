from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.webhooks import router as webhooks_router
from app.api.graph_api import router as graph_router
from app.api.analytics_api import router as analytics_router
from app.api.copilot_api import router as copilot_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Coordinated Abuse-Ring & Sybil Sentinel for Razorpay Risk Management"
)

# Enable CORS for Frontend Development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(webhooks_router, prefix=settings.API_V1_STR)
app.include_router(graph_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(copilot_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "endpoints": {
            "webhooks": f"{settings.API_V1_STR}/webhooks/razorpay",
            "graph_overview": f"{settings.API_V1_STR}/graph/overview",
            "syndicates": f"{settings.API_V1_STR}/graph/syndicates",
            "analytics_cost_curve": f"{settings.API_V1_STR}/analytics/cost-curve",
            "copilot_chat": f"{settings.API_V1_STR}/copilot/chat"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
