import streamlit as st
import requests
from src.gemini_client import ask_gemini

# 1. Page Config & CSS
st.set_page_config(page_title="API 1: Full Profile Predictor", layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"], [data-testid="stHeader"] { display: none !important; }
        @keyframes fadeIn { 0% { opacity: 0; transform: translateY(15px); } 100% { opacity: 1; transform: translateY(0); } }
        .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; animation: fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        div[data-testid="stVerticalBlock"] > div { gap: 0.3rem !important; }
    </style>
    """, unsafe_allow_html=True
)

# 2. Navigation
nav_col, _ = st.columns([3, 1])
with nav_col:
    page_selected = st.segmented_control(
        label="Nav", options=["🏠 Home Portal", "📊 API 1 Predictor", "⚡ API 2 Predictor"],
        default="📊 API 1 Predictor", label_visibility="collapsed", key="nav_p2"
    )
if page_selected == "🏠 Home Portal": st.switch_page("app.py")
elif page_selected == "⚡ API 2 Predictor": st.switch_page("pages/3_kkbox.py")

st.markdown("### 📊 API 1: Logistic Regression Classifier (with Explanations)")
inputs_are_open = "prediction_result" not in st.session_state

# 3. Inputs
with st.expander("👤 Configure Subscriber Metrics", expanded=inputs_are_open):
    left_main, right_main = st.columns(2, gap="medium")
    with left_main:
        col_a, col_b = st.columns(2)
        with col_a:
            gender = st.selectbox("Gender", ["Female", "Male"], key="p2_gender")
            subscription_type = st.selectbox("Sub Type", ["Basic", "Standard", "Premium"], key="p2_subtype")
            paperless_billing = st.selectbox("Paperless", ["No", "Yes"], key="p2_paperless")
            total_charges = st.number_input("Total Charges", value=1919.76, step=0.01, key="p2_total_charges")
        with col_b:
            account_age = st.number_input("Acct Age (Mos)", value=24, key="p2_age")
            payment_method = st.selectbox("Payment", ["Mailed check", "Electronic check", "Credit card", "Bank transfer"], key="p2_payment")
            monthly_charges = st.number_input("Monthly $", value=79.99, step=0.01, key="p2_monthly_charges")
            support_tickets = st.number_input("Tickets/Mo", value=1, key="p2_tickets")
    with right_main:
        col_c, col_d = st.columns(2)
        with col_c:
            content_type = st.selectbox("Content", ["Movies", "TV Shows", "Both"], key="p2_content")
            viewing_hours = st.number_input("Hrs/Week", value=15.5, key="p2_hours")
            downloads = st.number_input("Downloads/Mo", value=5, key="p2_downloads")
            user_rating = st.slider("Rating", 1.0, 5.0, 4.5, key="p2_rating")
            parental_control = st.selectbox("Parental Control", ["No", "Yes"], key="p2_parental")
        with col_d:
            genre_preference = st.selectbox("Genre", ["Action", "Comedy", "Drama", "Sci-Fi", "Thriller"], key="p2_genre")
            avg_duration = st.number_input("Avg Mins", value=120, key="p2_duration")
            watchlist_size = st.number_input("Watchlist Size", value=12, key="p2_watchlist")
            device_registered = st.selectbox("Device", ["Computer", "Mobile", "Tablet", "TV"], key="p2_device")
            multi_device = st.selectbox("Multi-Device", ["Yes", "No"], key="p2_multidevice")
            subtitles = st.selectbox("Subtitles", ["Yes", "No"], key="p2_subtitles")

    run_prediction = st.button("🚀 Run Prediction & Explanation Analysis", use_container_width=True, type="primary", key="p2_btn_submit")

# 4. API Execution
if run_prediction:
    payload = {
        "AccountAge": int(account_age), "MonthlyCharges": float(monthly_charges), "TotalCharges": float(total_charges),
        "SubscriptionType": subscription_type, "PaymentMethod": payment_method, "PaperlessBilling": paperless_billing,
        "ContentType": content_type, "MultiDeviceAccess": multi_device, "DeviceRegistered": device_registered,
        "ViewingHoursPerWeek": float(viewing_hours), "AverageViewingDuration": float(avg_duration),
        "ContentDownloadsPerMonth": int(downloads), "GenrePreference": genre_preference, "UserRating": float(user_rating),
        "SupportTicketsPerMonth": int(support_tickets), "Gender": gender, "WatchlistSize": int(watchlist_size),
        "ParentalControl": parental_control, "SubtitlesEnabled": subtitles
    }

    BASE_URL = "https://retention-agent-api-306889378080.europe-west1.run.app"

    with st.spinner("Analyzing subscriber data and calculating explanations..."):
        try:
            res_pred = requests.get(f"{BASE_URL}/predict", params=payload, timeout=7)
            if res_pred.status_code == 200:
                st.session_state.prediction_result = res_pred.json()
                st.session_state.last_payload = payload

                # Resilient Explanation Routing
                try:
                    res_expl = requests.get(f"{BASE_URL}/explain", params=payload, timeout=5)
                    if res_expl.status_code != 200:
                        res_expl = requests.post(f"{BASE_URL}/explain", json=payload, timeout=5)

                    if res_expl.status_code == 200:
                        st.session_state.explanation_result = res_expl.json()
                    else:
                        st.session_state.explanation_result = {"Notice": f"Explanation API returned HTTP {res_expl.status_code}."}
                except Exception:
                    st.session_state.explanation_result = {"Notice": "Explanation API was unreachable."}

                st.rerun()
            else:
                st.error(f"❌ Main Predict Endpoint Failed: {res_pred.status_code}")
                st.code(res_pred.text)
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Cloud service connection error: {e}")

# 5. Output & Gemini
if "prediction_result" in st.session_state:
    if st.button("🔄 Reset Profile", key="p2_btn_reset"):
        st.session_state.pop("prediction_result", None)
        st.session_state.pop("explanation_result", None)
        st.rerun()

    out_col1, out_col2 = st.columns([1, 2], gap="large")
    with out_col1:
        st.markdown("##### 📋 Prediction Output")
        st.json(st.session_state.prediction_result)
        st.markdown("##### 🔍 Feature Explanations")
        st.json(st.session_state.explanation_result)

    with out_col2:
        if st.button("✨ Ask Gemini for Data-Driven Strategies", use_container_width=True, key="p2_btn_gemini"):
            prompt = f"""
            You are an expert customer retention data scientist.
            Profile: {st.session_state.last_payload}
            Churn Probability: {st.session_state.prediction_result}
            Feature Explanations: {st.session_state.explanation_result}

            Tasks:
            1. Write an executive summary. Explicitly reference the top 2 features from the explanations to explain why the model made this specific prediction.
            2. Provide 3 highly specific user interventions designed to directly counteract the top risk vectors.
            """
            with st.spinner("Gemini is analyzing the explanation drivers..."):
                st.write(ask_gemini(prompt))
