import streamlit as st
import requests
from src.gemini_client import ask_gemini

# 1. Page Config & CSS
st.set_page_config(page_title="API 2: KKBox Streaming", layout="wide", initial_sidebar_state="collapsed")
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
        default="⚡ API 2 Predictor", label_visibility="collapsed", key="nav_p3"
    )
if page_selected == "🏠 Home Portal": st.switch_page("app.py")
elif page_selected == "📊 API 1 Predictor": st.switch_page("pages/2_log_reg.py")

st.markdown("### ⚡ API 2: Sequential Transaction Engine (with SHAP Explanations)")
inputs_are_open = "kkbox_prediction_result" not in st.session_state

# 3. Inputs
with st.expander("🎵 Configure KKBox Subscriber Metrics", expanded=inputs_are_open):
    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        st.subheader("👤 Demographics")
        city = st.number_input("City Code", value=1, key="p3_city")
        gender_filled = st.selectbox("Gender", ["Female", "Male", "Unknown"], key="p3_gender")
        bd_clean = st.number_input("Age", value=28.0, key="p3_age")
        bd_was_invalid = st.selectbox("Age Invalid?", [0, 1], key="p3_invalid")
        registered_via = st.selectbox("Reg Method ID", [3, 4, 7, 9, 13], index=3, key="p3_reg")
        tenure_days = st.number_input("Tenure (Days)", value=365.0, key="p3_tenure")
    with col2:
        st.subheader("💳 Transactions")
        n_transactions = st.number_input("Total Txns", value=12.0, key="p3_txns")
        n_cancels_before_cutoff = st.number_input("Cancels Before Cutoff", value=0.0, key="p3_cancels")
        days_since_last_txn = st.number_input("Days Since Last Txn", value=15.0, key="p3_last_txn")
        latest_payment_method_id = st.number_input("Latest Pay Method ID", value=41.0, key="p3_pay_id")
        n_unique_payment_methods = st.number_input("Unique Pay Methods", value=1.0, key="p3_uniq_pay")
    with col3:
        st.subheader("💰 Financials")
        mean_actual_paid = st.number_input("Mean Paid ($)", value=149.0, key="p3_mean_paid")
        sum_actual_paid = st.number_input("Sum Paid ($)", value=1788.0, key="p3_sum_paid")
        mean_list_price = st.number_input("Mean List Price ($)", value=149.0, key="p3_list_price")
        mean_plan_days = st.number_input("Mean Plan Days", value=30.0, key="p3_plan_days")
        mean_auto_renew = st.slider("Auto-Renew Ratio", 0.0, 1.0, 1.0, key="p3_renew")
        discount_ratio = st.number_input("Discount Ratio", value=0.0, key="p3_discount")
        days_until_expiry_at_cutoff = st.number_input("Days to Expiry", value=15.0, key="p3_expiry")

    run_prediction = st.button("🚀 Run Prediction & SHAP Analysis", use_container_width=True, type="primary", key="p3_btn_submit")

# 4. API Execution
if run_prediction:
    payload = {
        "city": int(city), "bd_clean": float(bd_clean), "bd_was_invalid": int(bd_was_invalid), "gender_filled": gender_filled,
        "registered_via": int(registered_via), "tenure_days": float(tenure_days), "n_transactions": float(n_transactions),
        "n_cancels_before_cutoff": float(n_cancels_before_cutoff), "mean_actual_paid": float(mean_actual_paid),
        "sum_actual_paid": float(sum_actual_paid), "mean_list_price": float(mean_list_price), "mean_plan_days": float(mean_plan_days),
        "mean_auto_renew": float(mean_auto_renew), "n_unique_payment_methods": float(n_unique_payment_methods),
        "discount_ratio": float(discount_ratio), "days_since_last_txn": float(days_since_last_txn),
        "days_until_expiry_at_cutoff": float(days_until_expiry_at_cutoff), "latest_payment_method_id": float(latest_payment_method_id)
    }

    BASE_URL = "https://retention-agent-api-306889378080.europe-west1.run.app"

    with st.spinner("Analyzing streaming profile and calculating SHAP values..."):
        try:
            res_pred = requests.get(f"{BASE_URL}/predict_kkbox", params=payload, timeout=7)
            if res_pred.status_code == 200:
                st.session_state.kkbox_prediction_result = res_pred.json()
                st.session_state.kkbox_last_payload = payload

                # Resilient Explanation Routing
                try:
                    res_shap = requests.get(f"{BASE_URL}/explain_kkbox", params=payload, timeout=5)
                    if res_shap.status_code != 200:
                        res_shap = requests.post(f"{BASE_URL}/explain_kkbox", json=payload, timeout=5)

                    if res_shap.status_code == 200:
                        st.session_state.kkbox_shap_result = res_shap.json()
                    else:
                        st.session_state.kkbox_shap_result = {"Notice": f"SHAP API returned HTTP {res_shap.status_code}."}
                except Exception:
                    st.session_state.kkbox_shap_result = {"Notice": "SHAP API was unreachable."}

                st.rerun()
            else:
                st.error(f"❌ Main Predict Endpoint Failed: {res_pred.status_code}")
                st.code(res_pred.text)
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Cloud service connection error: {e}")

# 5. Output & Gemini
if "kkbox_prediction_result" in st.session_state:
    if st.button("🔄 Reset Profile", key="p3_btn_reset"):
        st.session_state.pop("kkbox_prediction_result", None)
        st.session_state.pop("kkbox_shap_result", None)
        st.rerun()

    out_col1, out_col2 = st.columns([1, 2], gap="large")
    with out_col1:
        st.markdown("##### 📋 Prediction Output")
        st.json(st.session_state.kkbox_prediction_result)
        st.markdown("##### 🔍 Local SHAP Values")
        st.json(st.session_state.kkbox_shap_result)

    with out_col2:
        if st.button("✨ Ask Gemini for SHAP-Guided Strategies", use_container_width=True, key="p3_btn_gemini"):
            prompt = f"""
            You are an expert customer retention data scientist specializing in streaming platforms.
            Profile: {st.session_state.kkbox_last_payload}
            Churn Probability: {st.session_state.kkbox_prediction_result}
            SHAP Influences: {st.session_state.kkbox_shap_result}

            Tasks:
            1. Write an executive summary. Explicitly reference the top 2 features from the SHAP context to explain why the model made this specific prediction.
            2. Provide 3 highly specific user interventions designed to directly neutralize the top risk vectors.
            """
            with st.spinner("Gemini is analyzing the SHAP force plot drivers..."):
                st.write(ask_gemini(prompt))
