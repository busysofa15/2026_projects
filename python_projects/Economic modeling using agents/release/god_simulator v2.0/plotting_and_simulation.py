import numpy as np
from matplotlib import pyplot as plt
from agents import *
from agricultural_sector import *
from b2b_tech_sector import *
from parameters import *
from sectors_and_tick import *
sectors = sector_data()
agents = agent_data(sectors)
business_info = business_data(sectors)
tech = tech_biz_data(sectors)
for day in range(NUM_DAYS):
    agents.tick(sectors, business_info)
    sectors.tick(agents, business_info)     
    tech.tick(agents)
    sectors.tick_tech(business_info, tech)   
    business_info.tick(agents)             
    # --- Masks for Clean Counting ---
    alive_mask = agents.alive
    working_mask = alive_mask & (agents.age >= 18) & (agents.age <= 65)

    # Sector employment (checking working age alive agents)
    is_agri_emp = agents.employed
    is_tech_emp = agents.employed_in_tech
    is_any_emp = (is_agri_emp | is_tech_emp) & working_mask

    # --- Record Metrics ---
    # 1. GDP & Financials
    consumer_spending = sectors.total_transactions
    agri_payroll = np.sum(business_info.money_to_be_subtracted_from_business)
    tech_payroll = np.sum(tech.operational_costs)
    b2b_investment = sectors.tech_transactions
    gdp_history[day] = consumer_spending + agri_payroll + tech_payroll + b2b_investment

    # 2. Population & Demographics
    alive_history[day] = np.sum(alive_mask)
    starvation_history[day] = agents.recent_starvations
    children_count[day] = np.sum(alive_mask & (agents.age < 18))
    working_age_count[day] = np.sum(working_mask)
    retired_count[day] = np.sum(alive_mask & (agents.age > 65))

    # 3. Employment & Labor (Correctly handles dual-sector status)
    agri_employed_count[day] = np.sum(working_mask & is_agri_emp)
    tech_employed_count[day] = np.sum(working_mask & is_tech_emp)
    total_employed_count[day] = np.sum(is_any_emp)
    unemployment_history[day] = np.sum(working_mask & ~is_agri_emp & ~is_tech_emp)

    # 4. Sector Active Business Counts
    agri_biz_count[day] = np.sum(business_info.profits)
    tech_biz_count[day] = np.sum(tech.profits)
days_x = np.arange(0, NUM_DAYS, STEP)
fig, axes = plt.subplots(3, 3, figsize=(18, 10), dpi=100)

# Row 1: Macro Economy
axes[0, 0].plot(days_x, gdp_history[::STEP], color='tab:green')
axes[0, 0].set_title("GDP Over Time")
axes[0, 0].grid(True)

axes[0, 1].plot(days_x, alive_history[::STEP], color='tab:blue')
axes[0, 1].set_title("Alive Agents")
axes[0, 1].grid(True)

axes[0, 2].plot(days_x, starvation_history[::STEP], color='tab:red')
axes[0, 2].set_title("Daily Starvation Deaths")
axes[0, 2].grid(True)

# Row 2: Demographics
axes[1, 0].plot(days_x, children_count[::STEP], color='tab:purple')
axes[1, 0].set_title("Children (<18)")
axes[1, 0].grid(True)

axes[1, 1].plot(days_x, working_age_count[::STEP], color='tab:brown')
axes[1, 1].set_title("Working Age (18-65)")
axes[1, 1].grid(True)

axes[1, 2].plot(days_x, retired_count[::STEP], color='tab:pink')
axes[1, 2].set_title("Retired (65+)")
axes[1, 2].grid(True)

# Row 3: Labor & Businesses Split
axes[2, 0].plot(days_x, unemployment_history[::STEP], color='tab:orange')
axes[2, 0].set_title("Unemployed Count")
axes[2, 0].grid(True)

axes[2, 1].plot(days_x, agri_employed_count[::STEP], label='Agri', color='tab:cyan')
axes[2, 1].plot(days_x, tech_employed_count[::STEP], label='Tech', color='tab:olive')
axes[2, 1].plot(days_x, total_employed_count[::STEP], label='Total', color='tab:gray', linestyle='--')
axes[2, 1].set_title("Employed by Sector")
axes[2, 1].legend()
axes[2, 1].grid(True)

axes[2, 2].plot(days_x, agri_biz_count[::STEP], label='Agri profits', color='tab:green')
axes[2, 2].plot(days_x, tech_biz_count[::STEP], label='Tech profits', color='tab:purple')
axes[2, 2].set_title("Active Businesses")
axes[2, 2].legend()
axes[2, 2].grid(True)

plt.tight_layout()
plt.show()