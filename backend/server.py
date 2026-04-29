from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="KYNTHIA API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============ Models ============
class QuoteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    company: Optional[str] = Field(default="", max_length=120)
    tier_interest: str = Field(pattern="^(echo|aether|cosmos|unsure)$")
    budget: Optional[str] = Field(default="", max_length=80)
    message: str = Field(min_length=1, max_length=4000)


class Quote(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    company: Optional[str] = ""
    tier_interest: str
    budget: Optional[str] = ""
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    email_sent: bool = False


# ============ Email sending (Resend) ============
async def send_quote_email(quote: Quote) -> bool:
    """Send notification email via Resend. No-op if keys not configured."""
    api_key = os.environ.get("RESEND_API_KEY", "").strip()
    sender = os.environ.get("SENDER_EMAIL", "").strip()
    admin = os.environ.get("ADMIN_EMAIL", "").strip()

    if not api_key or not sender or not admin:
        logger.info("Resend not configured (missing RESEND_API_KEY/SENDER_EMAIL/ADMIN_EMAIL). Skipping email.")
        return False

    try:
        import resend
        resend.api_key = api_key
        html = f"""
        <div style="font-family:Manrope,Arial,sans-serif;background:#0a0a0a;color:#fff;padding:32px;">
          <h2 style="letter-spacing:-0.02em;margin:0 0 16px 0;">New KYNTHIA Quote Request</h2>
          <table style="width:100%;border-collapse:collapse;color:#fff;">
            <tr><td style="padding:6px 0;color:#999;">Name</td><td>{quote.name}</td></tr>
            <tr><td style="padding:6px 0;color:#999;">Email</td><td>{quote.email}</td></tr>
            <tr><td style="padding:6px 0;color:#999;">Company</td><td>{quote.company or '-'}</td></tr>
            <tr><td style="padding:6px 0;color:#999;">Tier</td><td>{quote.tier_interest.upper()}</td></tr>
            <tr><td style="padding:6px 0;color:#999;">Budget</td><td>{quote.budget or '-'}</td></tr>
          </table>
          <hr style="border:0;border-top:1px solid #222;margin:20px 0;">
          <p style="white-space:pre-wrap;line-height:1.6;">{quote.message}</p>
          <p style="color:#666;font-size:12px;margin-top:24px;">Quote ID: {quote.id}</p>
        </div>
        """
        params = {
            "from": sender,
            "to": [admin],
            "subject": f"[KYNTHIA] New {quote.tier_interest.upper()} quote from {quote.name}",
            "html": html,
        }
        result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent via Resend: {result.get('id')}")
        return True
    except Exception as e:
        logger.error(f"Resend email failed: {e}")
        return False


# ============ Routes ============
@api_router.get("/")
async def root():
    return {"message": "KYNTHIA API", "status": "ok"}


@api_router.get("/health")
async def health():
    return {"status": "healthy", "time": datetime.now(timezone.utc).isoformat()}


@api_router.post("/quote", response_model=Quote)
async def create_quote(payload: QuoteCreate):
    quote = Quote(**payload.model_dump())
    doc = quote.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.quotes.insert_one(doc)

    email_ok = await send_quote_email(quote)
    if email_ok:
        await db.quotes.update_one({"id": quote.id}, {"$set": {"email_sent": True}})
        quote.email_sent = True
    return quote


@api_router.get("/quotes", response_model=List[Quote])
async def list_quotes():
    rows = await db.quotes.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    for r in rows:
        if isinstance(r.get('created_at'), str):
            try:
                r['created_at'] = datetime.fromisoformat(r['created_at'])
            except Exception:
                r['created_at'] = datetime.now(timezone.utc)
    return rows


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
