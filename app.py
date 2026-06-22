import streamlit as st
import requests

st.set_page_config(page_title="Customer Retention Agent", layout="wide", initial_sidebar_state="collapsed")

# MACBOOK OPTIMIZED CSS: Hide header completely, ultra-thin padding
st.markdown(
    """
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"], [data-testid="stHeader"] {
            display: none !important; visibility: hidden !important;
        }
        .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
        /* Shrink gap between elements */
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
        options=["🏠 Home Portal", "📊 API 1 Predictor", "⚡ API 2 Predictor"],
        default="🏠 Home Portal", label_visibility="collapsed"
    )

if page_selected == "📊 API 1 Predictor": st.switch_page("pages/2_log_reg.py")
elif page_selected == "⚡ API 2 Predictor": st.switch_page("pages/3_kkbox.py")

# Compact Title Area
st.markdown("### 🎯 Customer Retention Analytics Portal & Operational Engines")
st.caption("Centralized ML engine control hub. Select an engine above to begin.")

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("**📊 API 1: Full Profile Predictor** (Logistic Regression)")
    with st.container(border=True):
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

with col2:
    st.markdown("**⚡ API 2: KKBox Predictor** (Sequential Engine)")
    with st.container(border=True):
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

# Original Detailed Glossary restored inside a space-saving expander
with st.expander("📖 ML Metric Glossary (Click to expand)", expanded=False):
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
