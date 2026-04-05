import stripe
import streamlit as st

stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]

def create_checkout_session(email):

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price": st.secrets["STRIPE_PRICE_ID"],
            "quantity": 1,
        }],
        mode="payment",
        customer_email=email,

        success_url=st.secrets["APP_URL"] + "?success=true",
        cancel_url=st.secrets["APP_URL"] + "?canceled=true",
    )

    return session.url