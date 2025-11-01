"""Quote calculation engine for piano moving."""

from typing import Tuple
import structlog
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from app.schemas import QuoteDetails, PianoType, QuoteCalculationResult

logger = structlog.get_logger()

# Pricing constants
BASE_PRICES = {
    PianoType.UPRIGHT: 200.0,
    PianoType.BABY_GRAND: 350.0,
    PianoType.GRAND: 500.0,
}

PRICE_PER_KM = 1.50  # $1.50 per kilometer
PRICE_PER_STAIR = 15.0  # $15 per stair
INSURANCE_RATE = 0.15  # 15% of subtotal


async def calculate_distance(address1: str, address2: str) -> float:
    """
    Calculate distance between two addresses in kilometers.

    Uses geopy with Nominatim (OpenStreetMap) geocoder.
    For production, consider using Google Maps API for better accuracy.
    """
    try:
        geolocator = Nominatim(user_agent="pianomove-ai")

        # Geocode addresses
        location1 = geolocator.geocode(address1)
        location2 = geolocator.geocode(address2)

        if not location1 or not location2:
            logger.warning(
                "geocoding_failed",
                address1=address1,
                address2=address2,
                found1=location1 is not None,
                found2=location2 is not None
            )
            # Fallback: estimate 50km if geocoding fails
            return 50.0

        # Calculate geodesic distance
        coords1 = (location1.latitude, location1.longitude)
        coords2 = (location2.latitude, location2.longitude)
        distance = geodesic(coords1, coords2).kilometers

        logger.info(
            "distance_calculated",
            address1=address1,
            address2=address2,
            distance_km=round(distance, 2)
        )

        return distance

    except Exception as e:
        logger.error("distance_calculation_error", error=str(e))
        # Fallback distance
        return 50.0


async def calculate_quote(details: QuoteDetails) -> QuoteCalculationResult:
    """
    Calculate quote based on piano details.

    Pricing formula:
    - Base price (depends on piano type)
    - Distance charge (per km)
    - Stairs charge (per stair)
    - Insurance (15% of subtotal)
    """
    # Base price
    base_price = BASE_PRICES.get(details.piano_type, BASE_PRICES[PianoType.UPRIGHT])

    # Calculate distance
    distance_km = await calculate_distance(
        details.pickup_address,
        details.delivery_address
    )

    # Distance charge
    distance_charge = distance_km * PRICE_PER_KM

    # Stairs charge
    stairs_charge = (details.stairs_count or 0) * PRICE_PER_STAIR

    # Subtotal
    subtotal = base_price + distance_charge + stairs_charge

    # Insurance
    insurance_charge = subtotal * INSURANCE_RATE if details.has_insurance else 0.0

    # Total
    total = subtotal + insurance_charge

    result = QuoteCalculationResult(
        base_price=base_price,
        distance_charge=distance_charge,
        stairs_charge=stairs_charge,
        insurance_charge=insurance_charge,
        total=round(total, 2),
        distance_km=round(distance_km, 2)
    )

    logger.info(
        "quote_calculated",
        piano_type=details.piano_type.value if details.piano_type else "unknown",
        distance_km=result.distance_km,
        stairs=details.stairs_count,
        insurance=details.has_insurance,
        total=result.total
    )

    return result


def format_quote_summary(details: QuoteDetails, calculation: QuoteCalculationResult) -> str:
    """
    Format a professional quote summary for SMS delivery.
    """
    piano_name = details.piano_type.value.replace('_', ' ').title() if details.piano_type else "Piano"

    summary = f"""🎹 PianoMove Quote

Piano: {piano_name}
Route: {calculation.distance_km:.0f}km
Stairs: {details.stairs_count or 0}
Insurance: {"Yes" if details.has_insurance else "No"}

BREAKDOWN:
Base: ${calculation.base_price:.2f}
Distance: ${calculation.distance_charge:.2f}
Stairs: ${calculation.stairs_charge:.2f}
Insurance: ${calculation.insurance_charge:.2f}

TOTAL: ${calculation.total:.2f}

Valid for 7 days.
Book: pianomove.com.au
Questions? Reply to this number.
"""
    return summary
