import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from src.gemini_client import ask_gemini

# --- CONFIGURATION & CONSTANTS ---
st.set_page_config(page_title="Transactional predictor engine", layout="wide", initial_sidebar_state="collapsed")

BASE_URL = "https://retention-agent-api-306889378080.europe-west1.run.app"

# Color Palette Variables
COLORS = {
    "bg_soft": "#F0F1F4",
    "surface": "#FEFEFE",
    "primary_blue": "#1F72ED",
    "retention_teal": "#06A1A3",
    "navy_dark": "#030330",
    "agent_purple": "#6C3EDD",
    "soft_blue": "#8FB9EF",
    "lavender": "#9973F4",
    "coral": "#FB5754",
    "yellow": "#FAAB14"
}

# 🗺️ Translation Dictionary for API 2 Features
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

# --- ADVANCED CSS ---
st.markdown(
    f"""
    <style>
        /* Global Background & Animations */
        .stApp {{ background-color: {COLORS['bg_soft']}; }}
        [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"], [data-testid="stHeader"] {{ display: none !important; }}

        @keyframes fadeIn {{
            0% {{ opacity: 0; transform: translateY(15px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}

        .block-container {{
            padding: 1.5rem 3rem !important;
            animation: fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }}

        /* Buttons: Force Wide & Palette */
        div.stButton > button {{
            width: 100% !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Specific Button Color Logic */
        button[kind="primary"] {{
            background-color: {COLORS['coral']} !important;
            border: none !important;
        }}

        /* Secondary buttons (Auto-fill/Reset) */
        button[kind="secondary"] {{
            background-color: {COLORS['surface']} !important;
            color: {COLORS['navy_dark']} !important;
            border: 1px solid {COLORS['soft_blue']} !important;
        }}

        /* Card Surfaces */
        div[data-testid="stExpander"], div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: {COLORS['surface']} !important;
            border-radius: 12px !important;
            border: 1px solid {COLORS['soft_blue']} !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        }}

        /* Navigation Styling */
        div[data-testid="stSegmentedControl"] {{
            background-color: {COLORS['surface']};
            border-radius: 10px;
            padding: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}

        /* Typography */
        h3, h4 {{ color: {COLORS['navy_dark']} !important; font-family: 'Inter', sans-serif; }}
        .req-header {{
            color: {COLORS['navy_dark']} !important;
            font-size: 1.15rem;
            font-weight: 700;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
            border-bottom: 2px solid {COLORS['retention_teal']};
            padding-bottom: 4px;
        }}
        .req-category {{ color: {COLORS['lavender']}; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; margin-top: 0.8rem; }}

        /* Metrics Custom Styling */
        [data-testid="stMetricValue"] {{ color: {COLORS['navy_dark']} !important; font-weight: 800 !important; }}
    </style>
    """, unsafe_allow_html=True
)

# --- NAVIGATION ---
nav_col, _ = st.columns([3, 1])
with nav_col:
    page_selected = st.segmented_control(
        label="Navigation Menu",
        options=["🏠 Home Portal", "👤 Behavioral predictor engine", "💳 Transactional predictor engine"],
        default="💳 Transactional predictor engine",
        label_visibility="collapsed",
        key="nav_p3"
    )
if page_selected == "🏠 Home Portal": st.switch_page("app.py")
elif page_selected == "👤 Behavioral predictor engine": st.switch_page("pages/2_log_reg.py")

# --- HEADER ---
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.markdown("<h3 style='margin-top:10px;'>💳 Transactional Predictor Engine</h3>", unsafe_allow_html=True)
with header_col2:
    st.markdown(f"<div style='background:{COLORS['retention_teal']}; color:white; padding:5px 12px; border-radius:20px; font-size:0.7em; font-weight:bold; text-align:center; margin-top:15px;'>ACTIVE AGENT</div>", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
def load_mock_api2():
    st.session_state.update({
        "p3_tenure": 730.0, "p3_txns": 24.0, "p3_last_txn": 15.0,
        "p3_sum_paid": 3576.0, "p3_list_price": 149.0, "p3_renew": 1.0, "p3_expiry": 15.0,
        "p3_plan_days": 30.0, "p3_discount": 0.0,
        "p3_gender": "Male", "p3_age": 28.0, "p3_mean_paid": 149.0
    })

def reset_api2():
    st.session_state.update({
        "p3_tenure": None, "p3_txns": None, "p3_last_txn": None,
        "p3_sum_paid": None, "p3_list_price": None, "p3_renew": None, "p3_expiry": None,
        "p3_plan_days": 34.0, "p3_discount": 1.0,
        "p3_gender": "Unknown", "p3_age": 30.0, "p3_mean_paid": None
    })
    st.session_state.pop("kkbox_prediction_result", None)
    st.session_state.pop("kkbox_shap_result", None)

# --- DATA ENTRY UI ---
inputs_are_open = "kkbox_prediction_result" not in st.session_state

with st.expander("📝 Data Configuration: Input transactional data", expanded=inputs_are_open):
    # Full-width buttons split 50/50
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1: st.button("✨ Auto-Fill Mock Data", on_click=load_mock_api2, key="p3_mock_btn", use_container_width=True)
    with btn_col2: st.button("🗑️ Reset Fields", on_click=reset_api2, key="p3_reset_fields_btn", use_container_width=True)

    st.markdown("<div class='req-header'>Mandatory Parameters</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("<div class='req-category'>Customer Activity</div>", unsafe_allow_html=True)
        tenure_days = st.number_input("Days Since Joining", value=None, step=1.0, key="p3_tenure")
        n_transactions = st.number_input("Total Number of Transactions", value=None, step=1.0, key="p3_txns")
        days_since_last_txn = st.number_input("Days Since Last Transaction", value=None, step=1.0, key="p3_last_txn")
    with col2:
        st.markdown("<div class='req-category'>Financials</div>", unsafe_allow_html=True)
        sum_actual_paid = st.number_input("Total Amount Spent ($)", value=None, step=1.0, key="p3_sum_paid")
        mean_list_price = st.number_input("Average Subscription Price ($)", value=None, step=1.0, key="p3_list_price")
        mean_auto_renew = st.number_input("Auto-Renewal Rate", min_value=0.0, max_value=1.0, value=None, step=0.1, key="p3_renew")
        days_until_expiry_at_cutoff = st.number_input("Days Until Subscription Expires", value=None, step=1.0, key="p3_expiry")

    with st.expander("🛠️ Advanced Settings (Imputation Defaults)", expanded=False):
        col3, col4 = st.columns(2, gap="large")
        with col3:
            mean_plan_days = st.number_input("Average Subscription Length (Days)", value=34.0, step=1.0, key="p3_plan_days")
            discount_ratio = st.number_input("Discount Share", value=1.0, step=0.1, key="p3_discount")
            gender_filled = st.selectbox("Gender", ["Female", "Male", "Unknown"], index=2, key="p3_gender")
        with col4:
            bd_clean = st.number_input("Age", value=30.0, step=1.0, key="p3_age")
            mean_actual_paid = st.number_input("Average Amount Paid per Transaction (Auto-computed if empty)", value=None, step=1.0, key="p3_mean_paid")

    with st.expander("Feature Explanations Glossary", expanded=False):
        st.markdown("""
        * **Auto-Renewal Rate:** The percentage of the user's historical transactions that were processed via automatic renewal.
        * **Discount Share:** The proportion of the standard subscription price that was discounted for this user.
        * **Average Amount Paid per Transaction:** The typical amount the user actually pays per billing cycle. *(Note: If left blank, the system will automatically calculate this based on their total spend and transaction count).*
        * **Average Subscription Length (Days):** The typical duration of the user's billing cycle. *(Defaults to 34 days, the platform average).*
        """)

    st.markdown("<br>", unsafe_allow_html=True)
    run_prediction = st.button("🚀 Analyze Churn Risk and Drivers", use_container_width=True, type="primary", key="p3_btn_submit")

# --- EXECUTION LOGIC ---
if run_prediction:
    mandatory_list = [tenure_days, n_transactions, days_since_last_txn, sum_actual_paid, mean_list_price, mean_auto_renew, days_until_expiry_at_cutoff]
    if any(i is None for i in mandatory_list):
        st.warning("Please fill in all Mandatory fields or click '✨ Auto-Fill Mock Data' before running.")
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
            "latest_payment_method_id": 7.0,
            "gender_filled": gender_filled, "bd_clean": float(bd_clean),
            "mean_plan_days": float(mean_plan_days), "discount_ratio": float(discount_ratio),
            "mean_actual_paid": float(computed_mean_paid), "tenure_days": float(tenure_days),
            "n_transactions": float(n_transactions), "days_since_last_txn": float(days_since_last_txn),
            "sum_actual_paid": float(sum_actual_paid), "mean_list_price": float(mean_list_price),
            "mean_auto_renew": float(mean_auto_renew), "days_until_expiry_at_cutoff": float(days_until_expiry_at_cutoff)
        }
        with st.spinner("Agent running Transactional Inference..."):
            try:
                res_pred = requests.get(f"{BASE_URL}/predict_kkbox", params=payload, timeout=30)
                if res_pred.status_code == 200:
                    st.session_state.kkbox_prediction_result = res_pred.json()
                    st.session_state.kkbox_last_payload = payload
                    try:
                        res_shap = requests.get(f"{BASE_URL}/explain_kkbox", params=payload, timeout=30)
                        if res_shap.status_code != 200:
                            res_shap = requests.post(f"{BASE_URL}/explain_kkbox", json=payload, timeout=30)
                        if res_shap.status_code == 200:
                            st.session_state.kkbox_shap_result = res_shap.json()
                        else:
                            st.session_state.kkbox_shap_result = {"Notice": f"SHAP API returned HTTP {res_shap.status_code}."}
                    except Exception: st.session_state.kkbox_shap_result = {"Notice": "SHAP API was unreachable."}
                    st.rerun()
                else: st.error(f"Predict Failed: {res_pred.status_code}")
            except requests.exceptions.RequestException as e: st.error(f"Cloud error: {e}. Try again!")

# --- DASHBOARD ---
if "kkbox_prediction_result" in st.session_state:
    st.markdown("---")

    dash_header_col1, dash_header_col2 = st.columns([5, 1])
    with dash_header_col1:
        st.markdown("<h4>📊 Inference Dashboard</h4>", unsafe_allow_html=True)
    with dash_header_col2:
        if st.button("🔄 New Case", use_container_width=True, key="p3_new_analysis"):
            st.session_state.pop("kkbox_prediction_result", None)
            st.session_state.pop("kkbox_shap_result", None)
            st.rerun()

    out_col1, out_col2 = st.columns([1, 1.2], gap="large")

    prob = st.session_state.kkbox_prediction_result.get("churn_probability", 0)
    retention_prob = 1.0 - prob
    raw_shap = st.session_state.kkbox_shap_result

    with out_col1:
        with st.container(border=True):
            st.markdown("<div class='req-header' style='margin-top:0;'>Risk Assessment</div>", unsafe_allow_html=True)

            p_col1, p_col2 = st.columns(2)
            with p_col1:
                status_color = "normal" if prob < 0.35 else "off" if prob < 0.70 else "inverse"
                risk_label = "Low Risk" if prob < 0.35 else "Medium Risk" if prob < 0.70 else "High Risk"
                st.metric(label="Churn Risk", value=f"{prob * 100:.2f}%", delta=risk_label, delta_color=status_color)

            with p_col2:
                retention_color = "normal" if retention_prob >= 0.65 else "off" if retention_prob >= 0.30 else "inverse"
                safe_label = "High Confidence" if retention_prob >= 0.65 else "Moderate Confidence" if retention_prob >= 0.30 else "Low Confidence"
                st.metric(label="Retention Score", value=f"{retention_prob * 100:.2f}%", delta=safe_label, delta_color=retention_color)

            st.markdown("<br>", unsafe_allow_html=True)

            h_col1, h_col2 = st.columns([1, 2])
            with h_col1:
                st.markdown("<div style='font-size:0.9em; font-weight:600; padding-top:8px;'>Key churn drivers:</div>", unsafe_allow_html=True)
            with h_col2:
                shap_limit = st.radio("Number of top churn-driving features to analyze:", options=["1", "2", "3", "4", "5"], index=4, horizontal=True, label_visibility="collapsed", key="p3_shap_limit")

            limit = int(shap_limit)
            st.markdown(f"<div class='req-category'>Top {limit} Risk Drivers</div>", unsafe_allow_html=True)

            drivers_list = raw_shap.get("top_drivers", [])[:limit] if isinstance(raw_shap, dict) else []
            gemini_context = []

            if drivers_list:
                df_shap = pd.DataFrame(drivers_list)
                df_shap["feature"] = df_shap["feature"].str.replace(r"num__|cat__", "", regex=True).map(lambda x: API2_FEATURE_MAP.get(x, x))
                df_shap["direction"] = df_shap["shap_value"].apply(lambda x: "Increases Risk" if float(x) > 0 else "Decreases Risk")

                df_shap["text_val"] = df_shap["shap_value"].apply(lambda x: f"+{float(x):.3f}" if float(x) > 0 else f"{float(x):.3f}")

                for _, row in df_shap.iterrows():
                    gemini_context.append(f"{row['feature']}: {row['direction']}")

                fig = px.bar(
                    df_shap, x="shap_value", y="feature", orientation='h', color="direction", text="text_val",
                    color_discrete_map={"Increases Risk": COLORS['coral'], "Decreases Risk": COLORS['retention_teal']},
                    labels={"shap_value": "Impact Intensity", "feature": ""}
                )

                x_min = df_shap['shap_value'].min()
                x_max = df_shap['shap_value'].max()
                padding = max(abs(x_min), abs(x_max)) * 0.30 if max(abs(x_min), abs(x_max)) > 0 else 0.15

                fig.update_traces(
                    textposition="outside",
                    textfont=dict(size=13, color=COLORS['navy_dark']),
                    cliponaxis=False
                )
                fig.update_layout(
                    showlegend=False, margin=dict(l=0, r=0, t=10, b=0), height=250,
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=COLORS['navy_dark']),
                    xaxis=dict(range=[x_min - padding, x_max + padding])
                )
                st.plotly_chart(fig, use_container_width=True)

    with out_col2:
        with st.container(border=True):
            st.markdown(f"<div class='req-header' style='margin-top:0; border-color:{COLORS['agent_purple']}'>🧠 AI Retention Strategy</div>", unsafe_allow_html=True)

            if st.button("Ask Gemini Agent for Intervention Plan", use_container_width=True, type="primary", key="p3_btn_gemini"):
                prompt = f"""
                Analyze this churn profile: {st.session_state.kkbox_last_payload}
                Churn Probability: {prob * 100:.2f}%
                Key Risk Drivers (Top {limit}): {', '.join(gemini_context)}
                Provide: 1. Executive Summary 2. Specific Actionable Interventions directly neutralizing the {limit} risk drivers identified.
                """
                with st.spinner("Consulting Strategy Agent..."):
                    with st.container(border=True):
                        st.write(ask_gemini(prompt))
