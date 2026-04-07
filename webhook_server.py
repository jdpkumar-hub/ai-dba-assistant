from flask import Flask, request, jsonify
import stripe
from supabase import create_client
import os

app = Flask(__name__)

# =========================
# CONFIG
# =========================
stripe.api_key = "sk_test_51TIgBOLpPn2nuTvMNXCNhRpiUkDGlSDGmL21Pb4liOnpz86GgQwoe91KpBHpS1PHZyYxtA2vmY0Y6xsZnFQcwvPr00Rb83zsGx"   # 🔴 YOUR SECRET KEY
endpoint_secret = "whsec_OK6ig3uDMnDTHWrhSb2QVy50YAkPKrF9"    # 🔴 FROM STRIPE WEBHOOK

SUPABASE_URL = "https://wequqsbvhydvugifevhm.supabase.co"
SUPABASE_KEY = "sb_publishable_ZOfGu0PLriJqtJLdmk6Bkg_mJ3HrURB"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# WEBHOOK
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        print("❌ Signature error:", e)
        return "Error", 400

    # =========================
    # PAYMENT SUCCESS
    # =========================
    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        email = session.get("customer_email")

        print("✅ Payment success for:", email)

        if email:
            supabase.table("users").update({
                "role": "pro"
            }).eq("email", email).execute()

            print("✅ Role updated to PRO")

    return jsonify({"status": "success"}), 200


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(port=5000)