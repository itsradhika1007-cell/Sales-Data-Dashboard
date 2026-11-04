import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

NAVY = "#10213D"
BLUE = "#244F91"
LIGHT_BLUE = "#EAF1FA"
WHITE = "#FFFFFF"

st.markdown(f"""
<style>
.stApp {{
    background-color: #F4F7FC;
}}

[data-testid="stSidebar"] {{
    background-color: #10213D;
}}

[data-testid="stSidebar"] * {{
    color: white !important;
}}

.main-title {{
    background: #10213D;
    color: white;
    padding: 24px 28px;
    border-radius: 14px;
    margin-bottom: 22px;
}}

.main-title h1 {{
    color: white;
    margin: 0;
}}

.main-title p {{
    color: #D7E3F5;
}}

div[data-testid="stMetric"] {{
    background: #FFFFFF !important;
    border: 1px solid #D0D9E8 !important;
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(16,33,61,.08);
}}

div[data-testid="stMetricLabel"] p {{
    color: #344054 !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}}

div[data-testid="stMetricValue"] {{
    color: #10213D !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}}

div[data-testid="stMetricDelta"] {{
    opacity: 1 !important;
}}

h2, h3 {{
    color: #10213D;
}}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_excel("sales_data.xlsx")

try:
    df = load_data()
except Exception:
    st.error("Could not find sales_data.xlsx. Please upload it to the same GitHub repository as app.py.")
    st.stop()

df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
df = df.dropna(subset=["Order_Date"])

st.sidebar.title("📊 Sales Analytics")
st.sidebar.caption("Business Performance Portal")
page = st.sidebar.radio(
    "NAVIGATION",
    ["Home", "Sales Dashboard", "Sales Analysis", "About Project"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Filters")

regions = st.sidebar.multiselect(
    "Select Region",
    sorted(df["Region"].dropna().unique()),
    default=sorted(df["Region"].dropna().unique())
)
products = st.sidebar.multiselect(
    "Select Product",
    sorted(df["Product"].dropna().unique()),
    default=sorted(df["Product"].dropna().unique())
)

filtered = df[
    df["Region"].isin(regions) &
    df["Product"].isin(products)
].copy()

if page == "Home":
    st.markdown("""
    <div class="main-title">
        <h1>Sales Data Dashboard</h1>
        <p>Understand sales performance through data, charts and business insights.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Welcome to Sales Analytics")
    st.write(
        "This project presents an interactive analysis of sample sales data. "
        "It uses Excel for data storage, Python for data processing and Streamlit "
        "for the website interface."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Orders", f"{len(filtered):,}")
    c2.metric("Products", f"{filtered['Product'].nunique():,}")
    c3.metric("Regions", f"{filtered['Region'].nunique():,}")

    st.info("Use the navigation menu on the left to explore the dashboard and sales analysis.")

elif page == "Sales Dashboard":
    st.markdown("""
    <div class="main-title">
        <h1>Sales Dashboard</h1>
        <p>Key performance indicators and overall sales performance</p>
    </div>
    """, unsafe_allow_html=True)

    revenue = filtered["Revenue"].sum()
    profit = filtered["Profit"].sum()
    orders = len(filtered)
    quantity = filtered["Quantity"].sum()
    margin = (profit / revenue * 100) if revenue else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Revenue", f"₹{revenue:,.0f}")
    m2.metric("Total Profit", f"₹{profit:,.0f}")
    m3.metric("Total Orders", f"{orders:,}")
    m4.metric("Profit Margin", f"{margin:.1f}%")

    st.markdown("### Sales Trend")
    monthly = (
        filtered.assign(Month=filtered["Order_Date"].dt.to_period("M").astype(str))
        .groupby("Month", as_index=False)["Revenue"].sum()
    )
    fig = px.line(
        monthly, x="Month", y="Revenue", markers=True,
        title="Monthly Revenue Trend",
        color_discrete_sequence=[BLUE]
    )
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        by_region = filtered.groupby("Region", as_index=False)["Revenue"].sum()
        fig_region = px.bar(
            by_region, x="Region", y="Revenue",
            title="Revenue by Region",
            color_discrete_sequence=[BLUE]
        )
        fig_region.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_region, use_container_width=True)

    with right:
        by_product = filtered.groupby("Product", as_index=False)["Revenue"].sum()
        fig_product = px.pie(
            by_product, names="Product", values="Revenue",
            title="Revenue Share by Product", hole=0.4
        )
        st.plotly_chart(fig_product, use_container_width=True)

elif page == "Sales Analysis":
    st.markdown("""
    <div class="main-title">
        <h1>Sales Analysis</h1>
        <p>Explore product, region and sales-channel performance</p>
    </div>
    """, unsafe_allow_html=True)

    a, b = st.columns(2)
    with a:
        product_analysis = filtered.groupby("Product", as_index=False).agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Units_Sold=("Quantity", "sum")
        ).sort_values("Revenue", ascending=False)
        st.subheader("Product Performance")
        st.dataframe(product_analysis, use_container_width=True, hide_index=True)

    with b:
        channel = filtered.groupby("Sales_Channel", as_index=False)["Revenue"].sum()
        fig_channel = px.bar(
            channel, x="Sales_Channel", y="Revenue",
            title="Revenue by Sales Channel",
            color_discrete_sequence=[BLUE]
        )
        fig_channel.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_channel, use_container_width=True)

    st.subheader("Sales Records")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered sales data (CSV)",
        data=csv,
        file_name="filtered_sales_data.csv",
        mime="text/csv"
    )

elif page == "About Project":
    st.markdown("""
    <div class="main-title">
        <h1>About the Project</h1>
        <p>Sales Data Dashboard – College Project</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Project Overview")
    st.write(
        "The Sales Data Dashboard is designed to organise and analyse sales "
        "information and present useful business insights through interactive "
        "visualisations."
    )

    st.subheader("Objectives")
    st.markdown("""
    - Analyse revenue, profit and order performance.
    - Compare sales across products and regions.
    - Identify trends using charts and visualisations.
    - Make sales information easier to understand.
    """)

    st.subheader("Technologies Used")
    st.markdown("""
    - **Microsoft Excel:** Stores the sample sales dataset.
    - **Python:** Processes and analyses the data.
    - **Pandas:** Reads and manages tabular data.
    - **Plotly:** Creates interactive charts.
    - **Streamlit:** Builds the interactive website.
    - **GitHub:** Stores and manages project files.
    """)

    st.caption("Note: This demonstration uses a generated sample dataset for academic purposes.")
