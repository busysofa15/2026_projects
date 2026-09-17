import pandas as pd
import numpy as np
import streamlit as st
companies = np.array(["TSLA", "AAPL"])
prices = np.array([100, 200])
drifts = np.array([0.1, 0.2])
volatility = np.array([0.1, 0.3])
st.title("Live market simulator mach 2 version")
days = st.number_input(
    "Enter number of days to simulate: ", min_value=1, value=50, step=1)
step = st.slider("Detail Level (1 = Max Detail)",
                 min_value=1, max_value=500, value=100)
if st.button("Run simulation"):
    time_step = 1/252
    random_variations = np.random.normal(0, 1, (days, len(companies)))
    daily_variations = ((drifts-((volatility)**2)/2)*time_step +
                        volatility*np.sqrt(time_step)*random_variations)
    cumulative_growth = np.cumsum(daily_variations, axis=0)
    prices_after_variations = prices*np.exp(cumulative_growth)
    full_path = np.vstack([prices, prices_after_variations])
    display_path = full_path[::step]
    df = pd.DataFrame(display_path, columns=companies)
    st.line_chart(df)
    st.write("### Final Results")
    for i, name in enumerate(companies):
        st.metric(label=name, value=f"${prices_after_variations[-1, i]:.2f}")
