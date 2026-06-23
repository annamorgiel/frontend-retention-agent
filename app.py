import streamlit as st

st.set_page_config(page_title="Customer Retention Agent", layout="wide", initial_sidebar_state="collapsed")

# MACBOOK OPTIMIZED CSS
st.markdown(
    """
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"], [data-testid="stHeader"] {
            display: none !important; visibility: hidden !important;
        }
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(15px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        .block-container {
            padding-top: 1.5rem !important; padding-bottom: 1rem !important;
            animation: fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        div[data-testid="stVerticalBlock"] > div { gap: 0.5rem !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# Top Navigation Bar
nav_col, _ = st.columns([3, 1])
with nav_col:
    page_selected = st.segmented_control(
        label="Navigation Menu",
        options=["🏠 Home Portal", "👤 API 1: Behavioral Predictor", "💳 API 2: Transactional Predictor"],
        default="🏠 Home Portal", label_visibility="collapsed", key="nav_home"
    )

if page_selected == "👤 API 1: Behavioral Predictor": st.switch_page("pages/2_log_reg.py")
elif page_selected == "💳 API 2: Transactional Predictor": st.switch_page("pages/3_kkbox.py")

# Compact Title Area
st.markdown("#### 🎯 Customer Retention Analytics Agent")

# 🧭 THE ROUTING WIZARD
with st.container(border=True):
    data_type = st.radio(
        "**Which data do you primarily have?**",
        [
            "🔍 Unsure / Show me all options",
            "👤 Customer engagement behavioral data (Demographics, content preferences, support tickets)",
            "💳 Subscription and payment transactional data (Transaction logs, auto-renews, plan lengths)"
        ],
        index=None  # 🔥 Starts empty to force user engagement
    )

st.markdown("<br>", unsafe_allow_html=True)

# Smart State Routing Logic
is_unsure = data_type is not None and "Unsure" in data_type
is_api1 = data_type is not None and "engagement" in data_type
is_api2 = data_type is not None and "Subscription" in data_type

# Determine Expander States
show_api1_details = is_unsure or is_api1
show_api2_details = is_unsure or is_api2

col1, col2 = st.columns(2, gap="large")

with col1:
    # Highlight badge only appears if explicitly selected
    if is_api1: st.success("✨ **Best Match: API 1: Behavioral Predictor** 👤")

    with st.container(border=True):
        st.markdown("**👤 API 1: Behavioral Predictor** with Logistic Regression model trained on a synthetic dataset")

        with st.expander("📋 View 19 Required Features", expanded=show_api1_details):
            features_api1 = [
                "Gender", "Account Age", "Subscription Type", "Payment Method",
                "Paperless Billing", "Monthly Charges", "Total Charges", "Support Tickets",
                "Content Type", "Genre", "Viewing Hours", "Avg Duration", "Downloads",
                "Watchlist Size", "User Rating", "Device", "Parental Control", "Multi-Device", "Subtitles"
            ]
            f_col1, f_col2 = st.columns(2)
            half_1 = len(features_api1) // 2 + 1
            with f_col1:
                for f in features_api1[:half_1]: st.markdown(f"<span style='font-size:0.85em'>- {f}</span>", unsafe_allow_html=True)
            with f_col2:
                for f in features_api1[half_1:]: st.markdown(f"<span style='font-size:0.85em'>- {f}</span>", unsafe_allow_html=True)

        # Launch button is now ALWAYS visible
        if st.button("🚀 Launch API 1: Behavioral Predictor Engine 👤", type="primary", use_container_width=True, key="launch_1"):
            st.switch_page("pages/2_log_reg.py")

with col2:
    # Highlight badge only appears if explicitly selected
    if is_api2: st.success("✨ **Best Match: API 2: Transactional Predictor** 💳 ")

    with st.container(border=True):
        st.markdown("**💳 API 2: Transactional Predictor** with KKBox model trained on a non-synthetic dataset Sequential Engine")

        with st.expander("📋 View 18 Required Features", expanded=show_api2_details):
            features_api2 = [
                "City Code", "Cleaned Age", "Age Invalid Flag", "Gender Imputed",
                "Registration Method", "Total Tenure", "Total Transactions", "Cancellations",
                "Mean Actual Paid", "Sum Actual Paid", "Mean List Price", "Mean Plan Duration",
                "Auto-Renew Ratio", "Unique Payment Methods", "Discount Ratio", "Days Since Last Txn",
                "Days Until Expiry", "Latest Payment Method"
            ]
            f_col3, f_col4 = st.columns(2)
            half_2 = len(features_api2) // 2
            with f_col3:
                for f in features_api2[:half_2]: st.markdown(f"<span style='font-size:0.85em'>- {f}</span>", unsafe_allow_html=True)
            with f_col4:
                for f in features_api2[half_2:]: st.markdown(f"<span style='font-size:0.85em'>- {f}</span>", unsafe_allow_html=True)

        # Launch button is now ALWAYS visible
        if st.button("🚀 Launch API 2: Transactional Predictor Engine 💳", type="primary", use_container_width=True, key="launch_2"):
            st.switch_page("pages/3_kkbox.py")

# Glossary
with st.expander("📖 ML Metric Glossary (Click to expand)", expanded=False):
    g_col1, g_col2 = st.columns(2, gap="large")
    with g_col1:
        st.markdown("""
        ### 📈 Global Discrimination Metrics
        * **ROC-AUC (or AUC):** "If I pick a random churner and a random non-churner, how often does the model rank the churner higher?"
        * **PR-AUC (Average Precision):** Total area under the Precision-Recall curve. Excellent for imbalanced datasets.
        * **Recall @ top 10%:** If we target the top 10% highest-risk users, what fraction of true churners do we catch?
        """)
    with g_col2:
        st.markdown("""
        ### 🎯 Threshold-Dependent Metrics
        * **Precision:** Of all flagged high-risk churners, what fraction actually left?
        * **Recall (Sensitivity):** Of all actual churners, what fraction did the model successfully flag?
        * **F1-Score:** The harmonic mean balancing both Precision and Recall.
        """)
