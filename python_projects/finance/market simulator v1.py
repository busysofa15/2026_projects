import pandas as pd
import numpy as np
import streamlit as st
import time
import math as m
st.title("Live market simulator v1")
days = st.number_input(
    "Enter number of days to simulate: ", min_value=1, value=50, step=1)

market = {
    "AAPL": {
        "price": 188.61,
        "drift": 0.12,
        "volatility": 0.22
    },
    "TSLA": {
        "price": 269.61,
        "drift": 0.15,
        "volatility": 0.48
    }
}
if st.button("Run simulation"):
    history = []
    chart_placeholder = st.empty()
    col1, col2 = st.columns(2)
    aapl_slot = col1.empty()
    tsla_slot = col2.empty()
    for day in range(days):
        price_history = {}

        for ticker, data in market.items():
            time_step = 1/252
            espilon = np.random.normal(0, 1)
            drift = data["drift"]
            price = data["price"]
            volatility = data["volatility"]
            chang_in_price_overtime = (drift - ((volatility)**2)/2)*time_step
            chaos = ((volatility*espilon)*m.sqrt(time_step))
            gbm = (price*np.exp(chang_in_price_overtime+chaos))
            if ticker == "AAPL":
                aapl_slot.metric("Apple", f"${gbm:.2f}")
            else:
                tsla_slot.metric("Tesla", f"${gbm:.2f}")
            market[ticker]["price"] = gbm
            price_history[ticker] = gbm
        history.append(price_history)
        df = pd.DataFrame(history)
        chart_placeholder.line_chart(df, use_container_width=True)
    st.write("Simulation is done")
