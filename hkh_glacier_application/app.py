
from pathlib import Path
import warnings
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
import folium
from folium.plugins import Fullscreen, MiniMap

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
DATA_PATH = PROJECT_ROOT / "processed_data" / "hkh_glacier_mass_change_era5land_hydrological_year_eda.csv"
MODEL_PATH = PROJECT_ROOT / "spatial_cv_outputs" / "hkh_glacier_spatial_cv_selected_model.joblib"

FEATURES = [
    "glacier_area_km2", "hydrological_year", "t2m", "snowc", "sde", "sd",
    "sf", "smlt", "ssr", "str", "ro", "es", "sro", "e", "u10", "v10", "tp"
]
CLASS_NAMES = {0: "Mass gain", 1: "Mass loss", 2: "Near balance"}
# High-contrast, colour-blind-friendlier class palette.
# Avoids the low-visibility yellow used previously for Near balance.
CLASS_COLORS = {
    "Mass loss": "#D55E00",      # vermilion
    "Near balance": "#CC79A7",   # magenta
    "Mass gain": "#0072B2"       # blue
}
MASS_COL = "glacier_mass_change_mwe"
LAT_COL = "target_latitude"
LON_COL = "target_longitude"

st.set_page_config(
    page_title="HKH Glacier Intelligence",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(show_spinner="Loading and preparing the HKH dataset…")
def load_data():
    d = pd.read_csv(DATA_PATH)
    d["mass_change_class"] = np.select(
        [d[MASS_COL] > 0.1, d[MASS_COL] < -0.1],
        ["Mass gain", "Mass loss"],
        default="Near balance"
    )
    return d

@st.cache_resource(show_spinner="Loading trained Gradient Boosting model…")
def load_model():
    return joblib.load(MODEL_PATH)

df = load_data()
model = load_model()

# ----------------------------- visual system -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f5f7fb; }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1600px; }
[data-testid="stSidebar"] { background: #101e2b; }
[data-testid="stSidebar"] * { color: #e7edf4 !important; }
.hero {
  background: linear-gradient(115deg,#102b3b 0%,#174c59 55%,#237b79 100%);
  padding: 30px 34px; border-radius: 20px; color: white; margin-bottom: 22px;
  box-shadow: 0 12px 30px rgba(16,43,59,.14);
}
.hero h1 { font-family: Manrope,sans-serif; font-size: 2.05rem; margin: 0 0 7px 0; color: white; font-weight: 800; }
.hero p { color: #d4e5e8; margin: 0; font-size: 1rem; }
.eyebrow { text-transform: uppercase; letter-spacing: .14em; font-size: .70rem; font-weight: 700; color: #79c9bd; margin-bottom: 8px; }
.kpi {
  background: white; border: 1px solid #e8edf3; border-radius: 15px;
  padding: 17px 18px; min-height: 108px; box-shadow: 0 4px 14px rgba(23,43,77,.035);
}
.kpi-label { color: #526174; font-size: .78rem; font-weight: 600; }
.kpi-value { color: #142c3c; font-family: Manrope,sans-serif; font-size: 1.65rem; font-weight: 800; margin-top: 6px; }
.kpi-note { color: #5f6d7d; font-size: .72rem; margin-top: 2px; }
.section-title { font-family: Manrope,sans-serif; color: #193647; font-weight: 800; font-size: 1.25rem; margin: 18px 0 8px 0; }
.subtle { color: #526174; font-size: .88rem; }
div[data-testid="stMetric"] { background: white; padding: 14px 16px; border: 1px solid #d5dde7; border-radius: 13px; }
div[data-testid="stMetric"] label { color: #526174; }
div[data-testid="stAlert"] { border-radius: 12px; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { background: white; border-radius: 9px 9px 0 0; padding: 10px 18px; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

def hero(kicker, title, description):
    st.markdown(f"""<div class="hero"><div class="eyebrow">{kicker}</div>
    <h1>{title}</h1><p>{description}</p></div>""", unsafe_allow_html=True)

def kpi(label, value, note=""):
    st.markdown(f"""<div class="kpi"><div class="kpi-label">{label}</div>
    <div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>""", unsafe_allow_html=True)

def section(title, subtitle=None):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="subtle">{subtitle}</div>', unsafe_allow_html=True)

def fmt_num(x, digits=2):
    return f"{x:,.{digits}f}"

def add_download(df_to_download, filename, label):
    st.download_button(label, df_to_download.to_csv(index=False).encode("utf-8"),
                       file_name=filename, mime="text/csv")

# Sidebar
with st.sidebar:
    st.markdown("## 🏔️ HKH Glacier")
    st.caption("MASS-CHANGE INTELLIGENCE")
    dark_mode = st.toggle("Dark theme", value=False, key="dark_theme")
    page = st.radio("WORKSPACE", [
        "Overview", "Exploratory analysis", "Geographic explorer",
        "Prediction laboratory", "Model & methodology", "Data catalogue"
    ], label_visibility="visible")
    st.divider()
    st.markdown("**DATA SNAPSHOT**")
    st.caption(f"{len(df):,} observations · {df[[LAT_COL,LON_COL]].drop_duplicates().shape[0]:,} grid locations")
    st.caption(f"Hydrological years {df.hydrological_year.min()}–{df.hydrological_year.max()}")
    st.caption("Copernicus/WGMS mass change + ERA5-Land predictors")
    st.divider()
    st.caption("Research decision-support interface · Not an operational forecast")

# Apply the selected theme without changing the dashboard's layout or content.
plotly_template = "plotly_dark" if dark_mode else "plotly_white"
if dark_mode:
    st.markdown("""
    <style>
    /* Main canvas and readable default text */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background: #101923 !important;
        color: #E8EEF5 !important;
    }
    .block-container { color: #E8EEF5 !important; }
    .stApp, .stApp p, .stApp li, .stApp label, .stApp small,
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stCaptionContainer"] {
        color: #DCE5EF;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .section-title { color: #F2F6FA !important; }
    .subtle, [data-testid="stCaptionContainer"] {
        color: #A9B8C8 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0B1420 !important;
        border-right: 1px solid #263648;
    }
    [data-testid="stSidebar"] * { color: #E5EDF5 !important; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #A9B8C8 !important;
    }

    /* KPI cards and native metric cards */
    .kpi, div[data-testid="stMetric"] {
        background: #1B2A3A !important;
        border: 1px solid #34485D !important;
        box-shadow: 0 5px 18px rgba(0,0,0,.18) !important;
    }
    .kpi-label, div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #B8C7D6 !important;
    }
    .kpi-value, div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #F4F7FB !important;
    }
    .kpi-note { color: #A9B8C8 !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: #1B2A3A !important;
        color: #C8D4E0 !important;
        border: 1px solid #34485D !important;
        border-bottom: 0 !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #26394D !important;
        color: #FFFFFF !important;
    }
    .stTabs [aria-selected="true"] {
        background: #29445B !important;
        color: #FFFFFF !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { background: #55B6A8 !important; }

    /* Text inputs, number inputs, dropdowns and multi-selects */
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div,
    [data-baseweb="select"] > div,
    [data-testid="stDateInput"] input,
    [data-testid="stTimeInput"] input {
        background: #1B2A3A !important;
        color: #F0F4F8 !important;
        border-color: #52677D !important;
    }
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea,
    [data-baseweb="select"] input {
        color: #F0F4F8 !important;
        -webkit-text-fill-color: #F0F4F8 !important;
        caret-color: #FFFFFF !important;
    }
    [data-baseweb="input"] input::placeholder,
    [data-baseweb="textarea"] textarea::placeholder {
        color: #A9B8C8 !important;
        -webkit-text-fill-color: #A9B8C8 !important;
    }
    [data-baseweb="select"] svg { fill: #DCE5EF !important; }
    [data-baseweb="popover"], [data-baseweb="menu"],
    [role="listbox"], [role="option"] {
        background: #1B2A3A !important;
        color: #E8EEF5 !important;
    }
    [role="option"]:hover, [aria-selected="true"][role="option"] {
        background: #304A62 !important;
        color: #FFFFFF !important;
    }

    /* Buttons and interactive controls */
    .stButton > button, .stDownloadButton > button,
    [data-testid="stFormSubmitButton"] > button {
        background: #245A66 !important;
        color: #FFFFFF !important;
        border: 1px solid #4C8790 !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover {
        background: #317783 !important;
        color: #FFFFFF !important;
        border-color: #75B8B8 !important;
    }
    [data-testid="stCheckbox"] label, [data-testid="stRadio"] label,
    [data-testid="stToggle"] label, [data-testid="stSlider"] label {
        color: #E1E9F1 !important;
    }
    [data-testid="stSlider"] [role="slider"] {
        background: #67C5B5 !important;
        border-color: #67C5B5 !important;
    }

    /* Expanders, alerts and separators */
    [data-testid="stExpander"] {
        background: #182636 !important;
        border: 1px solid #34485D !important;
        border-radius: 10px !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary span {
        color: #E8EEF5 !important;
    }
    [data-testid="stAlert"] {
        background: #1B2A3A !important;
        color: #E8EEF5 !important;
        border: 1px solid #3A5066 !important;
    }
    hr { border-color: #34485D !important; }

    /* Dataframes and tables */
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        background: #182636 !important;
        color: #E8EEF5 !important;
        border: 1px solid #34485D !important;
    }
    [data-testid="stDataFrame"] [role="grid"],
    [data-testid="stDataFrame"] [role="gridcell"],
    [data-testid="stDataFrame"] [role="columnheader"],
    [data-testid="stTable"] table,
    [data-testid="stTable"] th,
    [data-testid="stTable"] td {
        background-color: #182636 !important;
        color: #E8EEF5 !important;
        border-color: #34485D !important;
    }
    [data-testid="stDataFrame"] [role="columnheader"] {
        background-color: #24384B !important;
        color: #F2F6FA !important;
    }
    [data-testid="stDataFrame"] [role="gridcell"]:hover {
        background-color: #29445B !important;
    }

    /* Code blocks and inline code */
    .stApp code, .stApp pre {
        background: #182636 !important;
        color: #E5EDF5 !important;
        border-color: #34485D !important;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    /* Keep the light theme readable when Streamlit's inherited theme changes. */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background: #f5f7fb !important;
        color: #172b3a !important;
    }
    .stApp p, .stApp li, .stApp label,
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stCaptionContainer"] {
        color: #26384a;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .section-title {
        color: #193647 !important;
    }
    .hero h1, .hero h1 span, .hero h1 a, .hero p {
        color: #ffffff !important;
    }
    .subtle, [data-testid="stCaptionContainer"] {
        color: #526174 !important;
    }

    /* Native cards and tabs */
    .kpi, div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #d5dde7 !important;
        box-shadow: 0 5px 18px rgba(23,43,77,.07) !important;
    }
    .kpi-label, div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #526174 !important;
    }
    .kpi-value, div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #142c3c !important;
    }
    .kpi-note { color: #5f6d7d !important; }
    .stTabs [data-baseweb="tab"] {
        background: #ffffff !important;
        color: #26384a !important;
        border: 1px solid #c8d2de !important;
        border-bottom: 0 !important;
    }
    .stTabs [data-baseweb="tab"]:hover,
    .stTabs [aria-selected="true"] {
        background: #e8f2f1 !important;
        color: #123f4a !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { background: #168b83 !important; }

    /* Inputs and menu popovers */
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div,
    [data-baseweb="select"] > div,
    [data-testid="stDateInput"] input,
    [data-testid="stTimeInput"] input {
        background: #ffffff !important;
        color: #172b3a !important;
        border-color: #9aaabd !important;
    }
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea,
    [data-baseweb="select"] input {
        color: #172b3a !important;
        -webkit-text-fill-color: #172b3a !important;
        caret-color: #123f4a !important;
    }
    [data-baseweb="input"] input::placeholder,
    [data-baseweb="textarea"] textarea::placeholder {
        color: #667588 !important;
        -webkit-text-fill-color: #667588 !important;
    }
    [data-baseweb="select"] svg { fill: #405366 !important; }
    [data-baseweb="popover"], [data-baseweb="menu"],
    [role="listbox"], [role="option"] {
        background: #ffffff !important;
        color: #172b3a !important;
    }
    [role="option"]:hover, [aria-selected="true"][role="option"] {
        background: #e8f2f1 !important;
        color: #123f4a !important;
    }

    /* Buttons, feedback, and expandable content */
    .stButton > button, .stDownloadButton > button,
    [data-testid="stFormSubmitButton"] > button {
        background: #166b68 !important;
        color: #ffffff !important;
        border: 1px solid #0f5653 !important;
    }
    .stButton > button *,
    .stDownloadButton > button *,
    [data-testid="stFormSubmitButton"] > button * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover {
        background: #0f5653 !important;
        color: #ffffff !important;
        border-color: #0b4542 !important;
    }
    [data-testid="stCheckbox"] label, [data-testid="stRadio"] label,
    [data-testid="stToggle"] label, [data-testid="stSlider"] label {
        color: #26384a !important;
    }
    [data-testid="stSlider"] [role="slider"] {
        background: #168b83 !important;
        border-color: #168b83 !important;
    }
    [data-testid="stExpander"] {
        background: #ffffff !important;
        border: 1px solid #c8d2de !important;
        border-radius: 10px !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary span {
        color: #26384a !important;
    }
    [data-testid="stAlert"] {
        background: #f8fbfd !important;
        color: #26384a !important;
        border: 1px solid #b8c7d6 !important;
    }
    hr { border-color: #c8d2de !important; }

    /* Tables need explicit foreground and header colors in light mode. */
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        background: #ffffff !important;
        color: #172b3a !important;
        border: 1px solid #c8d2de !important;
    }
    [data-testid="stDataFrame"] [role="grid"],
    [data-testid="stDataFrame"] [role="gridcell"],
    [data-testid="stDataFrame"] [role="columnheader"],
    [data-testid="stTable"] table,
    [data-testid="stTable"] th,
    [data-testid="stTable"] td {
        background-color: #ffffff !important;
        color: #172b3a !important;
        border-color: #d5dde7 !important;
    }
    [data-testid="stDataFrame"] [role="columnheader"] {
        background-color: #e8eef4 !important;
        color: #193647 !important;
    }
    [data-testid="stDataFrame"] [role="gridcell"]:hover {
        background-color: #edf6f5 !important;
    }
    .stApp code, .stApp pre {
        background: #eef2f6 !important;
        color: #26384a !important;
        border-color: #c8d2de !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------------------- overview -----------------------------
if page == "Overview":
    hero("HINDU KUSH HIMALAYA · RESEARCH DASHBOARD",
         "Glacier Mass-Change Intelligence",
         "Explore observed gridded mass change, investigate climate relationships, and classify mass-change conditions with the selected spatial-CV model.")
    nloc = df[[LAT_COL,LON_COL]].drop_duplicates().shape[0]
    mean_mb = df[MASS_COL].mean()
    gain_pct = (df.mass_change_class == "Mass gain").mean()*100
    loss_pct = (df.mass_change_class == "Mass loss").mean()*100
    c = st.columns(4)
    with c[0]: kpi("OBSERVATIONS", f"{len(df):,}", "Grid-cell × hydrological-year records")
    with c[1]: kpi("GRID LOCATIONS", f"{nloc:,}", "Unique spatial coordinates")
    with c[2]: kpi("MEAN MASS CHANGE", f"{mean_mb:.3f}", "m water equivalent")
    with c[3]: kpi("MASS-LOSS RECORDS", f"{loss_pct:.1f}%", f"{gain_pct:.1f}% mass gain")
    section("The research landscape", "A compact view of the supplied data and the model's validated evaluation summary.")
    left, right = st.columns([1.45,1])
    with left:
        annual = df.groupby("hydrological_year")[MASS_COL].agg(["mean","median"]).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=annual.hydrological_year,y=annual["mean"],name="Annual mean",mode="lines+markers",
                                 line=dict(color="#168b83",width=3)))
        fig.add_trace(go.Scatter(x=annual.hydrological_year,y=annual["median"],name="Annual median",mode="lines",
                                 line=dict(color="#e1a447",width=2,dash="dot")))
        fig.add_hline(y=0,line_dash="dash",line_color="#9aa7b3")
        fig.update_layout(title="Observed mass-change trend by hydrological year",height=340,
                          yaxis_title="Mass change (m w.e.)",xaxis_title="Hydrological year",
                          template=plotly_template,legend=dict(orientation="h",y=1.12))
        st.plotly_chart(fig,use_container_width=True)
    with right:
        counts = df.mass_change_class.value_counts().reindex(["Mass loss","Mass gain","Near balance"]).fillna(0).reset_index()
        counts.columns=["Class","Records"]
        fig = px.pie(counts,names="Class",values="Records",hole=.62,
                     color="Class",color_discrete_map=CLASS_COLORS)
        fig.update_layout(title="Mass-change class distribution",height=340,template=plotly_template,
                          legend=dict(orientation="h",y=-.12))
        fig.update_traces(textposition="inside",textinfo="percent")
        st.plotly_chart(fig,use_container_width=True)
    section("Selected model · spatial out-of-fold evaluation")
    metrics = [
        ("Gradient Boosting","68.39%","62.97%","60.37%","0.8373"),
        ("Random Forest","64.76%","53.82%","52.94%","0.7654"),
        ("SVM (RBF)","52.92%","47.47%","44.71%","0.6796"),
        ("Logistic Regression","51.19%","43.68%","41.80%","0.6526")
    ]
    st.dataframe(pd.DataFrame(metrics,columns=["Classifier","Accuracy","Balanced accuracy","Macro F1","Macro OvR ROC-AUC"]),
                 hide_index=True,use_container_width=True)
    st.info("Evaluation values are transcribed from the supplied supervised-learning notebook. The same spatial folds were used for tuning and reporting; these are not an independent nested-CV estimate or a future-year forecasting score.")
    st.markdown("**Interpretation:** mass-loss records dominate the dataset. Near-balance classification is the most difficult class, so overall accuracy alone should not be used to judge model usefulness.")

# ----------------------------- EDA -----------------------------
elif page == "Exploratory analysis":
    hero("DATA UNDERSTANDING", "Exploratory & statistical analysis",
         "Inspect distributions, temporal patterns, feature relationships, uncertainty, and data completeness.")
    tab1,tab2,tab3,tab4 = st.tabs(["Distributions","Temporal patterns","Relationships","Statistical profile"])
    with tab1:
        col1,col2=st.columns(2)
        with col1:
            fig=px.histogram(
                df, x=MASS_COL, color="mass_change_class", nbins=60,
                color_discrete_map=CLASS_COLORS,
                category_orders={"mass_change_class": ["Mass loss", "Near balance", "Mass gain"]},
                title="Distribution of observed mass change"
            )
            fig.update_layout(template=plotly_template,height=370,xaxis_title="m w.e.",yaxis_title="Records")
            st.plotly_chart(fig,use_container_width=True)
        with col2:
            fig=px.box(df,x="mass_change_class",y=MASS_COL,color="mass_change_class",
                       color_discrete_map=CLASS_COLORS,title="Mass-change spread by class",points=False)
            fig.update_layout(template=plotly_template,height=370,showlegend=False)
            st.plotly_chart(fig,use_container_width=True)
        selected_feature=st.selectbox("Inspect a predictor distribution",FEATURES,index=2,
                                      format_func=lambda x: x.replace("_"," ").title())
        fig=px.histogram(
            df, x=selected_feature, nbins=50, color="mass_change_class",
            color_discrete_map=CLASS_COLORS,
            category_orders={"mass_change_class": ["Mass loss", "Near balance", "Mass gain"]},
            barmode="overlay", opacity=.58,
            title=f"Distribution of {selected_feature}"
        )
        # Light outlines help preserve class separation where distributions overlap.
        fig.update_traces(marker_line_width=0.45, marker_line_color="rgba(255,255,255,0.85)")
        fig.update_layout(
            template=plotly_template, height=380,
            legend_title_text="Mass-change class",
            xaxis_title=selected_feature,
            yaxis_title="Record count"
        )
        st.plotly_chart(fig,use_container_width=True)
    with tab2:
        annual=df.groupby("hydrological_year").agg(
            mean_mass_change=(MASS_COL,"mean"),median_mass_change=(MASS_COL,"median"),
            records=(MASS_COL,"size"),mean_uncertainty=("uncertainty_mwe","mean")).reset_index()
        fig=px.line(annual,x="hydrological_year",y=["mean_mass_change","median_mass_change"],
                    markers=True,title="Annual mean and median mass change")
        fig.add_hline(y=0,line_dash="dash",line_color="gray")
        fig.update_layout(template=plotly_template,height=390,yaxis_title="m w.e.")
        st.plotly_chart(fig,use_container_width=True)
        proportions=pd.crosstab(df.hydrological_year,df.mass_change_class,normalize="index").reset_index()
        p=proportions.melt(id_vars="hydrological_year",var_name="Class",value_name="Share")
        fig=px.area(p,x="hydrological_year",y="Share",color="Class",color_discrete_map=CLASS_COLORS,
                    title="Annual composition of mass-change classes")
        fig.update_layout(template=plotly_template,height=390,yaxis_tickformat=".0%")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(annual.round(4),hide_index=True,use_container_width=True)
    with tab3:
        corr=df[FEATURES+[MASS_COL]].corr(numeric_only=True)
        fig=px.imshow(corr,text_auto=".2f",aspect="auto",color_continuous_scale="RdBu_r",
                      zmin=-1,zmax=1,title="Pearson correlation matrix")
        fig.update_layout(template=plotly_template,height=720)
        st.plotly_chart(fig,use_container_width=True)
        xvar=st.selectbox("X-axis feature",FEATURES,index=2)
        yvar=st.selectbox("Y-axis feature",FEATURES,index=5)
        sample=df.sample(min(5000,len(df)),random_state=42)
        fig=px.scatter(sample,x=xvar,y=yvar,color="mass_change_class",
                       color_discrete_map=CLASS_COLORS,opacity=.55,
                       hover_data=[LAT_COL,LON_COL,"hydrological_year",MASS_COL],
                       title=f"{xvar} vs {yvar} (sample up to 5,000 records)")
        fig.update_layout(template=plotly_template,height=430)
        st.plotly_chart(fig,use_container_width=True)
    with tab4:
        st.markdown("**Numeric feature summary**")
        st.dataframe(df[FEATURES+[MASS_COL,"uncertainty_mwe"]].describe().T.round(4),
                     use_container_width=True)
        quality=pd.DataFrame({
            "Missing values":df.isna().sum(),
            "Missing (%)":(df.isna().mean()*100).round(3),
            "Unique values":df.nunique()
        }).sort_values("Missing values",ascending=False)
        st.markdown("**Data completeness**")
        st.dataframe(quality,use_container_width=True)
        st.markdown("**Uncertainty profile**")
        u=df["uncertainty_mwe"].dropna()
        a,b,c=st.columns(3)
        a.metric("Mean uncertainty",f"{u.mean():.3f} m w.e.")
        b.metric("Median uncertainty",f"{u.median():.3f} m w.e.")
        c.metric("95th percentile",f"{u.quantile(.95):.3f} m w.e.")
        fig=px.histogram(df,x="uncertainty_mwe",nbins=50,title="Reported mass-change uncertainty")
        fig.update_layout(template=plotly_template,height=330)
        st.plotly_chart(fig,use_container_width=True)

# ----------------------------- map -----------------------------
elif page == "Geographic explorer":
    hero("SPATIAL INTELLIGENCE", "HKH geographic explorer",
         "Explore the supplied glacier grid records on an interactive geographic basemap. Coordinates are used for mapping, not as model predictors.")
    years=sorted(df.hydrological_year.unique())
    f1,f2,f3=st.columns([1,1,1.2])
    with f1: year=st.selectbox("Hydrological year",["All years"]+years,index=0)
    with f2: cls=st.selectbox("Mass-change class",["All classes","Mass loss","Mass gain","Near balance"])
    with f3: metric=st.selectbox("Map colour represents",["Observed mass change (m w.e.)","Mass-change class","Uncertainty (m w.e.)"])
    md=df.copy()
    if year!="All years": md=md[md.hydrological_year==year]
    if cls!="All classes": md=md[md.mass_change_class==cls]
    # For all-years view, show location-level mean; for a selected year, show individual records.
    if year=="All years":
        md=md.groupby([LAT_COL,LON_COL],as_index=False).agg(
            glacier_mass_change_mwe=(MASS_COL,"mean"),
            uncertainty_mwe=("uncertainty_mwe","mean"),
            glacier_area_km2=("glacier_area_km2","mean"),
            mass_change_class=("mass_change_class",lambda s:s.mode().iloc[0]),
            hydrological_year=("hydrological_year","max"))
    if len(md)>6000:
        md=md.sample(6000,random_state=42)
        st.caption("Map is sampled to 6,000 points for browser performance; summary charts and data remain based on the full filtered selection.")
    center=[float(df[LAT_COL].mean()),float(df[LON_COL].mean())]
    m=folium.Map(location=center,zoom_start=4,tiles="OpenStreetMap",control_scale=True)
    Fullscreen(position="topright").add_to(m)
    MiniMap(toggle_display=True).add_to(m)



    if metric == "Observed mass change (m w.e.)":

        # Get valid mass-change values
        mass_values = pd.to_numeric(
            md[MASS_COL], errors="coerce"
        ).dropna()

        if mass_values.empty:
            st.info("No valid mass-change records available.")

        else:
            # Symmetric colour range around zero
            scale = max(
                abs(float(mass_values.quantile(0.02))),
                abs(float(mass_values.quantile(0.98))),
                0.001
            )

            # IMPORTANT: Always sorted thresholds
            thresholds = [-scale, 0.0, scale]

            cmap = __import__("branca").colormap.LinearColormap(
                colors=[
                    "blue",
                    "white",
                    "red"
                ],
                index=thresholds,
                vmin=-scale,
                vmax=scale
            )

            cmap.caption = "Observed mass change (m w.e.)"
            cmap.add_to(m)

            for _, r in md.iterrows():

                val = pd.to_numeric(
                    pd.Series([r[MASS_COL]]),
                    errors="coerce"
                ).iloc[0]

                if pd.isna(val):
                    continue

                marker_color = cmap(
                    float(np.clip(val, -scale, scale))
                )

                folium.CircleMarker(
                    location=[r[LAT_COL], r[LON_COL]],
                    radius=5,
                    color="#263238",
                    weight=0.8,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.95,
                    tooltip=(
                        f"Latitude: {r[LAT_COL]:.2f}°N<br>"
                        f"Longitude: {r[LON_COL]:.2f}°E<br>"
                        f"Mass change: {val:.3f} m w.e.<br>"
                        f"Hydrological year: {r.hydrological_year}"
                    )
                ).add_to(m)
    
    
    elif metric=="Mass-change class":
        for _,r in md.iterrows():
            color=CLASS_COLORS.get(r.mass_change_class,"#888888")
            folium.CircleMarker(
                [r[LAT_COL],r[LON_COL]],
                radius=4,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=.8,
                weight=.5,
                tooltip=f"{r.mass_change_class} · {r[LAT_COL]:.2f}, {r[LON_COL]:.2f}"
            ).add_to(m)

    else:
        lo,hi=float(md.uncertainty_mwe.min()),float(md.uncertainty_mwe.max())
        cmap=__import__("branca").colormap.LinearColormap(
            ["#d9f0e7","#1b806e"],
            vmin=lo,
            vmax=max(hi,lo+.001)
        )
        cmap.caption="Uncertainty (m w.e.)"
        cmap.add_to(m)
        for _,r in md.iterrows():
            val=float(r.uncertainty_mwe)
            folium.CircleMarker(
                [r[LAT_COL],r[LON_COL]],
                radius=4,
                color=cmap(val),
                fill=True,
                fill_color=cmap(val),
                fill_opacity=.8,
                weight=.5,
                tooltip=f"Uncertainty {val:.3f} m w.e. · {r[LAT_COL]:.2f}, {r[LON_COL]:.2f}"
            ).add_to(m)

    if md.empty:
        st.info(
            "No records found for the selected year and mass-change class. "
            "Please select another class or hydrological year."
        )
    
    st_folium(m,use_container_width=True,height=610,returned_objects=[])
    st.caption(f"Showing {len(md):,} mapped grid records. The source grid spans {df[LAT_COL].min():.2f}–{df[LAT_COL].max():.2f}°N and {df[LON_COL].min():.2f}–{df[LON_COL].max():.2f}°E.")
    section("Filtered spatial records")
    st.dataframe(md[[LAT_COL,LON_COL,"hydrological_year",MASS_COL,"mass_change_class","uncertainty_mwe","glacier_area_km2"]].head(2000),
                 use_container_width=True,hide_index=True)
    add_download(md,"hkh_filtered_spatial_records.csv","Download filtered map records")

# ----------------------------- prediction -----------------------------
elif page == "Prediction laboratory":
    hero("MODEL INFERENCE", "Prediction laboratory",
         "Run the trained Gradient Boosting classifier using either historical records or manually supplied feature values.")
    st.warning("Scientific scope: the model uses full hydrological-year climate aggregates and hydrological year itself. This is retrospective condition classification, not a forecast available before that hydrological year ends.")
    mode=st.radio("Choose input workflow",["Historical dataset selection","Manual feature entry"],horizontal=True)
    historical_row=None
    if mode=="Historical dataset selection":
        st.markdown("**1 · Choose a historical record**")
        a,b=st.columns(2)
        with a:
            yr=st.selectbox("Hydrological year",sorted(df.hydrological_year.unique(),reverse=True))
        location_df = (
            df.loc[df.hydrological_year == yr, [LAT_COL, LON_COL]]
            .drop_duplicates()
            .sort_values([LAT_COL, LON_COL])
        )
        # Materialize coordinates as a list of (latitude, longitude) tuples.
        # Streamlit's selectbox format_func receives each option; passing a
        # DataFrame iterator directly can result in scalar float options.
        location_options = [
            (float(row[LAT_COL]), float(row[LON_COL]))
            for _, row in location_df.iterrows()
        ]
        with b:
            selected = st.selectbox(
                "Grid location (latitude, longitude)",
                options=location_options,
                format_func=lambda xy: f"{xy[0]:.2f}°N, {xy[1]:.2f}°E"
            )
        historical_row=df[(df.hydrological_year==yr)&(df[LAT_COL]==selected[0])&(df[LON_COL]==selected[1])].iloc[0]
        st.caption(f"Selected location: {selected[0]:.2f}°N, {selected[1]:.2f}°E · HY {yr}")
        with st.expander("Inspect / edit the 17 model inputs",expanded=True):
            vals={}
            cols=st.columns(3)
            for i,feat in enumerate(FEATURES):
                with cols[i%3]:
                    vals[feat]=st.number_input(feat.replace("_"," ").title(),
                        value=float(historical_row[feat]),format="%.6f",key=f"hist_{feat}")
        lat=float(selected[0]); lon=float(selected[1])
    else:
        st.markdown("**1 · Enter geographic context and model features**")
        a,b=st.columns(2)
        with a: lat=st.number_input("Latitude (°N)",min_value=-90.0,max_value=90.0,value=float(df[LAT_COL].median()),format="%.4f")
        with b: lon=st.number_input("Longitude (°E)",min_value=-180.0,max_value=180.0,value=float(df[LON_COL].median()),format="%.4f")
        st.caption("Latitude and longitude are for map context only. They are not passed to the classifier.")
        med=df[FEATURES].median(numeric_only=True)
        with st.expander("Model feature values (17 predictors)",expanded=True):
            vals={}
            cols=st.columns(3)
            for i,feat in enumerate(FEATURES):
                with cols[i%3]:
                    lo=float(df[feat].quantile(.001)); hi=float(df[feat].quantile(.999))
                    vals[feat]=st.number_input(feat.replace("_"," ").title(),
                        value=float(med[feat]),format="%.6f",key=f"manual_{feat}")
        historical_row=None
    st.markdown("**2 · Classify the supplied conditions**")
    if st.button("Run mass-change classification",type="primary",use_container_width=True):
        x=pd.DataFrame([[vals[f] for f in FEATURES]],columns=FEATURES)
        pred=int(model.predict(x)[0])
        probs=model.predict_proba(x)[0]
        pred_name=CLASS_NAMES.get(pred,str(pred))
        st.session_state["last_prediction"]={"class":pred_name,"probabilities":probs.tolist(),"lat":lat,"lon":lon,"values":vals}
        st.session_state["last_historical"]=None if historical_row is None else {
            "actual":float(historical_row[MASS_COL]),"actual_class":str(historical_row.mass_change_class),
            "year":int(historical_row.hydrological_year)}
    result=st.session_state.get("last_prediction")
    if result:
        st.divider()
        st.markdown("**3 · Prediction result**")
        a,b=st.columns([1,1.3])
        with a:
            st.markdown(f"""<div class="kpi"><div class="kpi-label">MODEL-PREDICTED CLASS</div>
            <div class="kpi-value" style="color:{CLASS_COLORS[result['class']]}">{result['class']}</div>
            <div class="kpi-note">Gradient Boosting · 17 predictors</div></div>""",unsafe_allow_html=True)
            st.metric("Location context",f"{result['lat']:.2f}°N, {result['lon']:.2f}°E")
        with b:
            probdf=pd.DataFrame({"Class":[CLASS_NAMES[i] for i in range(3)],"Probability":result["probabilities"]})
            fig=px.bar(probdf,x="Class",y="Probability",color="Class",text=probdf["Probability"].map(lambda x:f"{x:.1%}"),
                       color_discrete_map=CLASS_COLORS,title="Predicted class probabilities")
            fig.update_layout(template=plotly_template,height=300,showlegend=False,yaxis_tickformat=".0%",yaxis_range=[0,1])
            st.plotly_chart(fig,use_container_width=True)
        actual=st.session_state.get("last_historical")
        if actual:
            st.info(f"Historical comparison · HY {actual['year']}: observed class **{actual['actual_class']}**, observed mass change **{actual['actual']:.3f} m w.e.** The prediction above is a separate model output. Because this record belongs to the supplied training dataset, this comparison is in-sample and is not an independent validation.")
        st.markdown("**Feature values used**")
        used=pd.DataFrame({"Feature":FEATURES,"Input value":[result["values"][f] for f in FEATURES]})
        st.dataframe(used,use_container_width=True,hide_index=True)
        # Global model importance, not a local causal explanation.
        if hasattr(model,"feature_importances_"):
            imp=pd.DataFrame({"Feature":FEATURES,"Importance":model.feature_importances_}).sort_values("Importance",ascending=True).tail(12)
            fig=px.bar(imp,x="Importance",y="Feature",orientation="h",title="Global model feature importance",
                       color="Importance",color_continuous_scale="Teal")
            fig.update_layout(template=plotly_template,height=420)
            st.plotly_chart(fig,use_container_width=True)
            st.caption("These are global impurity-based feature importances, not a local explanation of why this individual prediction was made and not causal effects.")
        # geographic locator map
        mp=folium.Map(location=[result["lat"],result["lon"]],zoom_start=6,tiles="OpenStreetMap")
        folium.Marker([result["lat"],result["lon"]],tooltip=f"Prediction: {result['class']}",
                      popup=f"{result['class']}").add_to(mp)
        st_folium(mp,use_container_width=True,height=300,returned_objects=[])
        out=pd.DataFrame([{"predicted_class":result["class"],"latitude":result["lat"],"longitude":result["lon"],
                           **{f"probability_{CLASS_NAMES[i].lower().replace(' ','_')}":result["probabilities"][i] for i in range(3)},
                           **result["values"]}])
        add_download(out,"hkh_glacier_prediction.csv","Download prediction result")

# ----------------------------- methodology -----------------------------
elif page == "Model & methodology":
    hero("MODEL TRANSPARENCY", "Model performance & methodology",
         "Review the selected classifier, spatial validation design, reported metrics, class-level limitations, and responsible-use notes.")
    st.subheader("Classifier comparison · spatial OOF results")
    perf=pd.DataFrame([
        ["Gradient Boosting",.6839,.6297,.6037,.8373],
        ["Random Forest",.6476,.5382,.5294,.7654],
        ["SVM (RBF)",.5292,.4747,.4471,.6796],
        ["Logistic Regression",.5119,.4368,.4180,.6526]
    ],columns=["Model","Accuracy","Balanced accuracy","Macro F1","Macro OvR ROC-AUC"])
    st.dataframe(perf.style.format({c:"{:.2%}" for c in perf.columns[1:4]}|{"Macro OvR ROC-AUC":"{:.4f}"}),
                 use_container_width=True,hide_index=True)
    fig=px.bar(perf.melt(id_vars="Model",var_name="Metric",value_name="Score"),
               x="Model",y="Score",color="Metric",barmode="group",title="Spatial out-of-fold model comparison")
    fig.update_layout(template=plotly_template,height=410,yaxis_tickformat=".0%")
    st.plotly_chart(fig,use_container_width=True)
    st.subheader("Gradient Boosting · class-level performance")
    class_report=pd.DataFrame([
        ["Mass loss",15344,.91,.73,.81],
        ["Mass gain",4976,.64,.66,.65],
        ["Near balance",3378,.27,.50,.35]
    ],columns=["Class","Support","Precision","Recall","F1-score"])
    st.dataframe(class_report.style.format({"Precision":"{:.2f}","Recall":"{:.2f}","F1-score":"{:.2f}"}),
                 use_container_width=True,hide_index=True)
    st.warning("Near balance has the weakest F1-score (0.35). The notebook notes that this class is especially sparse in recent years (0 records in 2022, 5 in 2023, 1 in 2024), so class imbalance and temporal distribution shift are important limitations.")
    st.subheader("Validation design documented in the notebook")
    st.markdown("""
    - Four candidate classifiers: Logistic Regression, Random Forest, RBF-SVM, and Gradient Boosting.
    - 25 spatial clusters constructed from unique grid coordinates using K-Means.
    - Five-fold `StratifiedGroupKFold`; spatial clusters are kept separate between train and validation within each fold.
    - 21 hyperparameter configurations per model (105 total fits across four models as documented).
    - Gradient Boosting selected and then fitted on the full dataset using balanced sample weights.
    """)
    st.error("The same five spatial folds were used for hyperparameter selection and reported OOF performance. The notebook itself flags possible optimism and recommends nested spatial CV or an untouched spatial test region for a publication-grade estimate.")
    st.info("The model includes hydrological_year and full-year aggregated ERA5-Land features. This does not establish future-year generalisation. A separate temporal holdout / spatiotemporal blocked evaluation is needed before making forecasting claims.")

# ----------------------------- data catalogue -----------------------------
elif page == "Data catalogue":
    hero("DATA & DEFINITIONS", "Dataset catalogue",
         "Inspect the supplied data schema, target definition, predictor list, spatial footprint, and export filtered records.")
    a,b,c,d=st.columns(4)
    a.metric("Rows",f"{len(df):,}")
    b.metric("Predictors",len(FEATURES))
    c.metric("Hydrological years",f"{df.hydrological_year.min()}–{df.hydrological_year.max()}")
    d.metric("Grid locations",f"{df[[LAT_COL,LON_COL]].drop_duplicates().shape[0]:,}")
    st.subheader("Spatial and temporal coverage")
    st.write(f"Latitude: **{df[LAT_COL].min():.2f} to {df[LAT_COL].max():.2f}°N**")
    st.write(f"Longitude: **{df[LON_COL].min():.2f} to {df[LON_COL].max():.2f}°E**")
    st.write(f"Hydrological years: **{df.hydrological_year.min()}–{df.hydrological_year.max()}**")
    st.caption("Coverage figures are calculated directly from the supplied CSV. The spatial extent is the dataset's grid footprint and should not be interpreted as a political boundary.")
    st.subheader("Target class definition")
    st.markdown("""
    - **Mass gain:** mass change > +0.1 m w.e.
    - **Mass loss:** mass change < −0.1 m w.e.
    - **Near balance:** −0.1 to +0.1 m w.e. inclusive.

    Target thresholds and labels follow the supplied supervised-learning notebook.
    """)
    st.subheader("The 17 model predictors")
    st.dataframe(pd.DataFrame({"Predictor":FEATURES,"Role":["Glacier area","Hydrological year"]+["ERA5-Land climate predictor"]*15}),
                 hide_index=True,use_container_width=True)
    st.subheader("Dataset preview")
    st.dataframe(df.head(100),use_container_width=True,hide_index=True)
    add_download(df,"hkh_glacier_dataset.csv","Download full dataset")

st.markdown("---")
st.caption("HKH Glacier Mass-Change Classification · Built from the supplied EDA dataset, supervised-learning notebook, and selected Gradient Boosting model. Research support only; not an operational glacier-hazard warning system.")
