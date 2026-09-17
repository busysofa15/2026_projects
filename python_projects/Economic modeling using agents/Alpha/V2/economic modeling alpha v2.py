import numpy as np
import pandas as pd
import streamlit as st
import time

# --- Setup Constants ---
N_AGENT = 10000
FIRMS = 100

# --- Initialization (Modern Streamlit State) ---
if 'initialized' not in st.session_state:
    st.session_state.agent_cash = np.random.normal(150, 50, size=N_AGENT)
    st.session_state.firm_cash = np.full(FIRMS, 1000.0)
    st.session_state.agent_is_employed = np.ones(N_AGENT, dtype=bool)
    st.session_state.history = []
    st.session_state.initialized = True

st.title("🚀 Modern Macro-Sim")

# --- UI Controls ---
days_to_run = st.sidebar.number_input("Days to Run", min_value=1, value=50)
if st.sidebar.button("Reset Economy"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

run_sim = st.button(f"Start Simulation for {days_to_run} Days")

# --- Updated & Fixed Logic Function ---


def run_economy_tick(agent_cash, firm_cash, agent_is_employed):
    # 1. Setup Parameters
    agent_spending_propensity = np.random.normal(0.8, 0.1, size=N_AGENT)
    agent_productivity = np.clip(
        np.random.normal(0.7, 0.15, size=N_AGENT), 0.2, 1)
    agent_talent = np.clip(
        np.random.normal(1.3, 0.3, size=N_AGENT), 0.3, 5)
    agent_budgets = agent_cash * agent_spending_propensity

    firm_capacity = np.random.normal(10000, 5, size=FIRMS).astype(int)
    firm_efficiency = np.clip(np.random.normal(
        0.5, 0.35, size=FIRMS), 0.1, 1.0)
    # Random work assignment for this tick
    agent_firm_id = np.random.randint(0, FIRMS, size=N_AGENT)

    # 2. Production & Wages
    base_wage = 30
    individual_work = agent_talent * agent_productivity * agent_is_employed
    total_work_per_firm = np.bincount(
        agent_firm_id, weights=individual_work, minlength=FIRMS)

    goods_produced = total_work_per_firm * firm_efficiency
    agent_wages = individual_work * base_wage
    total_wages_per_firm = np.bincount(
        agent_firm_id, weights=agent_wages, minlength=FIRMS)

    # 3. Pricing
    total_costs = total_wages_per_firm
    unit_costs = total_costs / (goods_produced + 1e-9)
    markups = np.random.normal(0.15, 0.1, size=FIRMS)
    prices = unit_costs * (1 + markups)

    # 4. Market (Buying Logic Fix)
    sorted_firms = np.argsort(prices)
    remaining_inventory = goods_produced.copy()
    firm_revenue = np.zeros(FIRMS)
    agent_spent = np.zeros(N_AGENT)
    agent_obtained_today = np.zeros(N_AGENT, dtype=bool)

    for f_idx in sorted_firms:
        p = prices[f_idx]
        inv = remaining_inventory[f_idx]
        if inv < 1 or p <= 0:
            continue

        # Who can afford it and hasn't bought today?
        can_afford = (agent_budgets > p) & (~agent_obtained_today)
        eligible_indices = np.where(can_afford)[0]

        if len(eligible_indices) > 0:
            actual_sales = int(min(len(eligible_indices), inv))
            buyers = eligible_indices[:actual_sales]

            # Transaction
            agent_spent[buyers] += p
            agent_budgets[buyers] -= p
            agent_obtained_today[buyers] = True
            firm_revenue[f_idx] += (actual_sales * p)
            remaining_inventory[f_idx] -= actual_sales

    # 5. Final Balance Sheet Update
    updated_agent_cash = agent_cash + agent_wages - agent_spent
    updated_firm_cash = firm_cash + firm_revenue - total_costs

    return updated_agent_cash, updated_firm_cash, prices.mean()


# --- Execution Loop ---
if run_sim:
    metric_box = st.empty()
    chart_box = st.empty()

    for d in range(days_to_run):
        a_cash, f_cash, avg_p = run_economy_tick(
            st.session_state.agent_cash,
            st.session_state.firm_cash,
            st.session_state.agent_is_employed
        )

        # Save state
        st.session_state.agent_cash = a_cash
        st.session_state.firm_cash = f_cash
        st.session_state.history.append(f_cash.mean())

        # Update UI
        with metric_box.container():
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Agent Wealth", f"${a_cash.mean():.2f}")
            col2.metric("Avg Firm Cash", f"${f_cash.mean():.0f}")
            col3.metric("Avg Market Price", f"${avg_p:.2f}")

        chart_box.line_chart(st.session_state.history)
