"""
DRVN Progression Intelligence - v1 test endpoint
One question, one answer, gated behind a real x402 micropayment.

SETUP CHECKLIST (see README.md for full details):
  1. Wallet address to receive USDC - already filled in below.
  2. CDP secret API key (Key ID + Secret) - set as environment
     variables before running, never hardcoded here:
         export CDP_API_KEY_ID="..."
         export CDP_API_KEY_SECRET="..."
  3. Install packages:  pip install flask x402 cdp-sdk
  4. Flip PAYMENT_REQUIRED to True below once the above is done.
  5. Deploy somewhere public (Render, Railway, etc.) - see README.

Until PAYMENT_REQUIRED is True, every request is answered for free
so you can test the endpoint logic without needing real credentials.
"""

import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# ---------------------------------------------------------------------
PAYMENT_REQUIRED = True        # flip to True once CDP keys are set
PRICE_USDC = "0.02"               # price per call
YOUR_WALLET_ADDRESS = "0xe7b7a8F420c3f18E04D4E7E7Ad62233640Cc1FC5"
NETWORK = "eip155:8453"           # Base mainnet. Use "eip155:84532"
                                   # (Base Sepolia) if you want a free
                                   # test network before real money.

CDP_API_KEY_ID = os.environ.get("CDP_API_KEY_ID", "")
CDP_API_KEY_SECRET = os.environ.get("CDP_API_KEY_SECRET", "")
# ---------------------------------------------------------------------

# The actual product: one hard-coded, expert-judgment answer.
# Add more entries here as you test more questions later.
PROGRESSION_DATA = {
    "goblet_squat_to_front_squat": {
        "endpoint": "/progression-timeline",
        "query": "goblet_squat_to_front_squat",
        "client_level": "beginner",
        "typical_timeline": "6-8 weeks",
        "confidence": "moderate",
        "basis": "coach estimate",
        "criteria_for_progression": (
            "Advance when goblet squat is performed with full depth, "
            "control, and no loss of positioning under increasing load "
            "- not on a fixed calendar schedule."
        ),
        "notes": (
            "Assumes 2-3x/week training frequency. Some clients need "
            "additional time in bodyweight squat before goblet squat is "
            "even loaded well - this can extend the timeline toward the "
            "higher end or beyond."
        ),
    }
}


@app.route("/progression-timeline", methods=["GET"])
def progression_timeline():
    exercise_pair = request.args.get("exercise", "goblet_squat_to_front_squat")
    data = PROGRESSION_DATA.get(exercise_pair)
    if not data:
        return jsonify({
            "error": f"No data for '{exercise_pair}' yet.",
            "available": list(PROGRESSION_DATA.keys())
        }), 404
    return jsonify(data), 200


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "DRVN Progression Intelligence",
        "status": "payment ON" if PAYMENT_REQUIRED else "test mode (free, no payment)",
        "try": "/progression-timeline?exercise=goblet_squat_to_front_squat"
    })


def _wire_up_real_payments():
    """
    Wraps /progression-timeline with a real x402 payment requirement,
    verified through Coinbase's facilitator using your CDP API key.

    Only runs if PAYMENT_REQUIRED is True and CDP keys are present -
    this keeps local/free testing simple and failure-proof otherwise.
    """
    from cdp.x402 import create_facilitator_config
    from x402.http.facilitator_client import HTTPFacilitatorClientSync
    from x402.http.middleware.flask import payment_middleware
    from x402.http.types import PaymentOption, RouteConfig
    from x402.server import x402ResourceServerSync
    from x402.mechanisms.evm.exact.register import register_exact_evm_server

    facilitator_config = create_facilitator_config(
        api_key_id=CDP_API_KEY_ID,
        api_key_secret=CDP_API_KEY_SECRET,
    )
    facilitator_client = HTTPFacilitatorClientSync(facilitator_config)

    server = x402ResourceServerSync(facilitator_client)
    register_exact_evm_server(server, networks=NETWORK)

    routes = {
        "/progression-timeline": RouteConfig(
            accepts=PaymentOption(
                scheme="exact",
                pay_to=YOUR_WALLET_ADDRESS,
                price=f"${PRICE_USDC}",
                network=NETWORK,
            ),
            description="Coach-judgment exercise progression timelines.",
        )
    }

    payment_middleware(app, routes, server)


if __name__ == "__main__":
    if PAYMENT_REQUIRED:
        if not (CDP_API_KEY_ID and CDP_API_KEY_SECRET):
            raise RuntimeError(
                "PAYMENT_REQUIRED is True but CDP_API_KEY_ID / "
                "CDP_API_KEY_SECRET are not set as environment variables. "
                "Set them first, or flip PAYMENT_REQUIRED back to False "
                "to keep testing for free."
            )
        _wire_up_real_payments()

    app.run(host="0.0.0.0", port=5000, debug=True)
