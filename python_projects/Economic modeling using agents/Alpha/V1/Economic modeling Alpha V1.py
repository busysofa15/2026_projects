import numpy as np
import pandas as pd
import math as m
import streamlit as st

N_AGENT = 10000
FIRMS = 50


def run_economy_tick(agent_starting_cash, agent_employed, firm_efficiency, firm_cap):
    agent_spending = np.random.normal(loc=0.6, scale=0.1, size=N_AGENT)
    agent_productivity = np.random.normal(loc=0.5, scale=0.15, size=N_AGENT)
    agent_productivity = np.clip(agent_productivity, 0, 1)
    agent_talent = np.random.normal(loc=1.3, scale=0.3, size=N_AGENT)
    agent_is_employed = agent_employed
    base_wage = 50
    individual_work = agent_talent * agent_productivity * agent_is_employed
    agent_wages = individual_work * base_wage
    agent_budgets = agent_spending
    agent_goods_obtained = np.zeros(N_AGENT, dtype=bool)
    agent_firm_id = np.random.randint(0, FIRMS, size=N_AGENT)
    total_work_per_firm = np.bincount(
        agent_firm_id, weights=individual_work, minlength=FIRMS)
    goods_per_firm = total_work_per_firm * firm_efficiency
    markup_per_firm = np.random.normal(loc=0.5, scale=0.35, size=FIRMS)
    total_wages_per_firm = np.bincount(
        agent_firm_id, weights=agent_wages, minlength=FIRMS)
    overhead_rate = 10.0
    fixed_costs = firm_cap * overhead_rate
    total_cost_per_firm = total_wages_per_firm + fixed_costs
    unit_cost = total_cost_per_firm / (goods_per_firm + 1e-9)
    prices_per_firm = unit_cost * (1 + markup_per_firm)
    sorted_firm_indices = np.argsort(prices_per_firm)
    remaining_inventory = goods_per_firm.copy()
    firm_revenue = np.zeros(FIRMS)
    total_spent_by_agents = np.zeros(N_AGENT)
    for f_idx in sorted_firm_indices:
        price = prices_per_firm[f_idx]
        inventory = remaining_inventory[f_idx]
        if inventory <= 0:
            continue
        can_afford = (agent_budgets >= price) & (~agent_goods_obtained)
        eligible_count = np.sum(can_afford)
        if eligible_count > 0:
            actual_sales = int(min(eligible_count, inventory))
            buyer_indices = np.where(can_afford)[0][:actual_sales]
            agent_goods_obtained[buyer_indices] = True
            agent_budgets[buyer_indices] -= price
            total_spent_by_agents[buyer_indices] += price
            firm_revenue[f_idx] += (actual_sales * price)
            remaining_inventory[f_idx] -= actual_sales
    updated_agent_cash = agent_wages - total_spent_by_agents
    updated_firm_cash = firm_revenue - total_cost_per_firm
    gdp = np.sum(firm_revenue)

    return updated_agent_cash, updated_firm_cash, prices_per_firm


# --- INITIALIZE DATA (Once per session) ---
if 'agent_cash' not in st.session_state:
    st.session_state.agent_cash = np.random.normal(1000, 200, size=N_AGENT)
    st.session_state.agent_employed = np.ones(N_AGENT, dtype=bool)
    st.session_state.firm_efficiency = np.random.normal(0.5, 0.35, size=FIRMS)
    st.session_state.firm_cap = np.random.normal(40, 5, size=FIRMS).astype(int)
    st.session_state.gdp_history = []

st.title("1994 Car Empire Sim Alpha")
# --- INPUT FOR TICKS ---
num_ticks = st.number_input(
    "Days to Simulate", min_value=1, max_value=1000000, value=1)

if st.button(f"Run {num_ticks} Days"):
    # Create a progress bar for longer simulations
    progress_bar = st.progress(0)

    for i in range(num_ticks):
        # Run the economy math
        updated_cash, updated_profit, prices = run_economy_tick(
            st.session_state.agent_cash,
            st.session_state.agent_employed,
            st.session_state.firm_efficiency,
            st.session_state.firm_cap
        )

        # Update the session state money for the NEXT loop iteration
        st.session_state.agent_cash = updated_cash

        # Log the GDP (Total cash in system)
        current_gdp = np.sum(updated_cash)
        st.session_state.gdp_history.append(current_gdp)

        # Update progress bar
        progress_bar.progress((i + 1) / num_ticks)

    st.success(f"Simulation complete for {num_ticks} days.")

# --- THE DASHBOARD ---
if st.session_state.gdp_history:
    st.subheader("Total Liquidity (GDP) Over Time")
    st.line_chart(st.session_state.gdp_history)

    avg_p = np.mean(prices)
    st.metric("Final Market Price", f"${avg_p:.2f}")
