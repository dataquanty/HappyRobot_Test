
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="Agent Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# CUSTOM CSS (UX polish)
# ---------------------------
st.markdown("""
<style>
.metric-card {
    background-color: #dca439;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
}
.metric-title {
    font-size: 14px;
    color: #1b1c1b;
}
.metric-value {
    font-size: 26px;
    font-weight: bold;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# TITLE
# ---------------------------
st.title("📊 Agent Performance Dashboard")
st.caption("Analyze performance, transactions, and satisfaction")

# ---------------------------
# LOAD DATA
# ---------------------------
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df['date'] = pd.to_datetime(df['date'])

    # ---------------------------
    # SIDEBAR FILTERS
    # ---------------------------
    st.sidebar.header("🔎 Filters")

    date_range = st.sidebar.date_input(
        "Date range",
        [df['date'].min(), df['date'].max()]
    )

    agents = st.sidebar.multiselect(
        "Agents",
        options=sorted(df['agent'].unique()),
        default=sorted(df['agent'].unique())
    )

    # ---------------------------
    # APPLY FILTERS
    # ---------------------------
    filtered_df = df.copy()

    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['date'] >= pd.to_datetime(date_range[0])) &
            (filtered_df['date'] <= pd.to_datetime(date_range[1]))
        ]

    if agents:
        filtered_df = filtered_df[filtered_df['agent'].isin(agents)]

    # ---------------------------
    # KPI SECTION
    # ---------------------------
    st.markdown("### 📌 Key Metrics")

    def metric_card(title, value):
        return f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(metric_card("Avg Amount", f"{filtered_df['amount'].mean():.2f}"), unsafe_allow_html=True)
    col2.markdown(metric_card("Avg Discount", f"{filtered_df['discount'].mean():.2f}"), unsafe_allow_html=True)
    col3.markdown(metric_card("Avg Exchanges", f"{filtered_df['exchanges'].mean():.2f}"), unsafe_allow_html=True)
    col4.markdown(metric_card("Avg Time (s)", f"{filtered_df['time'].mean():.2f}"), unsafe_allow_html=True)

    # ---------------------------
    # PREP DATA
    # ---------------------------
    filtered_df['date_only'] = filtered_df['date'].dt.date

    daily_count = filtered_df.groupby('date_only').size().reset_index(name='count')
    daily_amount = filtered_df.groupby('date_only')['amount'].sum().reset_index()

    # Rolling average (nice UX)
    daily_amount['rolling'] = daily_amount['amount'].rolling(3).mean()

    # ---------------------------
    # MAIN CHARTS
    # ---------------------------
    st.markdown("### 📈 Activity Overview")

    left, right = st.columns([2, 1])

    with left:
        fig1 = px.bar(
            daily_count,
            x='date_only',
            y='count',
            title="Transactions per Day",
            text='count'
        )
        fig1.update_layout(template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.line(
            daily_amount,
            x='date_only',
            y='amount',
            title="Revenue per Day"
        )

        # Add smooth line
        fig2.add_scatter(
            x=daily_amount['date_only'],
            y=daily_amount['rolling'],
            mode='lines',
            name='3-day avg'
        )

        fig2.update_layout(template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

    # ---------------------------
    # SIDE CHARTS
    # ---------------------------
    with right:
        st.markdown("### 🧩 Distribution")

        # Satisfaction
        sat = filtered_df['satisfaction'].value_counts().reset_index()
        sat.columns = ['satisfaction', 'count']

        fig3 = px.pie(
            sat,
            names='satisfaction',
            values='count',
            hole=0.4
        )
        fig3.update_layout(template="plotly_dark", title="Satisfaction")
        st.plotly_chart(fig3, use_container_width=True)

        # Items flag
        df['items_flag'] = df['items'].apply(lambda x: '0 items' if x == 0 else '>0 items')
        items = df['items_flag'].value_counts().reset_index()
        items.columns = ['items_flag', 'count']

        fig4 = px.pie(
            items,
            names='items_flag',
            values='count',
            hole=0.4
        )
        fig4.update_layout(template="plotly_dark", title="Items Distribution (Overall)")
        st.plotly_chart(fig4, use_container_width=True)

    # ---------------------------
    # TABLE (BONUS UX)
    # ---------------------------
    with st.expander("📄 View filtered data"):
        st.dataframe(filtered_df, use_container_width=True)

    # ---------------------------
    # DOWNLOAD BUTTON
    # ---------------------------
    st.download_button(
        "⬇️ Download filtered data",
        filtered_df.to_csv(index=False),
        file_name="filtered_data.csv"
    )

else:
    st.info("👆 Upload a CSV file to start")
