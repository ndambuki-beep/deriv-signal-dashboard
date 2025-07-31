# Streamlit Dashboard for Deriv Signal Analyzer

import streamlit as st
import pandas as pd
import time
import altair as alt

st.set_page_config(page_title="Deriv Signal Dashboard", layout="wide")

st.title("📈 Deriv Real-Time Signal Dashboard")

placeholder = st.empty()
signal_log_path = "signals_log.csv"

symbol_filter = st.sidebar.multiselect("Filter Symbols", options=[], default=[])
direction_filter = st.sidebar.selectbox("Signal Type", options=["All", "BUY", "SELL"])

# Sound alert toggle
alert_sound = st.sidebar.checkbox("🔔 Enable Alert Sound on New Signal", value=True)
last_signal_time = None

while True:
    with placeholder.container():
        st.subheader("🔔 Recent Trading Signals")

        try:
            df = pd.read_csv(signal_log_path, names=["Timestamp", "Symbol", "Direction", "RSI"], header=None)
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            df = df.sort_values(by="Timestamp", ascending=False)

            # Set filters if not already selected
            if not symbol_filter:
                symbol_filter = df['Symbol'].unique().tolist()
            filtered_df = df[df['Symbol'].isin(symbol_filter)]
            if direction_filter != "All":
                filtered_df = filtered_df[filtered_df['Direction'] == direction_filter]

            st.dataframe(filtered_df, use_container_width=True)

            # Summary stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Signals", len(filtered_df))
                st.metric("Unique Symbols", filtered_df['Symbol'].nunique())
            with col2:
                st.metric("Buy Signals", len(filtered_df[filtered_df['Direction'] == 'BUY']))
                st.metric("Sell Signals", len(filtered_df[filtered_df['Direction'] == 'SELL']))

            # Chart of signal frequency
            chart_data = filtered_df.groupby(["Timestamp", "Direction"]).size().reset_index(name="Count")
            chart = alt.Chart(chart_data).mark_bar().encode(
                x='Timestamp:T',
                y='Count:Q',
                color='Direction:N'
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)

            # Play alert sound if new signal
            if alert_sound and not last_signal_time:
                last_signal_time = df.iloc[0]['Timestamp']
            elif alert_sound and df.iloc[0]['Timestamp'] != last_signal_time:
                last_signal_time = df.iloc[0]['Timestamp']
                st.audio("https://www.soundjay.com/button/beep-07.wav", autoplay=True)

        except FileNotFoundError:
            st.warning("No signals have been logged yet.")

    time.sleep(5)
    st.rerun()
