"""
Piano Moving Quote Calculator

Business logic for calculating piano moving quotes.
Separated from agent logic - easy to test and modify.
"""

from typing import Dict, Any


def calculate_piano_quote(data: Dict[str, Any], business: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate piano moving quote.

    Args:
        data: Extracted customer data (piano_type, addresses, stairs, insurance)
        business: Business config (for pricing)

    Returns:
        Quote dictionary with breakdown
    """
    # Base prices by piano type
    base_prices = {
        "upright": 200.00,
        "baby_grand": 350.00,
        "grand": 500.00
    }

    piano_type = data.get("piano_type", "").lower().replace(" ", "_")
    base_price = base_prices.get(piano_type, 200.00)

    # Calculate distance (mock for MVP - would use geocoding API)
    # For now, assume 12km
    distance_km = 12
    distance_cost = distance_km * 1.50

    # Stairs cost
    stairs_count = data.get("stairs_count", 0)
    stairs_cost = stairs_count * 15.00

    # Subtotal
    subtotal = base_price + distance_cost + stairs_cost

    # Insurance (15% of subtotal)
    has_insurance = data.get("has_insurance", False)
    insurance_cost = subtotal * 0.15 if has_insurance else 0.00

    # Total
    total = subtotal + insurance_cost

    return {
        "piano_type": piano_type.replace("_", " ").title(),
        "pickup_address": data.get("pickup_address"),
        "delivery_address": data.get("delivery_address"),
        "distance_km": distance_km,
        "stairs_count": stairs_count,
        "has_insurance": has_insurance,
        "base_price": round(base_price, 2),
        "distance_cost": round(distance_cost, 2),
        "stairs_cost": round(stairs_cost, 2),
        "insurance_cost": round(insurance_cost, 2),
        "subtotal": round(subtotal, 2),
        "total": round(total, 2)
    }
