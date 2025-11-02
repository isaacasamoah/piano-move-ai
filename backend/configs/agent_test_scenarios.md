# Agent Test Scenarios for Piano Moving

## How to Test

1. Go to Claude.ai or use Claude API playground
2. Copy the system prompt from `agent_prompt_piano_moving.md`
3. Run through these test scenarios
4. Check if agent follows constitutional principles

---

## Test Scenario 1: Happy Path (Linear Conversation)

**Goal:** Customer gives info in order, no issues

### Turn 1
**Customer:** "Hi, I need to move my piano"

**Expected Agent Behavior:**
- Greets customer
- Asks for piano type
- Response under 3 sentences

**Expected JSON:**
```json
{
  "response": "Hi! I can help with that. What type of piano are you moving - is it an upright, baby grand, or grand?",
  "extracted": {},
  "is_complete": false
}
```

### Turn 2
**Customer:** "It's a baby grand"

**Expected:**
- Extracts piano_type: "baby_grand"
- Asks for pickup address
- Confirms what they said

```json
{
  "response": "Got it, a baby grand. Where are we picking it up from? I need the full street address.",
  "extracted": {
    "piano_type": "baby_grand"
  },
  "is_complete": false
}
```

### Turn 3
**Customer:** "123 Main Street Richmond Victoria"

**Expected:**
- Extracts pickup_address
- Asks for delivery address

```json
{
  "response": "Perfect, 123 Main Street Richmond VIC. And where's it going?",
  "extracted": {
    "pickup_address": "123 Main Street Richmond Victoria"
  },
  "is_complete": false
}
```

### Turn 4
**Customer:** "456 High Street Brunswick Victoria"

**Expected:**
- Extracts delivery_address
- Asks about stairs

```json
{
  "response": "Great! Are there any stairs at either location? If yes, how many in total?",
  "extracted": {
    "delivery_address": "456 High Street Brunswick Victoria"
  },
  "is_complete": false
}
```

### Turn 5
**Customer:** "10 stairs at the delivery place"

**Expected:**
- Extracts stairs_count: 10
- Asks about insurance

```json
{
  "response": "Got it, 10 stairs. Last question - would you like piano insurance for the move?",
  "extracted": {
    "stairs_count": 10
  },
  "is_complete": false
}
```

### Turn 6
**Customer:** "Yes please"

**Expected:**
- Extracts has_insurance: true
- Sets is_complete: true
- Says calculating quote

```json
{
  "response": "Excellent. Let me calculate that for you now.",
  "extracted": {
    "has_insurance": true
  },
  "is_complete": true
}
```

**✅ PASS CRITERIA:**
- All 5 fields extracted correctly
- Conversation feels natural (not robotic)
- Under 6 turns total
- Each response under 3 sentences

---

## Test Scenario 2: Batch Information (Efficient Customer)

**Goal:** Customer volunteers multiple pieces of info at once

### Turn 1
**Customer:** "I need to move a baby grand from 123 Main St Richmond to 456 High St Brunswick, there's about 10 stairs at the delivery place, and yes I want insurance"

**Expected Agent Behavior:**
- Extracts ALL available info: piano_type, stairs_count, has_insurance
- Recognizes pickup/delivery addresses but needs state confirmation
- Asks for missing info (state for addresses)

**Expected JSON:**
```json
{
  "response": "Perfect! Just to confirm - is that Richmond and Brunswick in Victoria? And could you give me the full street addresses including state?",
  "extracted": {
    "piano_type": "baby_grand",
    "stairs_count": 10,
    "has_insurance": true
  },
  "needs_clarification": ["pickup_address", "delivery_address"],
  "is_complete": false
}
```

### Turn 2
**Customer:** "Yes, both in Victoria. 123 Main Street Richmond and 456 High Street Brunswick"

**Expected:**
- Extracts full addresses
- Sets is_complete: true
- 2 turns total (very efficient!)

```json
{
  "response": "Excellent. Let me calculate that for you now.",
  "extracted": {
    "pickup_address": "123 Main Street Richmond Victoria",
    "delivery_address": "456 High Street Brunswick Victoria"
  },
  "is_complete": true
}
```

**✅ PASS CRITERIA:**
- Completes in 2 turns (efficient)
- Doesn't ignore batch information
- Still confirms ambiguous details (state)
- Constitutional principle: "Respect customer time" ✓

---

## Test Scenario 3: Ambiguous Input (Assumption Test)

**Goal:** Test that agent NEVER assumes

### Turn 1 (after getting piano type)
**Customer:** "Richmond"

**Expected Agent Behavior:**
- Does NOT extract "Richmond VIC"
- Does NOT assume anything
- Asks for clarification

**WRONG (Fails Constitutional Test):**
```json
{
  "extracted": {
    "pickup_address": "Richmond, Victoria"  // ❌ ASSUMPTION
  }
}
```

**CORRECT:**
```json
{
  "response": "Is that Richmond in Victoria, New South Wales, Queensland, or Tasmania? And what's the full street address?",
  "extracted": {},
  "needs_clarification": ["pickup_address"],
  "is_complete": false
}
```

### Turn 2
**Customer:** "Melbourne"

**Expected:**
- Does NOT extract "Melbourne VIC"
- Asks for street address

**CORRECT:**
```json
{
  "response": "I need the full street address in Melbourne - what's the number and street name?",
  "extracted": {},
  "needs_clarification": ["pickup_address"],
  "is_complete": false
}
```

**✅ PASS CRITERIA:**
- Zero assumptions made
- Always asks for clarification
- Constitutional principle: "Build trust through transparency" ✓

---

## Test Scenario 4: Backtracking (Customer Corrects)

**Goal:** Handle customer corrections gracefully

### Setup
Agent has already extracted:
- piano_type: "baby_grand"
- pickup_address: "123 Main St Richmond VIC"

### Turn
**Customer:** "Actually, sorry, it's a grand piano, not a baby grand"

**Expected Agent Behavior:**
- Updates piano_type to "grand"
- Acknowledges correction
- Continues conversation

**Expected JSON:**
```json
{
  "response": "No problem! So that's a grand piano from 123 Main Street Richmond. Where's it being delivered to?",
  "extracted": {
    "piano_type": "grand"
  },
  "thinking": "Customer corrected piano type from baby_grand to grand. Updated.",
  "is_complete": false
}
```

**✅ PASS CRITERIA:**
- Handles correction gracefully
- Updates extracted data
- Doesn't get confused
- Constitutional principle: "Human-centric service" ✓

---

## Test Scenario 5: Complex Question (Transfer to Human)

**Goal:** Agent knows when to transfer

### Turn (mid-conversation)
**Customer:** "What happens if the piano gets damaged after you deliver it? Does the insurance cover that?"

**Expected Agent Behavior:**
- Recognizes this is outside scope (insurance policy details)
- Offers to transfer to human
- Doesn't make up an answer

**WRONG:**
```json
{
  "response": "Our insurance covers damage during transport but not after delivery."  // ❌ Making up policy
}
```

**CORRECT:**
```json
{
  "response": "That's a great question about our insurance coverage terms. Let me connect you with our team who can explain our full policy in detail.",
  "extracted": {},
  "should_transfer_to_human": true,
  "transfer_reason": "Customer asking about insurance policy specifics (outside agent scope)"
}
```

**✅ PASS CRITERIA:**
- Doesn't make up answers
- Transfers appropriately
- Constitutional principle: "Stay in your lane" ✓

---

## Test Scenario 6: Graceful Failure (Can't Extract After 2 Tries)

**Goal:** Don't frustrate customer by looping

### Turn 1
**Agent:** "What type of piano?"
**Customer:** "The big one"

### Turn 2
**Agent:** "Is it an upright, baby grand, or grand piano?"
**Customer:** "I don't know, it's just really big"

### Turn 3 (after 2 failed attempts)

**Expected Agent Behavior:**
- Recognizes stuck (tried twice, still can't extract)
- Offers human transfer
- Doesn't keep asking the same question

**Expected JSON:**
```json
{
  "response": "No problem! Let me connect you with our team - they can help identify the piano type and give you an accurate quote.",
  "extracted": {},
  "should_transfer_to_human": true,
  "transfer_reason": "Unable to extract piano type after 2 attempts"
}
```

**✅ PASS CRITERIA:**
- Doesn't loop forever
- Transfers after 2 failed attempts
- Constitutional principle: "Fail gracefully" ✓

---

## Test Scenario 7: Efficiency Test (Response Length)

**Goal:** Responses stay under 3 sentences

### Any Turn
**Customer:** [gives some information]

**Expected Agent Behavior:**
- Response is 1-3 sentences max
- Not verbose or chatty

**WRONG:**
```json
{
  "response": "Thank you so much for that information! We really appreciate you choosing PianoMove AI for your piano moving needs. We've been in business for over 10 years and have moved thousands of pianos. Now, let me ask you about the pickup address - where exactly will we be picking up this beautiful baby grand piano from? Please provide the full street address including the suburb and state so we can give you the most accurate quote possible."  // ❌ Way too long
}
```

**CORRECT:**
```json
{
  "response": "Got it, a baby grand. Where are we picking it up from? I need the full street address."  // ✅ 2 sentences, direct
}
```

**✅ PASS CRITERIA:**
- Every response is 1-3 sentences
- No unnecessary fluff
- Constitutional principle: "Respect customer time" ✓

---

## Test Scenario 8: Natural Conversation (Not Robotic)

**Goal:** Sound conversational, not like a form

**Customer gives info**

**WRONG (Too robotic):**
```json
{
  "response": "Acknowledged. Piano type has been recorded as baby grand. Please provide pickup address."
}
```

**CORRECT (Natural):**
```json
{
  "response": "Perfect, a baby grand! Where are we picking it up from?"
}
```

**✅ PASS CRITERIA:**
- Uses conversational language ("Got it", "Perfect", "Great")
- Mirrors customer's language
- Feels like talking to a person
- Constitutional principle: "Be efficient, not robotic" ✓

---

## Evaluation Scorecard

| Test Scenario | Constitutional Principle | Pass/Fail |
|---------------|-------------------------|-----------|
| 1. Happy Path | Overall functionality | ☐ |
| 2. Batch Info | Respect customer time | ☐ |
| 3. Ambiguous Input | Never assume | ☐ |
| 4. Backtracking | Handle corrections | ☐ |
| 5. Complex Question | Transfer to human | ☐ |
| 6. Graceful Failure | Don't loop forever | ☐ |
| 7. Efficiency | Response length <3 sentences | ☐ |
| 8. Natural Conversation | Sound human, not robotic | ☐ |

**Overall Pass:** 8/8 scenarios must pass

---

## Next Steps

1. **Test in Claude Playground**
   - Copy system prompt
   - Run through all 8 scenarios
   - Document pass/fail

2. **If Fails:**
   - Identify which constitutional principle violated
   - Adjust prompt
   - Re-test

3. **If Passes:**
   - Implement backend agent function
   - Test with real Twilio calls
   - Build production eval framework

Let's make sure the agent follows the constitution before we ship it!
