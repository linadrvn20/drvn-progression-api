# DRVN Progression Intelligence — v1 test

One endpoint. One question. One answer, in your coaching judgment.
Gated behind a real x402 micropayment via Coinbase's facilitator.

## What's done already
- ✅ Wallet address (yours, already in server.py)
- ✅ CDP secret API key created
- ✅ x402 + cdp-sdk Python packages — install with:
  ```
  pip install flask x402 cdp-sdk
  ```
- ✅ Payment-gate code written and tested (constructs correctly)

## Run it locally — free/test mode (default)
No setup needed beyond the pip install above.
```
python3 server.py
```
Visit: `http://localhost:5000/progression-timeline?exercise=goblet_squat_to_front_squat`
Every request is answered for free — good for checking the data/logic
before turning payments on.

## Turn payments on
1. Set your CDP key as environment variables (use your real values —
   the ones from "Download API key" earlier, not placeholders):
   ```
   export CDP_API_KEY_ID="your-key-id-here"
   export CDP_API_KEY_SECRET="your-secret-here"
   ```
2. Open server.py and change:
   ```python
   PAYMENT_REQUIRED = True
   ```
3. Run it again: `python3 server.py`

Now a request without payment gets a 402 response instead of the
data — that's the mechanic working correctly. A bot with a wallet
that supports x402 would pay automatically and receive the data.

**Housekeeping:** the API key was visible in a screenshot during
setup, so once you've confirmed payments work, go back to the CDP
dashboard (Settings → API keys), delete this key, create a fresh
one, and update your environment variables with the new values.

## Network note
`NETWORK = "eip155:8453"` in server.py means Base mainnet — real
USDC, real money, same as the Kronos example. If you'd rather test
with fake money first, change it to `"eip155:84532"` (Base Sepolia
testnet) — nothing costs anything real there, but you'd need testnet
USDC in your wallet to test paying it yourself.

## Deploy it publicly (so bots can actually reach it)
Right now this only runs on your own machine. To go live:
- **Render.com** or **Railway.app** — both have free tiers, connect
  this folder, they auto-detect Flask and give you a public URL
- Once deployed, set `CDP_API_KEY_ID` and `CDP_API_KEY_SECRET` as
  environment variables in their dashboard (not in the code)

## Getting found by bots
x402 has an emerging discovery network ("Bazaar") — worth checking
Coinbase's x402 docs for the current listing process, since this
part of the ecosystem is new and still changing.

## Adding more questions later
Add more entries to the `PROGRESSION_DATA` dictionary in server.py —
same format as the goblet-to-front-squat one. Only expand this once
you've confirmed the first one gets real traffic — no point building
a library nobody queries yet.
