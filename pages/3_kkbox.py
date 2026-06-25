import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from src.gemini_client import ask_gemini

# --- CONFIGURATION & CONSTANTS ---
st.set_page_config(page_title="Transactional predictor engine", layout="wide", initial_sidebar_state="collapsed")

# --- CSS (ALIGNED WITH PAGE 2) ---
st.markdown(
    """
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"], [data-testid="stHeader"] { display: none !important; }

        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(15px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
            animation: fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        /* Compact spacing */
        div[data-testid="stVerticalBlock"] > div { gap: 0.3rem !important; }
        div[data-testid="stForm"] > div { gap: 0.3rem !important; }

        /* High contrast labels & headers */
        div[data-testid="stInputLabel"] p { font-size: 0.85rem !important; color: #111827 !important; font-weight: 600 !important; }
        .req-header { color: #111827 !important; font-size: 1.15rem; font-weight: 700; margin-top: 0.8rem; margin-bottom: 0.4rem; border-bottom: 1px solid #E5E7EB; padding-bottom: 4px; }
        .req-category { color: #4B5563; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; margin-top: 0.8rem; margin-bottom: 0.4rem; }
        .muted-text { color: #888888; font-size: 0.85em; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }

        /* Tighter styling for the radio buttons */
        div.row-widget.stRadio > div { flex-direction: row; align-items: center; gap: 15px; }
    </style>
    """, unsafe_allow_html=True
)

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

st.markdown("<h3 style='color: #111827; margin-bottom: 0; margin-top: 10px;'>Transactional predictor engine</h3>", unsafe_allow_html=True)

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

with st.expander("Input mandatory and optional data", expanded=inputs_are_open):
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

    with st.expander("Optional Parameters (Pre-filled via Imputation)", expanded=False):
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
    run_prediction = st.button("🚀 Predict churn probability and top churn-driving features", use_container_width=True, type="primary", key="p3_btn_submit")

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
            "latest_payment_method_id": 7.0, # 🔒 Hardcoded Backend Requirement
            "gender_filled": gender_filled, "bd_clean": float(bd_clean),
            "mean_plan_days": float(mean_plan_days), "discount_ratio": float(discount_ratio),
            "mean_actual_paid": float(computed_mean_paid), "tenure_days": float(tenure_days),
            "n_transactions": float(n_transactions), "days_since_last_txn": float(days_since_last_txn),
            "sum_actual_paid": float(sum_actual_paid), "mean_list_price": float(mean_list_price),
            "mean_auto_renew": float(mean_auto_renew), "days_until_expiry_at_cutoff": float(days_until_expiry_at_cutoff)
        }
        BASE_URL = "https://retention-agent-api-306889378080.europe-west1.run.app"
        with st.spinner("Computing churn probability and churn driving features..."):
            try:
                # Timout increased to 30
                res_pred = requests.get(f"{BASE_URL}/predict_kkbox", params=payload, timeout=30)
                if res_pred.status_code == 200:
                    st.session_state.kkbox_prediction_result = res_pred.json()
                    st.session_state.kkbox_last_payload = payload
                    try:
                        # Timeout increased to 30
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
            except requests.exceptions.RequestException as e: st.error(f"Cloud error: {e}. This can happen with too many requests. Try again!")

# --- ELEGANT RESULTS DASHBOARD (ALIGNED WITH PAGE 2) ---
if "kkbox_prediction_result" in st.session_state:
    st.markdown("---")

    # Header Control Row
    dash_header_col1, dash_header_col2 = st.columns([5, 1])
    with dash_header_col1:
        st.markdown("<h4 style='color: #111827; margin-bottom: 10px;'>Analysis Dashboard</h4>", unsafe_allow_html=True)
    with dash_header_col2:
        if st.button("🔄 New Analysis", use_container_width=True, key="p3_new_analysis"):
            st.session_state.pop("kkbox_prediction_result", None)
            st.session_state.pop("kkbox_shap_result", None)
            st.rerun()

    # Layout configured for Gemini reading room consistency
    out_col1, out_col2 = st.columns([1, 1.2], gap="large")

    prob = st.session_state.kkbox_prediction_result.get("churn_probability", 0)
    retention_prob = 1.0 - prob
    raw_shap = st.session_state.kkbox_shap_result

    with out_col1:
        with st.container(border=True):
            st.markdown("<div class='req-header' style='margin-top:0;'>Prediction & Impact</div>", unsafe_allow_html=True)

            p_col1, p_col2 = st.columns(2)
            with p_col1:
                status_color = "normal" if prob < 0.35 else "off" if prob < 0.70 else "inverse"
                risk_label = "Low Risk" if prob < 0.35 else "Medium Risk" if prob < 0.70 else "High Risk"
                st.metric(label="Churn Probability", value=f"{prob * 100:.2f}%", delta=risk_label, delta_color=status_color)

            with p_col2:
                retention_color = "normal" if retention_prob >= 0.65 else "off" if retention_prob >= 0.30 else "inverse"
                safe_label = "High Confidence" if retention_prob >= 0.65 else "Moderate Confidence" if retention_prob >= 0.30 else "Low Confidence"
                st.metric(label="Retention Likelihood", value=f"{retention_prob * 100:.2f}%", delta=safe_label, delta_color=retention_color)

            st.markdown("<br>", unsafe_allow_html=True)

            # High-fidelity Radio Selection
            h_col1, h_col2 = st.columns([1, 2])
            with h_col1:
                st.markdown("<div style='font-size:0.9em; font-weight:600; padding-top:8px;'>SHAP Features:</div>", unsafe_allow_html=True)
            with h_col2:
                shap_limit = st.radio("Number of top churn-driving features to analyze:", options=["1", "2", "3", "4", "5"], index=4, horizontal=True, label_visibility="collapsed", key="p3_shap_limit")

            limit = int(shap_limit)
            drivers_list = raw_shap.get("top_drivers", [])[:limit] if isinstance(raw_shap, dict) else []
            gemini_context = []

            if drivers_list:
                df_shap = pd.DataFrame(drivers_list)
                # Map friendly names and apply bold HTML tags directly for Plotly rendering
                df_shap["feature"] = df_shap["feature"].str.replace(r"num__|cat__", "", regex=True).map(lambda x: API2_FEATURE_MAP.get(x, x))
                df_shap["feature"] = df_shap["feature"].apply(lambda x: f"<b>{x}</b>")

                for _, row in df_shap.iterrows():
                    # Strip the bold tag for Gemini's pure text context
                    clean_name = row['feature'].replace('<b>', '').replace('</b>', '')
                    val = float(row["shap_value"])
                    impact = "Increases Risk" if val > 0 else "Decreases Risk"
                    gemini_context.append(f"{clean_name}: {impact} ({val:.3f})")

                df_shap["direction"] = df_shap["shap_value"].apply(lambda x: "Increases Risk" if float(x) > 0 else "Decreases Risk")

                # Formatting values to pure bolded .3f text
                df_shap["text_val"] = df_shap["shap_value"].apply(lambda x: f"<b>+{float(x):.3f}</b>" if float(x) > 0 else f"<b>{float(x):.3f}</b>")
                df_shap = df_shap.sort_values(by="shap_value", key=abs, ascending=True)

                fig = px.bar(
                    df_shap, x="shap_value", y="feature", orientation='h', color="direction", text="text_val",
                    color_discrete_map={"Increases Risk": "#ef4444", "Decreases Risk": "#10b981"},
                    labels={"shap_value": "<b>Log-Odds Impact</b>", "feature": ""}
                )

                x_min = df_shap['shap_value'].min()
                x_max = df_shap['shap_value'].max()
                padding = max(abs(x_min), abs(x_max)) * 0.30 if max(abs(x_min), abs(x_max)) > 0 else 0.15

                fig.update_traces(
                    textposition="outside",
                    textfont=dict(size=14, color="#000000"),
                    cliponaxis=False
                )
                fig.update_layout(
                    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, title="", font=dict(size=12, color="#000000")),
                    margin=dict(l=0, r=0, t=30, b=0), height=max(150, len(df_shap) * 55),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#000000", size=13),
                    yaxis=dict(tickfont=dict(size=13, color="#000000")),
                    xaxis=dict(
                        showgrid=True, gridcolor="#D1D5DB",
                        zerolinecolor="#000000", zerolinewidth=2,
                        range=[x_min - padding, x_max + padding],
                        title_font=dict(size=12, color="#374151")
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No SHAP drivers available to display.")

    with out_col2:
        with st.container(border=True):
            st.markdown("<div class='req-header' style='margin-top:0;'>AI Strategy Agent</div>", unsafe_allow_html=True)
            st.markdown("<div class='muted-text' style='margin-bottom:15px;'>Generate personalized retention recommendations.</div>", unsafe_allow_html=True)

            if st.button("🧠 Ask Gemini Agent for Intervention Plan based on churn drivers", use_container_width=True, type="primary", key="p3_btn_gemini"):
                prompt = f"""
                You are an expert customer retention data scientist specializing in transactional behavior and subscription platforms.
                Profile: {st.session_state.kkbox_last_payload}
                Churn Probability: {prob * 100:.2f}%
                SHAP Influences (Top {shap_limit}):
                {chr(10).join(gemini_context)}

                Tasks:
                1. Write an executive churn prevention summary based on SHAP features and provided churn predictions. Explicitly reference the top {shap_limit} features from the SHAP context to explain why the model made this specific prediction. When using more than 3 features for analysis, make sure to reduce length while keeping the actionable feedback.
                2. Provide highly specific user interventions designed to directly neutralize the risk vectors identified by the SHAP values.
                """
                with st.spinner("Retention agent is analyzing the key churn drivers...."):
                    with st.container(border=True):
                        st.write(ask_gemini(prompt))
