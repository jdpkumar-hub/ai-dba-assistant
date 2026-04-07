from flask import Flask, request
import stripe
from supabase import create_client
import os

app = Flask(__name__)

# 🔐 Stripe
stripe.api_key = "sk_test_51TIgBOLpPn2nuTvMNXCNhRpiUkDGlSDGmL21Pb4liOnpz86GgQwoe91KpBHpS1PHZyYxtA2vmY0Y6xsZnFQcwvPr00Rb83zsGx"   # your STRIPE SECRET KEY
endpoint_secret = "whsec_OK6ig3uDMnDTHWrhSb2QVy50YAkPKrF9"    # webhook secret

# 🗄 Supabase
SUPABASE_URL = "https://wequqsbvhydvugifevhm.supabase.co"
SUPABASE_KEY = "sb_publishable_ZOfGu0PLriJqtJLdmk6Bkg_mJ3HrURB"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/webhook", methods=["POST"])
def webhook():
    print("🔥 WEBHOOK HIT")

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        print("❌ Signature error:", e)
        return "Error", 400

    # 🎯 EVENT: PAYMENT SUCCESS
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # 🔑 Extract email (IMPORTANT FIX)
        email = session.get("customer_details", {}).get("email")

        print(f"💰 Payment success for {email}")

        if email:
            # 🔥 UPDATE USER ROLE TO PRO
            supabase.table("users").update({
                "role": "pro"
            }).eq("email", email).execute()

            print(f"✅ Upgraded {email} to PRO")

    return "Success", 200


if __name__ == "__main__":
    app.run(port=5000)