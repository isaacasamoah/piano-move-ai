"""Quick test script to verify setup."""

import sys


def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")

    try:
        import fastapi
        print("✓ FastAPI")
    except ImportError as e:
        print(f"✗ FastAPI: {e}")
        return False

    try:
        import twilio
        print("✓ Twilio")
    except ImportError as e:
        print(f"✗ Twilio: {e}")
        return False

    try:
        import anthropic
        print("✓ Anthropic")
    except ImportError as e:
        print(f"✗ Anthropic: {e}")
        return False

    try:
        import httpx
        print("✓ HTTPX")
    except ImportError as e:
        print(f"✗ HTTPX: {e}")
        return False

    try:
        import geopy
        print("✓ Geopy")
    except ImportError as e:
        print(f"✗ Geopy: {e}")
        return False

    try:
        import structlog
        print("✓ Structlog")
    except ImportError as e:
        print(f"✗ Structlog: {e}")
        return False

    try:
        import pydantic
        print("✓ Pydantic")
    except ImportError as e:
        print(f"✗ Pydantic: {e}")
        return False

    print("\n✓ All imports successful!")
    return True


def test_app_modules():
    """Test that app modules can be imported."""
    print("\nTesting app modules...")

    try:
        from app.config import get_settings
        print("✓ app.config")
    except Exception as e:
        print(f"✗ app.config: {e}")
        return False

    try:
        from app.schemas import ConversationState, QuoteDetails
        print("✓ app.schemas")
    except Exception as e:
        print(f"✗ app.schemas: {e}")
        return False

    try:
        from app.conversation import get_or_create_session
        print("✓ app.conversation")
    except Exception as e:
        print(f"✗ app.conversation: {e}")
        return False

    try:
        from app.quote_engine import calculate_quote
        print("✓ app.quote_engine")
    except Exception as e:
        print(f"✗ app.quote_engine: {e}")
        return False

    try:
        from app.twilio_handler import handle_incoming_call
        print("✓ app.twilio_handler")
    except Exception as e:
        print(f"✗ app.twilio_handler: {e}")
        return False

    try:
        from app.main import app
        print("✓ app.main")
    except Exception as e:
        print(f"✗ app.main: {e}")
        return False

    print("\n✓ All app modules loaded successfully!")
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("PianoMove AI - Setup Test")
    print("=" * 50)

    success = True

    if not test_imports():
        success = False
        print("\n❌ Import test failed!")
        print("Run: pip install -r requirements.txt")

    if not test_app_modules():
        success = False
        print("\n❌ App module test failed!")

    if success:
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your API keys to .env")
        print("3. Run: python -m app.main")
        print("4. Test: curl http://localhost:8000/health")
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)
