import streamlit as st
import requests

# 1. Force the layout to span the screen comfortably
st.set_page_config(
    page_title="Customer Churn Predictor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.header("📊 Customer Churn Risk Prediction")
st.write("Enter metrics side-by-side to generate an instant, scrolling-free risk profile.")

# 2. Main 2-Column Split for a compact MacBook view
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

    # Sub-columns to tighten up binary options tightly on laptop screens
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        device_registered = st.selectbox("Device Registered", ["Computer", "Mobile", "Tablet", "TV"])
        parental_control = st.selectbox("Parental Control", ["No", "Yes"])
    with sub_col2:
        multi_device = st.selectbox("Multi-Device Access", ["Yes", "No"])
        subtitles = st.selectbox("Subtitles Enabled", ["Yes", "No"])

# 3. Action Section
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
