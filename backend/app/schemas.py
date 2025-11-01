"""Pydantic schemas for data validation."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class PianoType(str, Enum):
    """Piano types we support."""
    UPRIGHT = "upright"
    BABY_GRAND = "baby_grand"
    GRAND = "grand"


class ConversationState(str, Enum):
    """States in the conversation flow."""
    GREETING = "greeting"
    PIANO_TYPE = "piano_type"
    PICKUP_ADDRESS = "pickup_address"
    DELIVERY_ADDRESS = "delivery_address"
    STAIRS = "stairs"
    INSURANCE = "insurance"
    QUOTE_READY = "quote_ready"
    COMPLETED = "completed"


class QuoteDetails(BaseModel):
    """Structured quote information extracted from conversation."""
    piano_type: Optional[PianoType] = None
    pickup_address: Optional[str] = None
    delivery_address: Optional[str] = None
    stairs_count: Optional[int] = Field(None, ge=0)
    has_elevator: Optional[bool] = None
    has_insurance: Optional[bool] = None
    distance_km: Optional[float] = None
    quote_amount: Optional[float] = None


class ConversationSession(BaseModel):
    """Active conversation session state."""
    call_sid: str
    phone_number: str
    state: ConversationState = ConversationState.GREETING
    quote_details: QuoteDetails = Field(default_factory=QuoteDetails)
    transcript: list[dict] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.utcnow)


class QuoteCalculationResult(BaseModel):
    """Result of quote calculation."""
    base_price: float
    distance_charge: float
    stairs_charge: float
    insurance_charge: float
    total: float
    distance_km: float
