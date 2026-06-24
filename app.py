import streamlit as st

st.set_page_config(page_title="Customer Retention Agent", layout="wide", initial_sidebar_state="collapsed")

# MACBOOK OPTIMIZED CSS & COMPACT LIST STYLES
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

        /* New Custom UI Classes for Expanders */
        .req-header { color: #111827 !important; font-size: 1.1em; font-weight: 700; margin-bottom: 0.2rem; }
        .req-category { color: #6B7280; font-size: 0.75em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 0.7rem; margin-bottom: 0.2rem; }
        .req-list { font-size: 0.85em; line-height: 1.5; color: #374151; }
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

# Sleeker Title Area
st.markdown("### Customer Retention Analytics Agent - asses churn risk and identify prevention measures")

# 🧭 THE ROUTING WIZARD
with st.container(border=True):
    data_type = st.radio(
        "**Which data do you primarily have?**",
        [
            "🔍 Unsure / Show me all options",
            "👤 Customer engagement behavioral data (Demographics, content preferences, support tickets)",
            "💳 Subscription and payment transactional data (Transaction logs, auto-renews, plan lengths)"
        ],
        index=None
    )

st.markdown("<br>", unsafe_allow_html=True)

# Smart State Routing Logic
is_unsure = data_type is not None and "Unsure" in data_type
is_api1 = data_type is not None and "engagement" in data_type
is_api2 = data_type is not None and "Subscription" in data_type

show_api1_details = is_unsure or is_api1
show_api2_details = is_unsure or is_api2

col1, col2 = st.columns(2, gap="large")

with col1:
    if is_api1: st.success("✨ **Best Match: API 1: Behavioral Predictor**")

    with st.container(border=True):
        st.markdown("**API 1: Behavioral Predictor with local SHAP values for explainability**\n\n<span style='font-size:0.9em; color:#888'>Logistic Regression model trained on a synthetic dataset</span>", unsafe_allow_html=True)

        with st.expander("View Data Requirements", expanded=show_api1_details):
            f_col1, f_col2 = st.columns(2)

            with f_col1:
                st.markdown("""
                <div class='req-header'>Mandatory Inputs</div>

                <div class='req-category'>Subscription & Account</div>
                <div class='req-list'>
                    - Monthly Charges<br>
                    - Subscription Type
                </div>

                <div class='req-category'>Engagement & Usage</div>
                <div class='req-list'>
                    - Avg Viewing Duration<br>
                    - Monthly Downloads<br>
                    - Viewing Hours / Week<br>
                    - Preferred Genre
                </div>
                """, unsafe_allow_html=True)

            with f_col2:
                st.markdown("""
                <div class='req-header'>Optional Inputs</div>

                <div class='req-category'>Auto-Imputed if missing</div>
                <div class='req-list'>
                    - Account Age<br>
                    - User Rating<br>
                    - Support Tickets<br>
                    - Watchlist Size<br>
                    - Device / Multi-Device<br>
                    - Payment / Billing Prefs<br>
                    - Demographics
                </div>
                """, unsafe_allow_html=True)

        if st.button("Launch API 1: Behavioral Predictor", type="primary", use_container_width=True, key="launch_1"):
            st.switch_page("pages/2_log_reg.py")

with col2:
    if is_api2: st.success("✨ **Best Match: API 2: Transactional Predictor**")

    with st.container(border=True):
        st.markdown("**API 2: Transactional Predictor with local SHAP values for explainability**\n\n<span style='font-size:0.9em; color:#888'>KKBox model trained on a real-world dataset (Sequential Engine)</span>", unsafe_allow_html=True)

        with st.expander("View Data Requirements", expanded=show_api2_details):
            f_col3, f_col4 = st.columns(2)

            with f_col3:
                st.markdown("""
                <div class='req-header'>Mandatory Inputs</div>

                <div class='req-category'>Customer Activity</div>
                <div class='req-list'>
                    - Days Since Joining<br>
                    - Total Transactions<br>
                    - Days Since Last Transaction
                </div>

                <div class='req-category'>Financials</div>
                <div class='req-list'>
                    - Total Amount Spent<br>
                    - Avg Subscription Price<br>
                    - Auto-Renewal Rate<br>
                    - Days Until Expiry
                </div>
                """, unsafe_allow_html=True)

            with f_col4:
                st.markdown("""
                <div class='req-header'>Optional Inputs</div>

                <div class='req-category'>Auto-Imputed if missing</div>
                <div class='req-list'>
                    - Avg Subscription Length<br>
                    - Discount Share<br>
                    - Gender<br>
                    - Age<br>
                    - Avg Paid per Trans. (Computed)
                </div>
                """, unsafe_allow_html=True)

        if st.button("Launch API 2: Transactional Predictor", type="primary", use_container_width=True, key="launch_2"):
            st.switch_page("pages/3_kkbox.py")

# Glossary
with st.expander("ML Metric Glossary", expanded=False):
    g_col1, g_col2 = st.columns(2, gap="large")
    with g_col1:
        st.markdown("""
        #### Global Discrimination Metrics
        * **ROC-AUC (or AUC):** "If I pick a random churner and a random non-churner, how often does the model rank the churner higher?"
        * **PR-AUC (Average Precision):** Total area under the Precision-Recall curve. Excellent for imbalanced datasets.
        * **Recall @ top 10%:** If we target the top 10% highest-risk users, what fraction of true churners do we catch?
        """)
    with g_col2:
        st.markdown("""
        #### Threshold-Dependent Metrics
        * **Precision:** Of all flagged high-risk churners, what fraction actually left?
        * **Recall (Sensitivity):** Of all actual churners, what fraction did the model successfully flag?
        * **F1-Score:** The harmonic mean balancing both Precision and Recall.
        """)
