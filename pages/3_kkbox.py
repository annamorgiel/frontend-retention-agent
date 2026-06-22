import streamlit as st
import requests
from src.gemini_client import ask_gemini

st.set_page_config(page_title="API 2: KKBox Streaming", layout="wide", initial_sidebar_state="collapsed")

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
        default="⚡ API 2 Predictor", label_visibility="collapsed"
    )

if page_selected == "🏠 Home Portal": st.switch_page("app.py")
elif page_selected == "📊 API 1 Predictor": st.switch_page("pages/2_log_reg.py")

st.markdown("### ⚡ API 2: Sequential Transaction Engine")

inputs_are_open = "kkbox_prediction_result" not in st.session_state

with st.expander("🎵 Configure KKBox Subscriber Metrics", expanded=inputs_are_open):
    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        city = st.number_input("City Code", value=1)
        gender_filled = st.selectbox("Gender", ["Female", "Male", "Unknown"])
        bd_clean = st.number_input("Age", value=28.0)
        bd_was_invalid = st.selectbox("Age Invalid?", [0, 1])
        registered_via = st.number_input("Reg Method ID", value=9)
        tenure_days = st.number_input("Tenure (Days)", value=365.0)

    with col2:
        n_transactions = st.number_input("Total Txns", value=12.0)
        n_cancels_before_cutoff = st.number_input("Cancels Before Cutoff", value=0.0)
        days_since_last_txn = st.number_input("Days Since Last Txn", value=15.0)
        latest_payment_method_id = st.number_input("Latest Pay Method ID", value=41.0)
        n_unique_payment_methods = st.number_input("Unique Pay Methods", value=1.0)

    with col3:
        mean_actual_paid = st.number_input("Mean Paid ($)", value=149.0)
        sum_actual_paid = st.number_input("Sum Paid ($)", value=1788.0)
        mean_list_price = st.number_input("Mean List Price ($)", value=149.0)
        mean_plan_days = st.number_input("Mean Plan Days", value=30.0)
        mean_auto_renew = st.slider("Auto-Renew Ratio", 0.0, 1.0, 1.0)
        discount_ratio = st.number_input("Discount Ratio", value=0.0)
        days_until_expiry_at_cutoff = st.number_input("Days to Expiry", value=15.0)

    # Button moved INSIDE the expander
    run_prediction = st.button("🚀 Run KKBox Prediction", use_container_width=True, type="primary")

if run_prediction:
    payload = { "city": int(city), "bd_clean": float(bd_clean), "bd_was_invalid": int(bd_was_invalid), "gender_filled": gender_filled, "registered_via": int(registered_via), "tenure_days": float(tenure_days), "n_transactions": float(n_transactions), "n_cancels_before_cutoff": float(n_cancels_before_cutoff), "mean_actual_paid": float(mean_actual_paid), "sum_actual_paid": float(sum_actual_paid), "mean_list_price": float(mean_list_price), "mean_plan_days": float(mean_plan_days), "mean_auto_renew": float(mean_auto_renew), "n_unique_payment_methods": float(n_unique_payment_methods), "discount_ratio": float(discount_ratio), "days_since_last_txn": float(days_since_last_txn), "days_until_expiry_at_cutoff": float(days_until_expiry_at_cutoff), "latest_payment_method_id": float(latest_payment_method_id) }
    with st.spinner("Analyzing..."):
        try:
            response = requests.get("https://retention-agent-651418512573.europe-west1.run.app/predict_kkbox", params=payload)
            if response.status_code == 200:
                st.session_state.kkbox_prediction_result = response.json()
                st.session_state.kkbox_last_payload = payload
                st.rerun()
        except requests.exceptions.ConnectionError: st.error("❌ Connection Failed.")

if "kkbox_prediction_result" in st.session_state:
    if st.button("🔄 Reset Profile"):
        st.session_state.pop("kkbox_prediction_result", None)
        st.rerun()

    out_col1, out_col2 = st.columns([1, 2], gap="large")
    with out_col1:
        st.markdown("##### 📋 API Output")
        st.json(st.session_state.kkbox_prediction_result)
    with out_col2:
        if st.button("✨ Ask Gemini", use_container_width=True):
            prompt = f"Expert retention analyst for streaming. Data: {st.session_state.kkbox_last_payload} Result: {st.session_state.kkbox_prediction_result}. Provide summary and 3 strategies."
            with st.spinner("Calculating..."): st.write(ask_gemini(prompt))
