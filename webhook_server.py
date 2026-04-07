from flask import Flask, request, jsonify
from supabase import create_client
import json

app = Flask(__name__)

# =========================
# CONFIG (USE YOUR VALUES)
# =========================

SUPABASE_URL = st.secrets["SUPABASE_URL"]

# ✅ IMPORTANT: USE SERVICE ROLE KEY (NOT publishable)
SUPABASE_KEY =  st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# TEST ROUTE
# =========================
@app.route("/", methods=["GET"])
def home():
    return "Webhook server running"

# =========================
# WEBHOOK
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        print("\n🔥 ===== WEBHOOK HIT =====")

        payload = request.data
        event = json.loads(payload)

        event_type = event.get("type")
        print("📌 EVENT TYPE:", event_type)

        # =========================
        # HANDLE PAYMENT SUCCESS
        # =========================
        if event_type == "checkout.session.completed":

            session = event.get("data", {}).get("object", {})

            email = session.get("customer_email")

            print("📧 EMAIL:", email)

            if not email:
                print("❌ No email found")
                return "No email", 400

            # UPDATE USER ROLE
            response = supabase.table("users").update({
                "role": "pro"
            }).eq("email", email).execute()

            print("✅ UPDATED TO PRO:", response)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(port=5000)