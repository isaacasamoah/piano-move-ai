"""
Voice Agent Test - The Voyager Way

Simple, obvious test that proves the core logic works.
No complex test framework. Just run it and see.
"""

import json
import asyncio
from pathlib import Path
from voice_agent import load_config, build_claude_prompt, claude_turn
from calculators.piano_quote import calculate_piano_quote


def test_config_loading():
    """Test that config loads correctly."""
    print("\n🔧 TEST 1: Config Loading")
    print("=" * 50)

    config = load_config("+12299223706")

    assert config is not None, "❌ Config not found!"
    assert config["business_id"] == "sydney_piano_movers", "❌ Wrong business!"
    assert config["agent"]["name"] == "Alex", "❌ Wrong agent name!"

    print(f"✅ Config loaded: {config['display_name']}")
    print(f"✅ Agent: {config['agent']['name']}")
    print(f"✅ Fields to extract: {', '.join(config['extract'].keys())}")

    return config


def test_prompt_building(config):
    """Test that Claude prompt builds correctly."""
    print("\n📝 TEST 2: Prompt Building")
    print("=" * 50)

    # Mock session
    session = {
        "data": {
            "piano_type": None,
            "pickup_address": None,
            "delivery_address": None,
            "stairs_count": None,
            "has_insurance": None
        },
        "transcript": []
    }

    prompt = build_claude_prompt(config, session)

    assert "Alex" in prompt, "❌ Agent name not in prompt!"
    assert "piano_type" in prompt, "❌ Fields not in prompt!"
    assert "EXTRACT" in prompt, "❌ Instructions not in prompt!"

    print("✅ Prompt built successfully")
    print(f"✅ Prompt length: {len(prompt)} characters")
    print("\n--- PROMPT PREVIEW ---")
    print(prompt[:500] + "...\n")

    return session


async def test_conversation_flow(config, session):
    """Test a complete conversation with Claude."""
    print("\n💬 TEST 3: Conversation Flow")
    print("=" * 50)

    # Simulate conversation
    conversation = [
        "It's a baby grand",
        "34 Smith Street, Brisbane",
        "45 Green Street, Brisbane",
        "Yeah, 3 at pickup and 7 at delivery",
        "Yes please"
    ]

    for i, user_speech in enumerate(conversation, 1):
        print(f"\n👤 Customer: {user_speech}")

        try:
            response = await claude_turn(user_speech, config, session)

            print(f"🤖 Agent: {response['message']}")
            if response.get('extracted'):
                print(f"📊 Extracted: {response['extracted']}")

            if response.get('is_complete'):
                print("\n✅ Conversation complete!")
                break

        except Exception as e:
            print(f"❌ Error: {e}")
            raise

    # Check all fields were extracted
    print("\n--- FINAL EXTRACTED DATA ---")
    for field, value in session["data"].items():
        status = "✅" if value is not None else "❌"
        print(f"{status} {field}: {value}")

    assert session["data"]["piano_type"] is not None, "❌ Piano type not extracted!"
    assert session["data"]["pickup_address"] is not None, "❌ Pickup address not extracted!"

    return session


def test_quote_calculation(config, session):
    """Test quote calculator."""
    print("\n💰 TEST 4: Quote Calculation")
    print("=" * 50)

    quote = calculate_piano_quote(session["data"], config)

    assert quote["total"] > 0, "❌ Quote total is zero!"
    assert "piano_type" in quote, "❌ Quote missing piano_type!"

    print("✅ Quote calculated successfully")
    print("\n--- QUOTE BREAKDOWN ---")
    print(f"Piano Type: {quote['piano_type']}")
    print(f"Base Price: ${quote['base_price']:.2f}")
    print(f"Distance ({quote['distance_km']}km): ${quote['distance_cost']:.2f}")
    print(f"Stairs ({quote['stairs_count']}): ${quote['stairs_cost']:.2f}")
    if quote['has_insurance']:
        print(f"Insurance: ${quote['insurance_cost']:.2f}")
    print(f"\n🎯 TOTAL: ${quote['total']:.2f}")

    return quote


async def main():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("🧪 VOICE AGENT TEST SUITE - THE VOYAGER WAY")
    print("=" * 50)

    try:
        # Test 1: Config loading
        config = test_config_loading()

        # Test 2: Prompt building
        session = test_prompt_building(config)

        # Test 3: Conversation flow (requires ANTHROPIC_API_KEY)
        import os
        if os.getenv("ANTHROPIC_API_KEY"):
            session = await test_conversation_flow(config, session)

            # Test 4: Quote calculation
            quote = test_quote_calculation(config, session)

            print("\n" + "=" * 50)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 50)
            print("\n✅ Config loads")
            print("✅ Prompts build correctly")
            print("✅ Claude extracts data from conversation")
            print("✅ Quote calculator works")
            print("\n🚀 Ready to ship to production!")

        else:
            print("\n⚠️  Skipping conversation test (no ANTHROPIC_API_KEY)")
            print("✅ Config and prompt tests passed")
            print("💡 Set ANTHROPIC_API_KEY to test full conversation flow")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
