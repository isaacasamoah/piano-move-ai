# Deploying Agent to Railway

## Quick Deploy

### 1. Commit Changes

```bash
git add .
git commit -m "Add Claude agent with A/B testing capability"
git push origin main
```

Railway will auto-deploy from GitHub.

### 2. Set Environment Variables in Railway

Go to Railway dashboard → Your project → Variables:

```bash
# Required (use your actual values from .env file)
ANTHROPIC_API_KEY=sk-ant-api03-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+12299223706

# Agent Configuration
USE_AGENT=True
AGENT_ROLLOUT_PERCENTAGE=100

# Already set
PORT=8000
```

### 3. Deploy

Railway will auto-deploy on git push. Watch logs:

```bash
railway logs
```

### 4. Test

Call +1 (229) 922-3706 and talk to the agent!

---

## A/B Testing Configurations

### 100% Agent (Current)
```bash
USE_AGENT=True
AGENT_ROLLOUT_PERCENTAGE=100
```

### 50% Agent, 50% State Machine
```bash
USE_AGENT=True
AGENT_ROLLOUT_PERCENTAGE=50
```

### 100% State Machine (Rollback)
```bash
USE_AGENT=False
```

### 10% Agent (Cautious Rollout)
```bash
USE_AGENT=True
AGENT_ROLLOUT_PERCENTAGE=10
```

---

## How A/B Testing Works

1. **Consistent Assignment**
   - Each call_sid gets hashed
   - Same call_sid always goes to same handler
   - Ensures multi-turn conversations don't switch mid-call

2. **Percentage Distribution**
   - `AGENT_ROLLOUT_PERCENTAGE=50` → 50% of calls use agent
   - Distribution is random but stable per call

3. **Logging**
   - Every webhook logs which handler was used:
   ```json
   {
     "event": "twilio_webhook",
     "call_sid": "CAxxxx",
     "handler": "agent"  // or "state_machine"
   }
   ```

---

## Monitoring After Deploy

### Check Logs for Agent Usage

```bash
railway logs | grep handler
```

Look for:
```json
{"event": "twilio_webhook", "handler": "agent", ...}
{"event": "agent_turn_complete", "extracted_fields": [...], ...}
```

### Compare Metrics

**Agent metrics to watch:**
- `agent_turn_complete` - Successful turns
- `agent_json_parse_failed` - JSON errors
- `claude_not_available_using_fallback` - Fallback usage
- `transfer_to_human` - Transfer rate

**vs State Machine:**
- `state_transition` - State changes
- `user_input` - Input processing

---

## Testing Checklist

### Test 1: Happy Path
☐ Call number
☐ Say "Baby grand"
☐ Give full addresses
☐ Say number of stairs
☐ Say "yes" to insurance
☐ Receive quote via voice
☐ Receive SMS with details

### Test 2: Batch Information
☐ Call number
☐ Say everything at once: "Baby grand from [address1] to [address2], 10 stairs, yes to insurance"
☐ Agent should extract multiple fields
☐ Complete in 2-3 turns

### Test 3: Ambiguous Input
☐ Call number
☐ Say "Baby grand"
☐ Say "Brisbane" (no street address)
☐ Agent should ask for full address
☐ Agent should NOT assume specific suburb

### Test 4: Complex Question (Transfer)
☐ Call number
☐ Ask "What happens if piano is damaged after delivery?"
☐ Agent should offer to transfer
☐ (Or gracefully explain it can't answer that)

---

## Rollback Plan

If agent has issues:

### Immediate Rollback (2 minutes)
```bash
# In Railway dashboard, set:
USE_AGENT=False
```

### Gradual Rollback (5 minutes)
```bash
# Reduce to 10%
AGENT_ROLLOUT_PERCENTAGE=10
# Monitor
# If still issues, set USE_AGENT=False
```

---

## Expected Behavior

### Agent (NEW)
- **Greeting:** "Hi! I'm Sandra from PianoMove AI. I can help you get an instant quote for moving your piano. What type of piano are you moving - is it an upright, baby grand, or grand?"
- **Responses:** 1-3 sentences, conversational
- **Efficiency:** Can extract multiple fields at once
- **Edge cases:** Transfers to human for complex questions

### State Machine (OLD)
- **Greeting:** "Hi! I'm Sandra from PianoMove AI..."
- **Responses:** Follows strict state order
- **Efficiency:** Always asks each question sequentially
- **Edge cases:** May get stuck or repeat questions

---

## Success Criteria

Agent is working if:
- ✅ Calls connect successfully
- ✅ Agent extracts data correctly (check logs)
- ✅ Quotes are calculated accurately
- ✅ SMS is delivered
- ✅ No JSON parsing errors in logs
- ✅ Conversation feels natural

---

## Troubleshooting

### "Agent not extracting data"
Check logs for:
```json
{"event": "agent_turn_complete", "extracted_fields": []}
```

Fix: Claude prompt may need tuning, or API key issue

### "JSON parse failed"
```json
{"event": "agent_json_parse_failed"}
```

Fix: Claude returning malformed JSON. Will fall back to simple response.

### "Claude not available"
```json
{"event": "claude_not_available_using_fallback"}
```

Fix: Check ANTHROPIC_API_KEY in Railway variables

### "Call connects but no response"
Check Railway logs for errors. Likely:
- Missing environment variable
- Import error in agent code

---

## Next Steps After Deploy

1. **Make test call** - Verify it works
2. **Check logs** - Confirm agent is being used
3. **Test edge cases** - Ambiguous inputs, complex questions
4. **Compare to state machine** - Make call with `USE_AGENT=False`, compare
5. **Gather feedback** - Does it feel natural?
6. **Iterate** - Adjust prompt if needed

Ready to deploy! 🚀
