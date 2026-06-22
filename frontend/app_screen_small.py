import streamlit as st
import requests

# 1. Page Configuration (Must be at the very top)
st.set_page_config(
    page_title="Customer Churn Predictor",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Singular Header Section
st.title("📊 Customer Churn Risk Prediction")
st.write("Fill in the customer metrics below to generate a real-time prediction.")
st.markdown("---")

# 3. Group inputs logically using Expanders (Collapsible Cards)
with st.expander("👤 1. Demographics & Account Details", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("Gender", ["Female", "Male"])
        account_age = st.number_input("Account Age (Months)", min_value=0, value=24)
        subscription_type = st.selectbox("Subscription Type", ["Basic", "Standard", "Premium"])
    with col2:
        payment_method = st.selectbox("Payment Method", ["Mailed check", "Electronic check", "Credit card", "Bank transfer"])
        paperless_billing = st.selectbox("Paperless Billing", ["No", "Yes"])

with st.expander("💰 2. Charges & Support Metrics", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, value=79.99, step=0.01)
        total_charges = st.number_input("Total Charges ($)", min_value=0.0, value=1919.76, step=0.01)
    with col2:
        support_tickets = st.number_input("Support Tickets / Month", min_value=0, value=1)
        user_rating = st.slider("User Rating", min_value=1.0, max_value=5.0, value=4.5, step=0.1)

with st.expander("🎬 3. Usage & Content Preferences", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        content_type = st.selectbox("Content Type", ["Movies", "TV Shows", "Both"])
        genre_preference = st.selectbox("Genre Preference", ["Action", "Comedy", "Drama", "Sci-Fi", "Thriller"])
        viewing_hours = st.number_input("Viewing Hours / Week", min_value=0.0, value=15.5, step=0.5)
        avg_duration = st.number_input("Avg Viewing Duration (Mins)", min_value=0, value=120)
    with col2:
        downloads = st.number_input("Downloads / Month", min_value=0, value=5)
        watchlist_size = st.number_input("Watchlist Size", min_value=0, value=12)
        device_registered = st.selectbox("Device Registered", ["Computer", "Mobile", "Tablet", "TV"])
        multi_device = st.selectbox("Multi-Device Access", ["Yes", "No"])

with st.expander("⚙️ 4. App Settings", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        parental_control = st.selectbox("Parental Control", ["No", "Yes"])
    with col2:
        subtitles = st.selectbox("Subtitles Enabled", ["Yes", "No"])

st.markdown("---")

# 4. Predict Button & Results Execution
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

    with st.spinner("Analyzing subscriber data..."):
        try:
            # Using your production Cloud Run URL
            response = requests.get("https://retention-agent-651418512573.europe-west1.run.app/predict", params=payload)

            if response.status_code == 200:
                result = response.json()
                st.success("### Prediction Successful!")
                st.json(result)
            else:
                st.error(f"❌ API Error: Received status code {response.status_code}")
                try:
                    st.write(response.json())
                except:
                    st.code(response.text)

        except requests.exceptions.ConnectionError:
            st.error("❌ Connection Failed. Make sure your cloud service is live at `https://retention-agent-651418512573.europe-west1.run.app`")
