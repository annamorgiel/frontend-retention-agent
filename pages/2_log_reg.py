import streamlit as st
import requests
from src.gemini_client import ask_gemini

# 1. Page Config & CSS
st.set_page_config(page_title="API 1: Behavioral Predictor", layout="wide", initial_sidebar_state="collapsed")
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
        label="Nav",
        options=["🏠 Home Portal", "👤 API 1: Behavioral Predictor", "💳 API 2: Transactional Predictor"],
        default="👤 API 1: Behavioral Predictor",
        label_visibility="collapsed",
        key="nav_p2"
    )
if page_selected == "🏠 Home Portal": st.switch_page("app.py")
elif page_selected == "💳 API 2: Transactional Predictor": st.switch_page("pages/3_kkbox.py")

st.markdown("### 👤 API 1: Behavioral Predictor with SHAP Explanations")

# 3. Callbacks (Mock Data & Reset)
def load_mock_api1():
    st.session_state.update({
        "p2_gender": "Male", "p2_subtype": "Premium", "p2_paperless": "Yes",
        "p2_total_charges": 1919.76, "p2_age": 24, "p2_payment": "Electronic check",
        "p2_monthly_charges": 79.99, "p2_tickets": 1, "p2_content": "Both",
        "p2_hours": 15.5, "p2_downloads": 5, "p2_rating": 4.5,
        "p2_parental": "Yes", "p2_genre": "Sci-Fi", "p2_duration": 120,
        "p2_watchlist": 12, "p2_device": "TV", "p2_multidevice": "Yes", "p2_subtitles": "Yes"
    })

def reset_api1():
    st.session_state.update({
        "p2_gender": None, "p2_subtype": None, "p2_paperless": None, "p2_total_charges": None,
        "p2_age": None, "p2_payment": None, "p2_monthly_charges": None, "p2_tickets": None,
        "p2_content": None, "p2_hours": None, "p2_downloads": None, "p2_rating": None,
        "p2_parental": None, "p2_genre": None, "p2_duration": None, "p2_watchlist": None,
        "p2_device": None, "p2_multidevice": None, "p2_subtitles": None
    })
    st.session_state.pop("prediction_result", None)
    st.session_state.pop("explanation_result", None)

inputs_are_open = "prediction_result" not in st.session_state

# 4. Inputs
with st.expander("👤 Configure Behavioral Metrics", expanded=inputs_are_open):

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button("🪄 Auto-Fill Mock Data", on_click=load_mock_api1, key="p2_mock_btn", use_container_width=True)
    with btn_col2:
        st.button("🗑️ Reset All Fields", on_click=reset_api1, key="p2_reset_fields_btn", use_container_width=True)

    st.markdown("---")

    left_main, right_main = st.columns(2, gap="medium")
    with left_main:
        col_a, col_b = st.columns(2)
        with col_a:
            gender = st.selectbox("Gender", ["Female", "Male"], index=None, key="p2_gender")
            subscription_type = st.selectbox("Sub Type", ["Basic", "Standard", "Premium"], index=None, key="p2_subtype")
            paperless_billing = st.selectbox("Paperless", ["No", "Yes"], index=None, key="p2_paperless")
            total_charges = st.number_input("Total Charges", value=None, step=0.01, key="p2_total_charges")
        with col_b:
            account_age = st.number_input("Acct Age (Mos)", value=None, step=1, key="p2_age")
            payment_method = st.selectbox("Payment", ["Mailed check", "Electronic check", "Credit card", "Bank transfer"], index=None, key="p2_payment")
            monthly_charges = st.number_input("Monthly $", value=None, step=0.01, key="p2_monthly_charges")
            support_tickets = st.number_input("Tickets/Mo", value=None, step=1, key="p2_tickets")
    with right_main:
        col_c, col_d = st.columns(2)
        with col_c:
            content_type = st.selectbox("Content", ["Movies", "TV Shows", "Both"], index=None, key="p2_content")
            viewing_hours = st.number_input("Hrs/Week", value=None, step=0.5, key="p2_hours")
            downloads = st.number_input("Downloads/Mo", value=None, step=1, key="p2_downloads")
            user_rating = st.number_input("Rating (1-5)", min_value=1.0, max_value=5.0, value=None, step=0.1, key="p2_rating")
            parental_control = st.selectbox("Parental Control", ["No", "Yes"], index=None, key="p2_parental")
        with col_d:
            genre_preference = st.selectbox("Genre", ["Action", "Comedy", "Drama", "Sci-Fi", "Thriller"], index=None, key="p2_genre")
            avg_duration = st.number_input("Avg Mins", value=None, step=1, key="p2_duration")
            watchlist_size = st.number_input("Watchlist Size", value=None, step=1, key="p2_watchlist")
            device_registered = st.selectbox("Device", ["Computer", "Mobile", "Tablet", "TV"], index=None, key="p2_device")
            multi_device = st.selectbox("Multi-Device", ["Yes", "No"], index=None, key="p2_multidevice")
            subtitles = st.selectbox("Subtitles", ["Yes", "No"], index=None, key="p2_subtitles")

    run_prediction = st.button("🚀 Run Behavioral Prediction & SHAP Analysis", use_container_width=True, type="primary", key="p2_btn_submit")

# 5. API Execution & Validation
if run_prediction:
    inputs_list = [account_age, monthly_charges, total_charges, subscription_type, payment_method, paperless_billing, content_type, multi_device, device_registered, viewing_hours, avg_duration, downloads, genre_preference, user_rating, support_tickets, gender, watchlist_size, parental_control, subtitles]

    if any(i is None for i in inputs_list):
        st.warning("⚠️ Please fill in all fields or click 'Auto-Fill Mock Data' before running the prediction.")
    else:
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

        with st.spinner("Analyzing subscriber data and fetching SHAP values..."):
            try:
                res_pred = requests.get(f"{BASE_URL}/predict", params=payload, timeout=7)
                if res_pred.status_code == 200:
                    st.session_state.prediction_result = res_pred.json()
                    st.session_state.last_payload = payload

                    try:
                        res_expl = requests.get(f"{BASE_URL}/explain", params=payload, timeout=5)
                        if res_expl.status_code != 200:
                            res_expl = requests.post(f"{BASE_URL}/explain", json=payload, timeout=5)

                        if res_expl.status_code == 200:
                            st.session_state.explanation_result = res_expl.json()
                        else:
                            st.session_state.explanation_result = {"Notice": f"SHAP API returned HTTP {res_expl.status_code}."}
                    except Exception:
                        st.session_state.explanation_result = {"Notice": "SHAP API was unreachable."}

                    st.rerun()
                else:
                    st.error(f"❌ Main Predict Endpoint Failed: {res_pred.status_code}")
                    st.code(res_pred.text)
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Cloud service connection error: {e}")

# 6. Output & Gemini (Frontend Filtering)
if "prediction_result" in st.session_state:
    out_col1, out_col2 = st.columns([1, 2], gap="large")

    with out_col2:
        with st.container(border=True):
            st.markdown("**⚙️ Select number of SHAP features for the explainability analysis**")
            shap_limit = st.radio(
                "Number of features to display and analyze:",
                options=["1", "2", "3", "4", "5"],
                index=4, horizontal=True, key="p2_shap_limit"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ✂️ Slice the SHAP results based on the radio button without re-running the API
        raw_shap = st.session_state.explanation_result
        display_shap = raw_shap

        limit = int(shap_limit)
        if isinstance(raw_shap, dict) and "Notice" not in raw_shap:
            display_shap = dict(list(raw_shap.items())[:limit])
        elif isinstance(raw_shap, list):
            display_shap = raw_shap[:limit]

        if st.button("✨ Ask Gemini for SHAP-Guided Strategies", use_container_width=True, key="p2_btn_gemini"):
            prompt = f"""
            You are an expert customer retention data scientist specializing in behavioral profiling.
            Profile: {st.session_state.last_payload}
            Churn Probability: {st.session_state.prediction_result}
            SHAP Influences: {display_shap}

            Tasks:
            1. Write an executive summary. Explicitly reference the top {shap_limit} features from the SHAP context to explain why the behavioral model made this specific prediction.
            2. Provide highly specific user interventions designed to directly neutralize the risk vectors identified by the SHAP values.
            """
            with st.spinner("Gemini is analyzing the SHAP force plot drivers..."):
                st.write(ask_gemini(prompt))

    with out_col1:
        st.markdown("##### 📋 Prediction Output")
        st.json(st.session_state.prediction_result)
        st.markdown("##### 🔍 Computed SHAP Values")
        st.json(display_shap)
