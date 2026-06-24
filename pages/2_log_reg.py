import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from src.gemini_client import ask_gemini

# --- CONFIGURATION & CONSTANTS ---
st.set_page_config(page_title="API 1: Behavioral Predictor", layout="wide", initial_sidebar_state="collapsed")

BASE_URL = "https://retention-agent-api-306889378080.europe-west1.run.app"

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

# --- CSS (ALIGNED WITH APP.PY) ---
st.markdown(
    """
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"], [data-testid="stHeader"] { display: none !important; }

        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(15px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        /* Restored to match app.py native wide layout */
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

# --- NAVIGATION (RESTORED ALIGNMENT) ---
nav_col, _ = st.columns([3, 1])
with nav_col:
    page_selected = st.segmented_control(
        label="Navigation Menu",
        options=["🏠 Home Portal", "👤 API 1: Behavioral Predictor", "💳 API 2: Transactional Predictor"],
        default="👤 API 1: Behavioral Predictor",
        label_visibility="collapsed",
        key="nav_p2"
    )
if page_selected == "🏠 Home Portal": st.switch_page("app.py")
elif page_selected == "💳 API 2: Transactional Predictor": st.switch_page("pages/3_kkbox.py")

st.markdown("<h3 style='color: #111827; margin-bottom: 0; margin-top: 10px;'>API 1: Behavioral Predictor</h3>", unsafe_allow_html=True)
st.markdown("<div class='muted-text' style='margin-bottom: 15px;'>Logistic Regression Model with SHAP Explanations</div>", unsafe_allow_html=True)

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

with st.expander("Configure Behavioral Metrics", expanded=inputs_are_open):
    btn_col1, btn_col2, _ = st.columns([1, 1, 4])
    with btn_col1: st.button("✨ Auto-Fill Mock Data", on_click=load_mock_api1, use_container_width=True)
    with btn_col2: st.button("🗑️ Reset Fields", on_click=reset_api1, use_container_width=True)

    st.markdown("<div class='req-header'>Mandatory Parameters</div>", unsafe_allow_html=True)

    grp_col1, grp_col2 = st.columns([1, 2], gap="large")
    with grp_col1:
        st.markdown("<div class='req-category'>Subscription & Account</div>", unsafe_allow_html=True)
        subscription_type = st.selectbox("Subscription Type", ["Basic", "Standard", "Premium"], index=None, key="p2_subtype")
        monthly_charges = st.number_input("Monthly Charges ($)", value=None, step=0.01, key="p2_monthly_charges")

    with grp_col2:
        st.markdown("<div class='req-category'>Engagement & Usage</div>", unsafe_allow_html=True)
        e_col1, e_col2 = st.columns(2, gap="small")
        with e_col1:
            avg_duration = st.number_input("Avg View Duration (Mins)", value=None, step=1, key="p2_duration")
            downloads = st.number_input("Monthly Downloads", value=None, step=1, key="p2_downloads")
        with e_col2:
            viewing_hours = st.number_input("Viewing Hours / Week", value=None, step=0.5, key="p2_hours")
            genre_preference = st.selectbox("Preferred Genre", ["Action", "Comedy", "Drama", "Sci-Fi", "Thriller"], index=None, key="p2_genre")

    with st.expander("Optional Parameters (Pre-filled via Imputation)", expanded=False):
        opt_col1, opt_col2, opt_col3, opt_col4 = st.columns(4, gap="small")
        with opt_col1:
            st.markdown("<div class='req-category'>Account History</div>", unsafe_allow_html=True)
            account_age = st.number_input("Account Age (Months)", value=12, step=1, key="p2_age")
            total_charges = st.number_input("Total Charges ($) (Auto)", value=None, step=0.01, key="p2_total_charges")
            support_tickets = st.number_input("Monthly Support Tickets", value=0, step=1, key="p2_tickets")
        with opt_col2:
            st.markdown("<div class='req-category'>Content Prefs</div>", unsafe_allow_html=True)
            content_type = st.selectbox("Content Type", ["Movies", "TV Shows", "Both"], index=2, key="p2_content")
            user_rating = st.number_input("User Rating (1-5)", min_value=1.0, max_value=5.0, value=3.5, step=0.1, key="p2_rating")
            watchlist_size = st.number_input("Watchlist Size", value=0, step=1, key="p2_watchlist")
        with opt_col3:
            st.markdown("<div class='req-category'>Billing & Access</div>", unsafe_allow_html=True)
            payment_method = st.selectbox("Payment Method", ["Mailed check", "Electronic check", "Credit card", "Bank transfer"], index=1, key="p2_payment")
            paperless_billing = st.selectbox("Paperless Billing", ["No", "Yes"], index=1, key="p2_paperless")
            device_registered = st.selectbox("Registered Device", ["Computer", "Mobile", "Tablet", "TV"], index=3, key="p2_device")
        with opt_col4:
            st.markdown("<div class='req-category'>User Settings</div>", unsafe_allow_html=True)
            multi_device = st.selectbox("Multi-Device Access", ["Yes", "No"], index=1, key="p2_multidevice")
            gender = st.selectbox("Gender", ["Female", "Male"], index=0, key="p2_gender")
            parental_control = st.selectbox("Parental Controls", ["No", "Yes"], index=0, key="p2_parental")
            subtitles = st.selectbox("Subtitles Enabled", ["Yes", "No"], index=0, key="p2_subtitles")

    st.markdown("<br>", unsafe_allow_html=True)
    run_prediction = st.button("🚀 Launch Model & SHAP Explainer", use_container_width=True, type="primary")

# --- EXECUTION LOGIC ---
if run_prediction:
    mandatory_inputs = {
        "Subscription Type": subscription_type, "Monthly Charges": monthly_charges,
        "Avg Duration": avg_duration, "Downloads": downloads,
        "Viewing Hours": viewing_hours, "Genre": genre_preference
    }

    if any(v is None for v in mandatory_inputs.values()):
        st.warning("Please fill in all Mandatory fields or click '✨ Auto-Fill Mock Data' before running.")
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

        with st.spinner("Executing model pipeline and extracting SHAP log-odds..."):
            try:
                # Timeout updated to 30
                res_pred = requests.get(f"{BASE_URL}/predict", params=payload, timeout=30)
                if res_pred.status_code == 200:
                    st.session_state.prediction_result = res_pred.json()
                    st.session_state.last_payload = payload
                    try:
                        # Timeouts updated to 30
                        res_expl = requests.get(f"{BASE_URL}/explain", params=payload, timeout=30)
                        if res_expl.status_code != 200:
                            res_expl = requests.post(f"{BASE_URL}/explain", json=payload, timeout=30)
                        st.session_state.explanation_result = res_expl.json() if res_expl.status_code == 200 else {"Notice": f"SHAP HTTP {res_expl.status_code}."}
                    except requests.exceptions.RequestException:
                        st.session_state.explanation_result = {"Notice": "SHAP API unreachable."}
                    st.rerun()
                else:
                    st.error(f"Predict Failed: {res_pred.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"Cloud error: {e}")

# --- ELEGANT RESULTS DASHBOARD ---
if "prediction_result" in st.session_state:
    st.markdown("---")

    # Header Control Row
    dash_header_col1, dash_header_col2 = st.columns([5, 1])
    with dash_header_col1:
        st.markdown("<h4 style='color: #111827; margin-bottom: 10px;'>Analysis Dashboard</h4>", unsafe_allow_html=True)
    with dash_header_col2:
        if st.button("🔄 New Analysis", use_container_width=True):
            st.session_state.pop("prediction_result", None)
            st.session_state.pop("explanation_result", None)
            st.rerun()

    # [1, 1.2] Ratio creates a solid balance while giving text room
    out_col1, out_col2 = st.columns([1, 1.2], gap="large")

    prob = st.session_state.prediction_result.get("churn_probability", 0)
    retention_prob = 1.0 - prob
    raw_shap = st.session_state.explanation_result

    with out_col1:
        # Wrap the Prediction & Impact in a distinct container card
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

            # 5 Radio Button Selector
            h_col1, h_col2 = st.columns([1, 2])
            with h_col1:
                st.markdown("<div style='font-size:0.9em; font-weight:600; padding-top:8px;'>SHAP Features:</div>", unsafe_allow_html=True)
            with h_col2:
                shap_limit = st.radio("Features:", options=["1", "2", "3", "4", "5"], index=4, horizontal=True, label_visibility="collapsed")

            limit = int(shap_limit)
            drivers_list = raw_shap.get("top_drivers", [])[:limit] if isinstance(raw_shap, dict) else []
            gemini_context = []

            if drivers_list:
                df_shap = pd.DataFrame(drivers_list)
                # Map friendly names and apply bold HTML tags directly for Plotly rendering
                df_shap["feature"] = df_shap["feature"].str.replace(r"num__|cat__", "", regex=True).map(lambda x: API1_FEATURE_MAP.get(x, x))
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
                # Increase padding logic to guarantee large text values aren't cropped
                padding = max(abs(x_min), abs(x_max)) * 0.30 if max(abs(x_min), abs(x_max)) > 0 else 0.15

                # High-Contrast Layout Updates
                fig.update_traces(
                    textposition="outside",
                    textfont=dict(size=14, color="#000000"), # Enforcing pure black for maximum contrast
                    cliponaxis=False # Prevents text from being clipped by the edge of the plot
                )
                fig.update_layout(
                    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, title="", font=dict(size=12, color="#000000")),
                    margin=dict(l=0, r=0, t=30, b=0), height=max(150, len(df_shap) * 55),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#000000", size=13), # Global font set to pure black
                    yaxis=dict(tickfont=dict(size=13, color="#000000")), # Enforced Y-axis styling
                    xaxis=dict(
                        showgrid=True, gridcolor="#D1D5DB",
                        zerolinecolor="#000000", zerolinewidth=2, # Stronger zero line for visual grounding
                        range=[x_min - padding, x_max + padding],
                        title_font=dict(size=12, color="#374151")
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No SHAP drivers available to display.")

    with out_col2:
        # Wrap the AI Strategy Agent in a distinct container card
        with st.container(border=True):
            st.markdown("<div class='req-header' style='margin-top:0;'>AI Strategy Agent</div>", unsafe_allow_html=True)
            st.markdown("<div class='muted-text' style='margin-bottom:15px;'>Generate personalized retention interventions directly targeting the vectors identified by the SHAP log-odds.</div>", unsafe_allow_html=True)

            if st.button("🧠 Ask Gemini for SHAP-Guided Strategies", use_container_width=True, type="primary"):
                prompt = f"""
                You are an expert customer retention data scientist specializing in behavioral profiling.
                Profile: {st.session_state.last_payload}
                Churn Probability: {prob * 100:.2f}%
                SHAP Influences (Top {shap_limit}):
                {chr(10).join(gemini_context)}

                Tasks:
                1. Write an executive churn prevention insights based on SHAP features and provided churn predictions. Explicitly reference the top {shap_limit} features from the SHAP context to explain why the model made this specific prediction. When using more than 3 features for analysis, make sure to reduce length while keeping the actionable feedback.
                2. Provide highly specific user interventions designed to directly neutralize the risk vectors identified by the SHAP values.
                """
                with st.spinner("Gemini is analyzing the SHAP force plot drivers..."):
                    # The response itself gets its own inner visual boundary
                    with st.container(border=True):
                        st.write(ask_gemini(prompt))
