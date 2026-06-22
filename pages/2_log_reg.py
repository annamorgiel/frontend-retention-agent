import streamlit as st
import requests
from src.gemini_client import ask_gemini

st.set_page_config(page_title="API 1: Full Profile Predictor", layout="wide", initial_sidebar_state="collapsed")

# MACBOOK OPTIMIZED CSS
st.markdown(
    """
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"], [data-testid="stHeader"] { display: none !important; }
        .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
        div[data-testid="stVerticalBlock"] > div { gap: 0.3rem !important; }
    </style>
    """,
    unsafe_allow_html=True
)

nav_col, _ = st.columns([3, 1])
with nav_col:
    page_selected = st.segmented_control(
        label="Nav", options=["🏠 Home Portal", "📊 API 1 Predictor", "⚡ API 2 Predictor"],
        default="📊 API 1 Predictor", label_visibility="collapsed"
    )

if page_selected == "🏠 Home Portal": st.switch_page("app.py")
elif page_selected == "⚡ API 2 Predictor": st.switch_page("pages/3_kkbox.py")

st.markdown("### 📊 API 1: Logistic Regression Classifier")

inputs_are_open = "prediction_result" not in st.session_state

with st.expander("👤 Configure Subscriber Metrics", expanded=inputs_are_open):
    left_main, right_main = st.columns(2, gap="medium")

    with left_main:
        col_a, col_b = st.columns(2)
        with col_a:
            gender = st.selectbox("Gender", ["Female", "Male"])
            subscription_type = st.selectbox("Sub Type", ["Basic", "Standard", "Premium"])
            paperless_billing = st.selectbox("Paperless", ["No", "Yes"])
            total_charges = st.number_input("Total Charges", value=1919.76, step=0.01)
        with col_b:
            account_age = st.number_input("Acct Age (Mos)", value=24)
            payment_method = st.selectbox("Payment", ["Mailed check", "Electronic check", "Credit card", "Bank transfer"])
            monthly_charges = st.number_input("Monthly $", value=79.99, step=0.01)
            support_tickets = st.number_input("Tickets/Mo", value=1)

    with right_main:
        col_c, col_d = st.columns(2)
        with col_c:
            content_type = st.selectbox("Content", ["Movies", "TV Shows", "Both"])
            viewing_hours = st.number_input("Hrs/Week", value=15.5)
            downloads = st.number_input("Downloads/Mo", value=5)
            user_rating = st.slider("Rating", 1.0, 5.0, 4.5)
            parental_control = st.selectbox("Parental Control", ["No", "Yes"])
        with col_d:
            genre_preference = st.selectbox("Genre", ["Action", "Comedy", "Drama", "Sci-Fi", "Thriller"])
            avg_duration = st.number_input("Avg Mins", value=120)
            watchlist_size = st.number_input("Watchlist Size", value=12)
            device_registered = st.selectbox("Device", ["Computer", "Mobile", "Tablet", "TV"])
            multi_device = st.selectbox("Multi-Device", ["Yes", "No"])
            subtitles = st.selectbox("Subtitles", ["Yes", "No"])

    # Button moved INSIDE the expander to save massive vertical space
    run_prediction = st.button("🚀 Run Churn Prediction", use_container_width=True, type="primary")

if run_prediction:
    payload = { "AccountAge": int(account_age), "MonthlyCharges": float(monthly_charges), "TotalCharges": float(total_charges), "SubscriptionType": subscription_type, "PaymentMethod": payment_method, "PaperlessBilling": paperless_billing, "ContentType": content_type, "MultiDeviceAccess": multi_device, "DeviceRegistered": device_registered, "ViewingHoursPerWeek": float(viewing_hours), "AverageViewingDuration": float(avg_duration), "ContentDownloadsPerMonth": int(downloads), "GenrePreference": genre_preference, "UserRating": float(user_rating), "SupportTicketsPerMonth": int(support_tickets), "Gender": gender, "WatchlistSize": int(watchlist_size), "ParentalControl": parental_control, "SubtitlesEnabled": subtitles }
    with st.spinner("Analyzing..."):
        try:
            response = requests.get("https://retention-agent-651418512573.europe-west1.run.app/predict", params=payload)
            if response.status_code == 200:
                st.session_state.prediction_result = response.json()
                st.session_state.last_payload = payload
                st.rerun()
        except requests.exceptions.ConnectionError: st.error("❌ Connection Failed.")

if "prediction_result" in st.session_state:
    if st.button("🔄 Reset Profile"):
        st.session_state.pop("prediction_result", None)
        st.rerun()

    out_col1, out_col2 = st.columns([1, 2], gap="large")
    with out_col1:
        st.markdown("##### 📋 API Output")
        st.json(st.session_state.prediction_result)
    with out_col2:
        if st.button("✨ Ask Gemini for Retention Insights", use_container_width=True):
            prompt = f"Expert retention analyst. Subscriber Data: {st.session_state.last_payload} Prediction: {st.session_state.prediction_result}. Provide: 1. Exec summary of churn risk. 2. Three concrete action items."
            with st.spinner("Calculating..."):
                st.write(ask_gemini(prompt))
