import streamlit as st

# --- CONFIGURATION ---
st.set_page_config(page_title="Intelligent Customer Retention Agent", layout="wide", initial_sidebar_state="collapsed")

# Color Palette Variables (Aligned with Pages 2 & 3)
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

        button[kind="primary"] {{
            background-color: {COLORS['coral']} !important;
            border: none !important;
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
        .req-list {{ font-size: 0.85em; line-height: 1.6; color: {COLORS['navy_dark']}; font-weight: 500; }}
        .subtitle {{ color: {COLORS['agent_purple']}; font-size: 1.1em; font-weight: 600; margin-bottom: 1.5rem; margin-top: -5px; }}

        /* Tighter styling for the radio buttons */
        div.row-widget.stRadio > div {{ flex-direction: column; gap: 10px; }}
        div[data-testid="stInputLabel"] p {{ font-size: 1rem !important; color: {COLORS['navy_dark']} !important; font-weight: 700 !important; }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- NAVIGATION ---
nav_col, _ = st.columns([3, 1])
with nav_col:
    page_selected = st.segmented_control(
        label="Navigation Menu",
        options=["🏠 Home Portal", "👤 Behavioral predictor engine", "💳 Transactional predictor engine"],
        default="🏠 Home Portal", label_visibility="collapsed", key="nav_home"
    )

if page_selected == "👤 Behavioral predictor engine": st.switch_page("pages/2_log_reg.py")
elif page_selected == "💳 Transactional predictor engine": st.switch_page("pages/3_kkbox.py")

# --- HEADER ---
st.markdown("<h3 style='margin-top:10px;'>🏠 Intelligent Customer Retention Agent</h3>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Assess churn risk and identify prevention measures</div>", unsafe_allow_html=True)

# --- THE ROUTING WIZARD ---
with st.container(border=True):
    data_type = st.radio(
        "Which data do you primarily have?",
        [
            "🔍 Unsure / Show me both options",
            "👤 Behavioral data: demographics, content preferences, preferred genre",
            "💳 Transactional data: payment data, transaction logs, auto-renews, plan lengths"
        ],
        index=None
    )

st.markdown("<br>", unsafe_allow_html=True)

# Smart State Routing Logic
is_unsure = data_type is not None and "Unsure" in data_type
is_api1 = data_type is not None and "Behavioral" in data_type
is_api2 = data_type is not None and "Transactional" in data_type

show_api1_details = is_unsure or is_api1
show_api2_details = is_unsure or is_api2

col1, col2 = st.columns(2, gap="large")

# Behavioral Route
with col1:
    if is_api1: st.success("✨ **Best Match: Behavioral predictor engine**")

    with st.container(border=True):
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
                    - Monthly Downloads Number<br>
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

        if st.button("Launch model: Behavioral predictor", type="primary", use_container_width=True, key="launch_1"):
            st.switch_page("pages/2_log_reg.py")

# Transactional Route
with col2:
    if is_api2: st.success("✨ **Best Match: Transactional predictor engine**")

    with st.container(border=True):
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

        if st.button("Launch model: Transactional predictor", type="primary", use_container_width=True, key="launch_2"):
            st.switch_page("pages/3_kkbox.py")

# --- GLOSSARY ---
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📚 ML Metric Glossary", expanded=False):
    g_col1, g_col2 = st.columns(2, gap="large")
    with g_col1:
        st.markdown(f"""
        <div style='color: {COLORS['navy_dark']};'>
            <h4 style='margin-bottom: 10px;'>Global Discrimination Metrics</h4>
            <ul style='font-size: 0.9em; line-height: 1.6;'>
                <li><b>ROC-AUC (or AUC):</b> "If I pick a random churner and a random non-churner, how often does the model rank the churner higher?"</li>
                <li><b>PR-AUC (Average Precision):</b> Total area under the Precision-Recall curve. Excellent for imbalanced datasets.</li>
                <li><b>Recall @ top 10%:</b> If we target the top 10% highest-risk users, what fraction of true churners do we catch?</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with g_col2:
        st.markdown(f"""
        <div style='color: {COLORS['navy_dark']};'>
            <h4 style='margin-bottom: 10px;'>Threshold-Dependent Metrics</h4>
            <ul style='font-size: 0.9em; line-height: 1.6;'>
                <li><b>Precision:</b> Of all flagged high-risk churners, what fraction actually left?</li>
                <li><b>Recall (Sensitivity):</b> Of all actual churners, what fraction did the model successfully flag?</li>
                <li><b>F1-Score:</b> The harmonic mean balancing both Precision and Recall.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
