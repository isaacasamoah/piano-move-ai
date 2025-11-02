"""
Business configuration management for multi-tenant platform.

Loads business-specific configs from database or JSON files.
"""

from typing import Dict, Any, Optional
import json
from pathlib import Path
import structlog

logger = structlog.get_logger()


class BusinessConfigManager:
    """Manages business configurations for multi-tenant platform."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize config manager.

        Args:
            config_dir: Directory containing business config JSON files
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent / "configs"

        self.config_dir = Path(config_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}

    def load_config(self, business_id: str) -> Dict[str, Any]:
        """
        Load business configuration.

        Args:
            business_id: Unique business identifier

        Returns:
            Business configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        # Check cache first
        if business_id in self._cache:
            logger.debug("business_config_cache_hit", business_id=business_id)
            return self._cache[business_id]

        # Load from file
        # In production, this would load from database
        config_file = self.config_dir / f"{business_id}.json"

        if not config_file.exists():
            logger.error("business_config_not_found", business_id=business_id)
            raise FileNotFoundError(f"Config not found for business: {business_id}")

        with open(config_file, 'r') as f:
            config = json.load(f)

        # Cache it
        self._cache[business_id] = config

        logger.info("business_config_loaded", business_id=business_id, business_type=config.get("business_type"))

        return config

    def get_business_from_phone(self, phone_number: str) -> Optional[str]:
        """
        Get business ID from Twilio phone number.

        In production, this would query database:
        SELECT business_id FROM businesses WHERE twilio_number = ?

        For now, simple mapping.
        """
        # Hardcoded mapping for MVP
        # In production: database lookup
        phone_to_business = {
            "+12299223706": "piano_moving_001",
            # Add more as needed
        }

        business_id = phone_to_business.get(phone_number)

        if business_id:
            logger.info("business_identified_from_phone", phone_number=phone_number, business_id=business_id)
        else:
            logger.warning("business_not_found_for_phone", phone_number=phone_number)

        return business_id

    def reload_config(self, business_id: str):
        """Reload configuration from source (clears cache)."""
        if business_id in self._cache:
            del self._cache[business_id]
            logger.info("business_config_cache_cleared", business_id=business_id)

        return self.load_config(business_id)


# Singleton instance
_config_manager = None


def get_config_manager() -> BusinessConfigManager:
    """Get singleton config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = BusinessConfigManager()
    return _config_manager


def load_business_config(business_id: str) -> Dict[str, Any]:
    """
    Convenience function to load business config.

    Args:
        business_id: Business identifier

    Returns:
        Business configuration dictionary
    """
    manager = get_config_manager()
    return manager.load_config(business_id)


def get_business_from_twilio_number(twilio_number: str) -> Optional[str]:
    """
    Get business ID from Twilio phone number.

    Args:
        twilio_number: Twilio phone number (e.g., "+12299223706")

    Returns:
        Business ID or None if not found
    """
    manager = get_config_manager()
    return manager.get_business_from_phone(twilio_number)
