import streamlit as st
import requests

# 1. Page Configuration (Must remain at the very top)
st.set_page_config(
    page_title="Customer Retention Agent",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "current_page" not in st.session_state:
    st.session_state.current_page = "page_1"

# --- PAGE 1: API / MODEL SELECTION & GLOSSARY ---
if st.session_state.current_page == "page_1":
    st.header("🎯 Customer Retention Analytics Portal")
    st.write("Select the underlying machine learning engine you want to evaluate or review metric definitions below.")

    st.markdown("---")

    # Existing Two-Column Layout for Model Selection
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.subheader("📊 API 1: Full Profile Churn Predictor (XGBoost)")
        st.write("Evaluates user risk profiles using a comprehensive 19-variable matrix.")
        if st.button("Launch Full Profile Predictor", use_container_width=True):
            st.session_state.current_page = "page_2"
            st.rerun()

    with col2:
        st.subheader("⚡ API 2: Streamlined Predictor (WIP)")
        st.write("An upcoming, lightweight model optimized for quick evaluations.")
        st.info("🚧 Backend Integration Pending: API 2 is currently under construction.")
        if st.button("Open Streamlined View (Preview)", use_container_width=True):
            st.session_state.current_page = "page_3"
            st.rerun()

    st.markdown("---")

    # --- NEW: METRIC GLOSSARY SECTION ---
    st.subheader("📖 Machine Learning Metric Glossary")
    st.write("Once we have the modeling results in hand, use this guide to interpret the performance metrics properly:")

    with st.expander("🔍 Click to open Metric Definitions", expanded=True):

        # Grid layout for digestible reading without vertical clutter
        g_col1, g_col2 = st.columns(2, gap="large")

        with g_col1:
            st.markdown("""
            ### 📈 Global Discrimination Metrics

            * **ROC-AUC (or AUC)**
              * **What it means:** *"If I pick a random churner and a random non-churner, how often does the model rank the churner higher?"*
              * **Range:** **0.5** (completely random guessing) to **1.0** (perfect accuracy).
              * **Pro Tip:** It does not depend on your decision threshold.
              * **Caveat:** Can look overly optimistic on highly imbalanced datasets.

            * **PR-AUC (Average Precision)**
              * **What it means:** The total area under the Precision-Recall curve.
              * **Pro Tip:** Much more informative than regular AUC for rare event detection. A perfectly random baseline model here gets a PR-AUC equal to your exact base rate (**~0.06**), *not* 0.5.

            ### 🎯 Budget & Deployment Strategy

            * **Recall @ top 10%**
              * **What it means:** If we sorted all subscribers by their predicted churn risk and targeted only the highest-risk **10%**, what fraction of true churners would we successfully catch?
              * **Business Value:** This maps directly to your retention marketing budget. It answers the critical resource question: *"We can only afford to contact 10% of our customers this month—who exactly should they be?"*
            """)

        with g_col2:
            st.markdown("""
            ### 🎯 Threshold-Dependent Operational Metrics

            * **Precision**
              * **What it means:** Of all the customers the model flagged as high-risk churners, what fraction actually ended up leaving?
              * **Core Question:** *"When the model says a user will churn, is it right?"*

            * **Recall (Sensitivity)**
              * **What it means:** Of all the actual churners hidden in the dataset, what fraction did our model successfully flag?
              * **Core Question:** *"Did we miss any high-value people that we care about saving?"*

            * **F1-Score**
              * **What it means:** The harmonic mean balancing both Precision and Recall into a single evaluation score.
              * **Pro Tip:** It balances the trade-off between the two and changes dynamically depending on where you set your final decision probability threshold.
            """)

# --- PAGE 2: API 1 FULL METRICS VIEW ---
elif st.session_state.current_page == "page_2":
    if st.button("⬅️ Back to Model Selection"):
        st.session_state.current_page = "page_1"
        st.rerun()

    st.header("📊 Customer Churn Risk Prediction (API 1)")
    st.write("Enter metrics side-by-side to generate an instant risk profile.")

    left_main, right_main = st.columns(2, gap="large")

    with left_main:
        st.subheader("👤 Account & Billing Profile")
        gender = st.selectbox("Gender", ["Female", "Male"])
        account_age = st.number_input("Account Age (Months)", min_value=0, value=24)
        subscription_type = st.selectbox("Subscription Type", ["Basic", "Standard", "Premium"])
        payment_method = st.selectbox("Payment Method", ["Mailed check", "Electronic check", "Credit card", "Bank transfer"])
        paperless_billing = st.selectbox("Paperless Billing", ["No", "Yes"])

        st.subheader("💰 Financials & Support")
        monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, value=79.99, step=0.01)
        total_charges = st.number_input("Total Charges ($)", min_value=0.0, value=1919.76, step=0.01)
        support_tickets = st.number_input("Support Tickets / Month", min_value=0, value=1)

    with right_main:
        st.subheader("🎬 Content & Platform Activity")
        content_type = st.selectbox("Content Type", ["Movies", "TV Shows", "Both"])
        genre_preference = st.selectbox("Genre Preference", ["Action", "Comedy", "Drama", "Sci-Fi", "Thriller"])
        viewing_hours = st.number_input("Viewing Hours / Week", min_value=0.0, value=15.5, step=0.5)
        avg_duration = st.number_input("Avg Viewing Duration (Mins)", min_value=0, value=120)
        downloads = st.number_input("Downloads / Month", min_value=0, value=5)
        watchlist_size = st.number_input("Watchlist Size", min_value=0, value=12)

        st.subheader("⚙️ Engagement & Settings")
        user_rating = st.slider("User Rating", min_value=1.0, max_value=5.0, value=4.5, step=0.1)

        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            device_registered = st.selectbox("Device Registered", ["Computer", "Mobile", "Tablet", "TV"])
            parental_control = st.selectbox("Parental Control", ["No", "Yes"])
        with sub_col2:
            multi_device = st.selectbox("Multi-Device Access", ["Yes", "No"])
            subtitles = st.selectbox("Subtitles Enabled", ["Yes", "No"])

    if st.button("🚀 Run Churn Prediction", use_container_width=True):
        payload = {
            "AccountAge": int(account_age),
            "MonthlyCharges": float(monthly_charges),
            "TotalCharges": float(total_charges),
            "SubscriptionType": subscription_type,
            "PaymentMethod": payment_method,
            "PaperlessBilling": paperless_billing,
            "ContentType": content_type,
            "MultiDeviceAccess": multi_device,
            "DeviceRegistered": device_registered,
            "ViewingHoursPerWeek": float(viewing_hours),
            "AverageViewingDuration": float(avg_duration),
            "ContentDownloadsPerMonth": int(downloads),
            "GenrePreference": genre_preference,
            "UserRating": float(user_rating),
            "SupportTicketsPerMonth": int(support_tickets),
            "Gender": gender,
            "WatchlistSize": int(watchlist_size),
            "ParentalControl": parental_control,
            "SubtitlesEnabled": subtitles
        }

        with st.spinner("Analyzing subscriber data via API 1..."):
            try:
                response = requests.get("https://retention-agent-651418512573.europe-west1.run.app/predict", params=payload)
                if response.status_code == 200:
                    result = response.json()
                    st.success("### Prediction Successful!")
                    st.json(result)
                else:
                    st.error(f"❌ API Error: Received status code {response.status_code}")
                    try: st.write(response.json())
                    except: st.code(response.text)
            except requests.exceptions.ConnectionError:
                st.error("❌ Connection Failed. Check your cloud service live endpoint.")


# --- PAGE 3: API 2 STRIPPED FLOW (WIP PREVIEW) ---
elif st.session_state.current_page == "page_3":
    if st.button("⬅️ Back to Model Selection"):
        st.session_state.current_page = "page_1"
        st.rerun()

    st.header("⚡ Streamlined Evaluation (API 2 Preview)")
    st.warning("This interface is a placeholder layout. Fields will be active once API 2 endpoints are configured.")

    # Ready to customize as soon as you settle on your secondary pipeline features!
    st.info("💡 Tip: Once API 2 features are finalized, map your inputs here exactly like Page 2.")
