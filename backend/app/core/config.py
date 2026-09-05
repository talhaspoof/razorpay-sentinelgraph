from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "SentinelGraph"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Razorpay Webhook Secret for HMAC verification
    RAZORPAY_WEBHOOK_SECRET: str = os.getenv("RAZORPAY_WEBHOOK_SECRET", "rzp_secret_test_key_12345")
    
    # AI / LLM Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    
    # Risk Thresholds
    DEFAULT_RISK_THRESHOLD: float = 0.70
    STEP_UP_AUTH_THRESHOLD: float = 0.45
    
    # Economic Cost Matrix Defaults (in INR)
    FALSE_POSITIVE_COST_MARGIN: float = 0.15  # Merchant margin loss ratio (15%)
    AVERAGE_TICKET_SIZE: float = 2500.0       # Avg transaction size
    FRAUD_INVESTIGATION_COST: float = 150.0   # Operational triage cost per alert
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
