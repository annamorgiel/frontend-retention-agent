import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from src.gemini_client import ask_gemini

# --- CONFIGURATION & CONSTANTS ---
st.set_page_config(page_title="Behavioral predictor engine", layout="wide", initial_sidebar_state="collapsed")

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

API1_FEATURE_MAP = {
    "AccountAge": "Account Age (Months)", "MonthlyCharges": "Monthly Charges ($)",
    "TotalCharges": "Total Charges ($)", "SubscriptionType": "Subscription Type",
    "PaymentMethod": "Payment Method", "PaperlessBilling": "Paperless Billing",
    "ContentType": "Content Type", "MultiDeviceAccess": "Multi-Device Access",
    "DeviceRegistered": "Registered Device", "ViewingHoursPerWeek": "Viewing Hours per Week",
    "AverageViewingDuration": "Avg Viewing Duration (Mins)", "ContentDownloadsPerMonth": "Monthly Downloads",
    "GenrePreference": "Preferred Genre", "UserRating": "User Rating",
    "SupportTicketsPerMonth": "Monthly Support Tickets", "Gender": "Gender",
    "WatchlistSize": "Watchlist Size", "ParentalControl": "Parental Controls Enabled",
    "SubtitlesEnabled": "Subtitles Enabled"
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
        default="👤 Behavioral predictor engine",
        label_visibility="collapsed",
        key="nav_p2"
    )
if page_selected == "🏠 Home Portal": st.switch_page("app.py")
elif page_selected == "💳 Transactional predictor engine": st.switch_page("pages/3_kkbox.py")

# --- HEADER ---
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.markdown(f"<h3 style='margin-top:10px;'>👤 Behavioral Predictor Engine</h3>", unsafe_allow_html=True)
with header_col2:
    # Small helper tag
    st.markdown(f"<div style='background:{COLORS['retention_teal']}; color:white; padding:5px 12px; border-radius:20px; font-size:0.7em; font-weight:bold; text-align:center; margin-top:15px;'>ACTIVE AGENT</div>", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
def load_mock_api1():
    st.session_state.update({
        "p2_monthly_charges": 149.00, "p2_subtype": "Premium", "p2_duration": 120,
        "p2_downloads": 10, "p2_hours": 20.0, "p2_genre": "Action", "p2_age": 12,
        "p2_rating": 4.5, "p2_tickets": 0, "p2_watchlist": 15, "p2_total_charges": 1788.00,
        "p2_content": "Both", "p2_payment": "Electronic check", "p2_paperless": "Yes",
        "p2_device": "Mobile", "p2_multidevice": "Yes", "p2_gender": "Male",
        "p2_parental": "No", "p2_subtitles": "Yes"
    })

def reset_api1():
    st.session_state.update({
        "p2_monthly_charges": None, "p2_subtype": None, "p2_duration": None, "p2_downloads": None,
        "p2_hours": None, "p2_genre": None, "p2_age": 12, "p2_rating": 3.5, "p2_tickets": 0,
        "p2_watchlist": 0, "p2_total_charges": None, "p2_content": "Both", "p2_payment": "Electronic check",
        "p2_paperless": "Yes", "p2_device": "TV", "p2_multidevice": "No", "p2_gender": "Female",
        "p2_parental": "No", "p2_subtitles": "Yes"
    })
    st.session_state.pop("prediction_result", None)
    st.session_state.pop("explanation_result", None)

# --- DATA ENTRY UI ---
inputs_are_open = "prediction_result" not in st.session_state

with st.expander("📝 Data Configuration: Input customer features", expanded=inputs_are_open):
    # Wider Buttons logic
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
    with btn_col1: st.button("✨ Auto-Fill Mock", on_click=load_mock_api1, use_container_width=True)
    with btn_col2: st.button("🗑️ Reset Fields", on_click=reset_api1, use_container_width=True)

    st.markdown("<div class='req-header'>Mandatory Parameters</div>", unsafe_allow_html=True)

    grp_col1, grp_col2 = st.columns([1, 2], gap="large")
    with grp_col1:
        st.markdown("<div class='req-category'>Subscription</div>", unsafe_allow_html=True)
        subscription_type = st.selectbox("Subscription Type", ["Basic", "Standard", "Premium"], index=None, key="p2_subtype")
        monthly_charges = st.number_input("Monthly Charges ($)", value=None, step=0.01, key="p2_monthly_charges")

    with grp_col2:
        st.markdown("<div class='req-category'>Engagement Metrics</div>", unsafe_allow_html=True)
        e_col1, e_col2 = st.columns(2, gap="small")
        with e_col1:
            avg_duration = st.number_input("Avg View Duration (Mins)", value=None, step=1, key="p2_duration")
            downloads = st.number_input("Monthly Downloads", value=None, step=1, key="p2_downloads")
        with e_col2:
            viewing_hours = st.number_input("Viewing Hours / Week", value=None, step=0.5, key="p2_hours")
            genre_preference = st.selectbox("Preferred Genre", ["Action", "Comedy", "Drama", "Sci-Fi", "Thriller"], index=None, key="p2_genre")

    with st.expander("🛠️ Advanced Settings (Imputation Defaults)", expanded=False):
        opt_col1, opt_col2, opt_col3, opt_col4 = st.columns(4, gap="small")
        with opt_col1:
            st.markdown("<div class='req-category'>History</div>", unsafe_allow_html=True)
            account_age = st.number_input("Account Age (Months)", value=12, step=1, key="p2_age")
            total_charges = st.number_input("Total Charges ($)", value=None, step=0.01, key="p2_total_charges")
            support_tickets = st.number_input("Support Tickets", value=0, step=1, key="p2_tickets")
        with opt_col2:
            st.markdown("<div class='req-category'>Content</div>", unsafe_allow_html=True)
            content_type = st.selectbox("Content Type", ["Movies", "TV Shows", "Both"], index=2, key="p2_content")
            user_rating = st.number_input("User Rating", min_value=1.0, max_value=5.0, value=3.5, step=0.1, key="p2_rating")
            watchlist_size = st.number_input("Watchlist Size", value=0, step=1, key="p2_watchlist")
        with opt_col3:
            st.markdown("<div class='req-category'>Billing</div>", unsafe_allow_html=True)
            payment_method = st.selectbox("Payment Method", ["Mailed check", "Electronic check", "Credit card", "Bank transfer"], index=1, key="p2_payment")
            paperless_billing = st.selectbox("Paperless", ["No", "Yes"], index=1, key="p2_paperless")
            device_registered = st.selectbox("Device", ["Computer", "Mobile", "Tablet", "TV"], index=3, key="p2_device")
        with opt_col4:
            st.markdown("<div class='req-category'>User</div>", unsafe_allow_html=True)
            multi_device = st.selectbox("Multi-Device", ["Yes", "No"], index=1, key="p2_multidevice")
            gender = st.selectbox("Gender", ["Female", "Male"], index=0, key="p2_gender")
            parental_control = st.selectbox("Parental Controls", ["No", "Yes"], index=0, key="p2_parental")
            subtitles = st.selectbox("Subtitles", ["Yes", "No"], index=0, key="p2_subtitles")

    st.markdown("<br>", unsafe_allow_html=True)
    # Primary Action (Coral Color)
    run_prediction = st.button("🚀 Analyze Churn Risk and Drivers", use_container_width=True, type="primary")

# --- EXECUTION LOGIC ---
if run_prediction:
    mandatory_inputs = {
        "Sub": subscription_type, "Charge": monthly_charges,
        "Dur": avg_duration, "Down": downloads,
        "Hrs": viewing_hours, "Gen": genre_preference
    }

    if any(v is None for v in mandatory_inputs.values()):
        st.warning("All mandatory fields must be populated.")
    else:
        computed_total_charges = total_charges or (float(monthly_charges * account_age) if monthly_charges and account_age else 0.0)

        payload = {
            "AccountAge": int(account_age), "MonthlyCharges": float(monthly_charges), "TotalCharges": float(computed_total_charges),
            "SubscriptionType": subscription_type, "PaymentMethod": payment_method, "PaperlessBilling": paperless_billing,
            "ContentType": content_type, "MultiDeviceAccess": multi_device, "DeviceRegistered": device_registered,
            "ViewingHoursPerWeek": float(viewing_hours), "AverageViewingDuration": float(avg_duration),
            "ContentDownloadsPerMonth": int(downloads), "GenrePreference": genre_preference, "UserRating": float(user_rating),
            "SupportTicketsPerMonth": int(support_tickets), "Gender": gender, "WatchlistSize": int(watchlist_size),
            "ParentalControl": parental_control, "SubtitlesEnabled": subtitles
        }

        with st.spinner("Agent running Behavioral Inference..."):
            try:
                res_pred = requests.get(f"{BASE_URL}/predict", params=payload, timeout=30)
                if res_pred.status_code == 200:
                    st.session_state.prediction_result = res_pred.json()
                    st.session_state.last_payload = payload
                    try:
                        res_expl = requests.get(f"{BASE_URL}/explain", params=payload, timeout=30)
                        if res_expl.status_code != 200:
                            res_expl = requests.post(f"{BASE_URL}/explain", json=payload, timeout=30)
                        st.session_state.explanation_result = res_expl.json() if res_expl.status_code == 200 else {"Notice": "SHAP Unavailable"}
                    except:
                        st.session_state.explanation_result = {"Notice": "SHAP Error"}
                    st.rerun()
                else:
                    st.error("API Connection Error")
            except Exception as e:
                st.error(f"Inference Timeout: {e}")

# --- DASHBOARD ---
if "prediction_result" in st.session_state:
    st.markdown("---")

    dash_header_col1, dash_header_col2 = st.columns([5, 1])
    with dash_header_col1:
        st.markdown(f"<h4>📊 Inference Dashboard</h4>", unsafe_allow_html=True)
    with dash_header_col2:
        if st.button("🔄 New Case", use_container_width=True):
            st.session_state.pop("prediction_result", None)
            st.session_state.pop("explanation_result", None)
            st.rerun()

    out_col1, out_col2 = st.columns([1, 1.2], gap="large")

    prob = st.session_state.prediction_result.get("churn_probability", 0)
    retention_prob = 1.0 - prob
    raw_shap = st.session_state.explanation_result

    with out_col1:
        with st.container(border=True):
            st.markdown("<div class='req-header' style='margin-top:0;'>Risk Assessment</div>", unsafe_allow_html=True)

            p_col1, p_col2 = st.columns(2)
            with p_col1:
                # Restored dynamic risk labels and colors
                status_color = "normal" if prob < 0.35 else "off" if prob < 0.70 else "inverse"
                risk_label = "Low Risk" if prob < 0.35 else "Medium Risk" if prob < 0.70 else "High Risk"
                st.metric(label="Churn Risk", value=f"{prob * 100:.2f}%", delta=risk_label, delta_color=status_color)

            with p_col2:
                # Restored dynamic confidence labels and colors
                retention_color = "normal" if retention_prob >= 0.65 else "off" if retention_prob >= 0.30 else "inverse"
                safe_label = "High Confidence" if retention_prob >= 0.65 else "Moderate Confidence" if retention_prob >= 0.30 else "Low Confidence"
                st.metric(label="Retention Score", value=f"{retention_prob * 100:.2f}%", delta=safe_label, delta_color=retention_color)

            st.markdown("<br>", unsafe_allow_html=True)

            # Updated text label
            h_col1, h_col2 = st.columns([1, 2])
            with h_col1:
                st.markdown("<div style='font-size:0.9em; font-weight:600; padding-top:8px;'>Key churn drivers:</div>", unsafe_allow_html=True)
            with h_col2:
                shap_limit = st.radio("Number of top churn-driving features to analyze:", options=["1", "2", "3", "4", "5"], index=4, horizontal=True, label_visibility="collapsed")

            limit = int(shap_limit)
            st.markdown(f"<div class='req-category'>Top {limit} Risk Drivers</div>", unsafe_allow_html=True)

            drivers_list = raw_shap.get("top_drivers", [])[:limit] if isinstance(raw_shap, dict) else []
            gemini_context = []

            if drivers_list:
                df_shap = pd.DataFrame(drivers_list)
                df_shap["feature"] = df_shap["feature"].str.replace(r"num__|cat__", "", regex=True).map(lambda x: API1_FEATURE_MAP.get(x, x))
                df_shap["direction"] = df_shap["shap_value"].apply(lambda x: "Increases Risk" if float(x) > 0 else "Decreases Risk")

                # Format values for display on the chart
                df_shap["text_val"] = df_shap["shap_value"].apply(lambda x: f"+{float(x):.3f}" if float(x) > 0 else f"{float(x):.3f}")

                for _, row in df_shap.iterrows():
                    gemini_context.append(f"{row['feature']}: {row['direction']}")

                # Added text="text_val" to display values on bars
                fig = px.bar(
                    df_shap, x="shap_value", y="feature", orientation='h', color="direction", text="text_val",
                    color_discrete_map={"Increases Risk": COLORS['coral'], "Decreases Risk": COLORS['retention_teal']},
                    labels={"shap_value": "Impact Intensity", "feature": ""}
                )

                # Calculate padding to prevent text cropping
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
                    xaxis=dict(range=[x_min - padding, x_max + padding]) # Apply padding
                )
                st.plotly_chart(fig, use_container_width=True)

    with out_col2:
        with st.container(border=True):
            st.markdown(f"<div class='req-header' style='margin-top:0; border-color:{COLORS['agent_purple']}'>🧠 AI Retention Strategy</div>", unsafe_allow_html=True)

            if st.button("Ask Gemini Agent for Intervention Plan", use_container_width=True, type="primary"):
                prompt = f"""
                Analyze this churn profile: {st.session_state.last_payload}
                Churn Probability: {prob * 100:.2f}%
                Key Risk Drivers (Top {limit}): {', '.join(gemini_context)}
                Provide: 1. Executive Summary 2. Specific Actionable Interventions directly neutralizing the {limit} risk drivers identified.
                """
                with st.spinner("Consulting Strategy Agent..."):
                    with st.container(border=True):
                        st.write(ask_gemini(prompt))
