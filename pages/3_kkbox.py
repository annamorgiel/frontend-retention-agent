import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from src.gemini_client import ask_gemini

st.set_page_config(page_title="API 2: Transactional Predictor", layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"], [data-testid="stHeader"] { display: none !important; }
        @keyframes fadeIn { 0% { opacity: 0; transform: translateY(15px); } 100% { opacity: 1; transform: translateY(0); } }
        .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; animation: fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        div[data-testid="stVerticalBlock"] > div { gap: 0.3rem !important; }
        .metric-card { padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True
)

# 🗺️ Translation Dictionary for API 2 Features (From PDF Requirements)
API2_FEATURE_MAP = {
    "tenure_days": "Days Since Joining", "n_transactions": "Total Number of Transactions",
    "days_since_last_txn": "Days Since Last Transaction", "latest_payment_method_id": "Most Recent Payment Method",
    "mean_actual_paid": "Average Amount Paid per Transaction", "sum_actual_paid": "Total Amount Spent ($)",
    "mean_list_price": "Average Subscription Price ($)", "mean_plan_days": "Average Subscription Length (Days)",
    "mean_auto_renew": "Auto-Renewal Rate", "discount_ratio": "Discount Share",
    "days_until_expiry_at_cutoff": "Days Until Subscription Expires", "gender_filled": "Gender",
    "bd_clean": "Age", "city": "City Code", "bd_was_invalid": "Age Invalid Flag",
    "registered_via": "Registration Method", "n_unique_payment_methods": "Unique Payment Methods",
    "n_cancels_before_cutoff": "Cancellations Before Cutoff"
}

nav_col, _ = st.columns([3, 1])
with nav_col:
    page_selected = st.segmented_control(
        label="Nav", options=["🏠 Home Portal", "👤 API 1: Behavioral Predictor", "💳 API 2: Transactional Predictor"],
        default="💳 API 2: Transactional Predictor", label_visibility="collapsed", key="nav_p3"
    )
if page_selected == "🏠 Home Portal": st.switch_page("app.py")
elif page_selected == "👤 API 1: Behavioral Predictor": st.switch_page("pages/2_log_reg.py")

st.markdown("#### 💳 API 2: Transactional Predictor (with SHAP Explanations)")

def load_mock_api2():
    st.session_state.update({
        "p3_tenure": 730.0, "p3_txns": 24.0, "p3_last_txn": 15.0,
        "p3_sum_paid": 3576.0, "p3_list_price": 149.0, "p3_renew": 1.0, "p3_expiry": 15.0,
        "p3_pay_id": 41.0, "p3_plan_days": 30.0, "p3_discount": 0.0,
        "p3_gender": "Male", "p3_age": 28.0, "p3_mean_paid": 149.0
    })

def reset_api2():
    st.session_state.update({
        "p3_tenure": None, "p3_txns": None, "p3_last_txn": None,
        "p3_sum_paid": None, "p3_list_price": None, "p3_renew": None, "p3_expiry": None,
        "p3_pay_id": 41.0, "p3_plan_days": 34.0, "p3_discount": 1.0,
        "p3_gender": "Unknown", "p3_age": 30.0, "p3_mean_paid": None
    })
    st.session_state.pop("kkbox_prediction_result", None)
    st.session_state.pop("kkbox_shap_result", None)

inputs_are_open = "kkbox_prediction_result" not in st.session_state

with st.expander("💳 Configure Transactional Metrics", expanded=inputs_are_open):
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1: st.button("🪄 Auto-Fill Mock Profile", on_click=load_mock_api2, key="p3_mock_btn", use_container_width=True)
    with btn_col2: st.button("🗑️ Reset All Fields", on_click=reset_api2, key="p3_reset_fields_btn", use_container_width=True)
    st.markdown("---")

    st.markdown("##### Mandatory Parameters")
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.markdown("**Customer Activity**")
        tenure_days = st.number_input("Days Since Joining", value=None, step=1.0, key="p3_tenure")
        n_transactions = st.number_input("Total Number of Transactions", value=None, step=1.0, key="p3_txns")
        days_since_last_txn = st.number_input("Days Since Last Transaction", value=None, step=1.0, key="p3_last_txn")
    with col2:
        st.markdown("**Financials**")
        sum_actual_paid = st.number_input("Total Amount Spent ($)", value=None, step=1.0, key="p3_sum_paid")
        mean_list_price = st.number_input("Average Subscription Price ($)", value=None, step=1.0, key="p3_list_price")
        mean_auto_renew = st.number_input("Auto-Renewal Rate", min_value=0.0, max_value=1.0, value=None, step=0.1, key="p3_renew", help="Share of transactions")
        days_until_expiry_at_cutoff = st.number_input("Days Until Subscription Expires", value=None, step=1.0, key="p3_expiry")

    with st.expander("Optional Parameters (Pre-filled)", expanded=False):
        col3, col4 = st.columns(2, gap="medium")
        with col3:
            latest_payment_method_id = st.number_input("Most Recent Payment Method", value=41.0, step=1.0, key="p3_pay_id")
            mean_plan_days = st.number_input("Average Subscription Length (Days)", value=34.0, step=1.0, key="p3_plan_days")
            discount_ratio = st.number_input("Discount Share", value=1.0, step=0.1, key="p3_discount", help="Shows how much discount the user received")
        with col4:
            gender_filled = st.selectbox("Gender", ["Female", "Male", "Unknown"], index=2, key="p3_gender")
            bd_clean = st.number_input("Age", value=30.0, step=1.0, key="p3_age")
            mean_actual_paid = st.number_input("Average Amount Paid per Transaction", value=None, step=1.0, key="p3_mean_paid", help="To be computed automatically if left empty.")

    with st.expander("📖 Feature Explanations Glossary", expanded=False):
            st.markdown("""
            * **Auto-Renewal Rate:** The percentage of the user's historical transactions that were processed via automatic renewal.
            * **Discount Share:** The proportion of the standard subscription price that was discounted for this user.
            * **Average Amount Paid per Transaction:** The typical amount the user actually pays per billing cycle. *(Note: If left blank, the system will automatically calculate this based on their total spend and transaction count).*
            * **Most Recent Payment Method:** An internal system ID representing how the user last paid. *(Defaults to 41, the platform's most common payment method).*
            * **Average Subscription Length (Days):** The typical duration of the user's billing cycle. *(Defaults to 34 days, the platform average).*
            """)

    run_prediction = st.button("🚀 Run Transactional Prediction & SHAP", use_container_width=True, type="primary", key="p3_btn_submit")

if run_prediction:
    mandatory_list = [tenure_days, n_transactions, days_since_last_txn, sum_actual_paid, mean_list_price, mean_auto_renew, days_until_expiry_at_cutoff]
    if any(i is None for i in mandatory_list):
        st.warning("⚠️ Please fill in all Mandatory fields or click 'Auto-Fill Mock Profile' before running.")
    else:
        computed_mean_paid = mean_actual_paid
        if computed_mean_paid is None:
            if n_transactions > 0 and sum_actual_paid is not None:
                computed_mean_paid = sum_actual_paid / n_transactions
            else:
                computed_mean_paid = 148.0

        payload = {
            "city": 1, "bd_was_invalid": 0, "registered_via": 7,
            "n_cancels_before_cutoff": 0, "n_unique_payment_methods": 1,
            "gender_filled": gender_filled, "bd_clean": float(bd_clean),
            "latest_payment_method_id": float(latest_payment_method_id),
            "mean_plan_days": float(mean_plan_days), "discount_ratio": float(discount_ratio),
            "mean_actual_paid": float(computed_mean_paid), "tenure_days": float(tenure_days),
            "n_transactions": float(n_transactions), "days_since_last_txn": float(days_since_last_txn),
            "sum_actual_paid": float(sum_actual_paid), "mean_list_price": float(mean_list_price),
            "mean_auto_renew": float(mean_auto_renew), "days_until_expiry_at_cutoff": float(days_until_expiry_at_cutoff)
        }
        BASE_URL = "https://retention-agent-api-306889378080.europe-west1.run.app"
        with st.spinner("Analyzing transactional profile and fetching SHAP values..."):
            try:
                res_pred = requests.get(f"{BASE_URL}/predict_kkbox", params=payload, timeout=7)
                if res_pred.status_code == 200:
                    st.session_state.kkbox_prediction_result = res_pred.json()
                    st.session_state.kkbox_last_payload = payload
                    try:
                        res_shap = requests.get(f"{BASE_URL}/explain_kkbox", params=payload, timeout=5)
                        if res_shap.status_code != 200: res_shap = requests.post(f"{BASE_URL}/explain_kkbox", json=payload, timeout=5)
                        if res_shap.status_code == 200: st.session_state.kkbox_shap_result = res_shap.json()
                        else: st.session_state.kkbox_shap_result = {"Notice": f"SHAP API returned HTTP {res_shap.status_code}."}
                    except Exception: st.session_state.kkbox_shap_result = {"Notice": "SHAP API was unreachable."}
                    st.rerun()
                else: st.error(f"❌ Predict Failed: {res_pred.status_code}")
            except requests.exceptions.RequestException as e: st.error(f"❌ Cloud error: {e}")

if "kkbox_prediction_result" in st.session_state:
    out_col1, out_col2 = st.columns([1, 2], gap="large")

    prob = st.session_state.kkbox_prediction_result.get("churn_probability", 0)

    with out_col2:
        with st.container(border=True):
            st.markdown("**⚙️ Select number of SHAP features to be analyzed**")
            shap_limit = st.radio("Number of features to display and analyze:", options=["1", "2", "3", "4", "5"], index=4, horizontal=True, key="p3_shap_limit")

        st.markdown("<br>", unsafe_allow_html=True)

        raw_shap = st.session_state.kkbox_shap_result
        limit = int(shap_limit)
        drivers_list = []
        if isinstance(raw_shap, dict) and "top_drivers" in raw_shap:
            drivers_list = raw_shap["top_drivers"][:limit]

        # Translate drivers for Gemini so it understands the friendly names
        gemini_context = []
        for d in drivers_list:
            raw_f = d.get("feature", "").replace("num__", "").replace("cat__", "")
            friendly_f = API2_FEATURE_MAP.get(raw_f, raw_f)
            val = d.get("shap_value", 0)
            impact = "Increases Risk" if val > 0 else "Decreases Risk"
            gemini_context.append(f"{friendly_f}: {impact} ({val:.3f})")

        if st.button("✨ Ask Gemini for SHAP-Guided Strategies", use_container_width=True, key="p3_btn_gemini"):
            prompt = f"""
            You are an expert customer retention data scientist specializing in transactional behavior and subscription platforms.
            Profile: {st.session_state.kkbox_last_payload}
            Churn Probability: {prob}
            SHAP Influences (Top {shap_limit}):
            {chr(10).join(gemini_context)}

            Tasks:
            1. Write an executive summary of SHAP features and provided churn predictions. Explicitly reference the top {shap_limit} features from the SHAP context to explain why the transactional model made this specific prediction. When using more than 3 features for analysis, make sure to reduce length while keeping the actionable feedback.
            2. Provide highly specific user interventions designed to directly neutralize the risk vectors identified by the SHAP values.
            """
            with st.spinner("Gemini is analyzing the SHAP force plot drivers..."): st.write(ask_gemini(prompt))

    with out_col1:
        st.markdown("##### 📋 Prediction Output")
        if prob < 0.35: st.success(f"**✅ Safe (Low Risk)** \nChurn Probability: **{prob*100:.1f}%**")
        elif prob < 0.70: st.warning(f"**⚠️ Warning (Medium Risk)** \nChurn Probability: **{prob*100:.1f}%**")
        else: st.error(f"**🚨 Danger (High Risk)** \nChurn Probability: **{prob*100:.1f}%**")

        st.markdown("##### 🔍 Local SHAP Impact (Log-Odds)")

        if drivers_list:
            for d in drivers_list:
                raw_feat = d.get("feature", "Unknown").replace("num__", "").replace("cat__", "")
                friendly_feat = API2_FEATURE_MAP.get(raw_feat, raw_feat)

                val = d.get("shap_value", 0)
                direction = "increases" if val > 0 else "decreases"

                if direction == "increases":
                    st.markdown(f"<div class='metric-card'><b>{friendly_feat}</b><br>🔴 Increases Risk (+{val:.3f})</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='metric-card'><b>{friendly_feat}</b><br>🟢 Decreases Risk (-{abs(val):.3f})</div>", unsafe_allow_html=True)

            df_shap = pd.DataFrame(drivers_list)
            df_shap["feature"] = df_shap["feature"].str.replace("num__", "").str.replace("cat__", "")
            # Apply translation map to dataframe
            df_shap["feature"] = df_shap["feature"].map(lambda x: API2_FEATURE_MAP.get(x, x))
            df_shap["direction"] = df_shap["shap_value"].apply(lambda x: "increases" if float(x) > 0 else "decreases")
            df_shap['abs_shap'] = df_shap['shap_value'].abs()
            df_shap = df_shap.sort_values(by='abs_shap', ascending=True)

            fig = px.bar(
                df_shap, x="shap_value", y="feature", orientation='h', color="direction",
                color_discrete_map={"increases": "#ff4b4b", "decreases": "#00cc96"},
                labels={"shap_value": "SHAP Impact", "feature": ""}
            )
            fig.update_layout(
                showlegend=False, margin=dict(l=0, r=0, t=10, b=0),
                height=max(200, len(df_shap) * 40), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No SHAP drivers available to display.")
