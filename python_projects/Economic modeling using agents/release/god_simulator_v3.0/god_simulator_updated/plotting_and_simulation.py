import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Button
from agents import *
from agricultural_sector import *
from b2b_tech_sector import *
from parameters import *
from sectors_and_tick import *
from secondary_goods_and_services import *

sectors = sector_data()
agents = agent_data(sectors)
business_info = business_data(sectors)
tech = tech_biz_data(sectors)
secondary = secondary_goods_and_services(sectors)

# Tracking arrays for secondary sector metrics
sec_employed_count = np.zeros(NUM_DAYS, dtype=np.int32)
sec_biz_profits = np.zeros(NUM_DAYS, dtype=np.float32)
gdp_history = np.zeros(NUM_DAYS, dtype=np.float32)
alive_history = np.zeros(NUM_DAYS, dtype=np.int32)
starvation_history = np.zeros(NUM_DAYS, dtype=np.int32)
# Population metrics
gdp_history = np.zeros(NUM_DAYS, dtype=np.float32)
alive_history = np.zeros(NUM_DAYS, dtype=np.int32)
starvation_history = np.zeros(NUM_DAYS, dtype=np.int32)

# Demographics
children_count = np.zeros(NUM_DAYS, dtype=np.int32)
working_age_count = np.zeros(NUM_DAYS, dtype=np.int32)
retired_count = np.zeros(NUM_DAYS, dtype=np.int32)

# Multi-Sector Labor Metrics
agri_employed_count = np.zeros(NUM_DAYS, dtype=np.int32)
tech_employed_count = np.zeros(NUM_DAYS, dtype=np.int32)
total_employed_count = np.zeros(NUM_DAYS, dtype=np.int32)
unemployment_history = np.zeros(NUM_DAYS, dtype=np.int32)

# Active Business Counts
agri_biz_count = np.zeros(NUM_DAYS, dtype=np.float32)
tech_biz_count = np.zeros(NUM_DAYS, dtype=np.float32)

for day in range(NUM_DAYS):
    agents.tick(sectors, business_info)
    sectors.tick(agents, business_info, tech, secondary)     
    business_info.tick(agents)         
    tech.tick(agents)
    secondary.tick(agents)
    sectors.tick_tech(business_info, tech, secondary, agents)   
       # --- Masks ---
    alive_mask = agents.alive
    working_mask = alive_mask & (agents.age >= 18) & (agents.age <= 65)

    is_agri_emp = agents.employed
    is_tech_emp = agents.employed_in_tech
    is_sec_emp = agents.employed_in_secondary_services_and_goods
    is_any_emp = (is_agri_emp | is_tech_emp | is_sec_emp) & working_mask

    # --- Record Metrics ---
    # 1. GDP Calculation
    agri_consumer_spending = sectors.total_transactions
    sec_consumer_spending = sectors.secondary_goods_and_services_transactions
    agri_payroll = np.sum(business_info.money_to_be_subtracted_from_business)
    tech_payroll = np.sum(tech.operational_costs)
    sec_payroll = np.sum(secondary.operational_costs)
    b2b_investment = sectors.tech_transactions

    gdp_history[day] = (
        agri_consumer_spending 
        + sec_consumer_spending 
        + agri_payroll 
        + tech_payroll 
        + sec_payroll 
        + b2b_investment
    )

    # 2. Demographics & Population
    alive_history[day] = np.sum(alive_mask)
    starvation_history[day] = agents.recent_starvations
    children_count[day] = np.sum(alive_mask & (agents.age < 18))
    working_age_count[day] = np.sum(working_mask)
    retired_count[day] = np.sum(alive_mask & (agents.age > 65))

    # 3. Employment
    agri_employed_count[day] = np.sum(working_mask & is_agri_emp)
    tech_employed_count[day] = np.sum(working_mask & is_tech_emp)
    sec_employed_count[day] = np.sum(working_mask & is_sec_emp)
    total_employed_count[day] = np.sum(is_any_emp)
    unemployment_history[day] = np.sum(working_mask & ~is_any_emp)

    # 4. Sector Profits
    agri_biz_count[day] = np.sum(business_info.profits)
    tech_biz_count[day] = np.sum(tech.profits)
    sec_biz_profits[day] = np.sum(secondary.profits)

days_x = np.arange(0, NUM_DAYS, STEP)

# =========================================================
# HYBRID VIEWPORT ARCHITECTURE (DASHBOARDS + FULLSCREEN)
# =========================================================

# 7 Core Metrics
charts_config = [
    {
        "title": "Gross Domestic Product (GDP)",
        "ylabel": "Currency Units ($)",
        "plots": [("GDP History", gdp_history, "tab:green", "-")]
    },
    {
        "title": "Total Population (Alive Agents)",
        "ylabel": "Agent Count",
        "plots": [("Alive Agents", alive_history, "tab:blue", "-")]
    },
    {
        "title": "Daily Starvation Mortality",
        "ylabel": "Deaths / Day",
        "plots": [("Starvation Deaths", starvation_history, "tab:red", "-")]
    },
    {
        "title": "Demographics Breakdown",
        "ylabel": "Agent Count",
        "plots": [
            ("Children (<18)", children_count, "tab:purple", "-"),
            ("Working Age (18-65)", working_age_count, "tab:brown", "-"),
            ("Retired (65+)", retired_count, "tab:pink", "-")
        ]
    },
    {
        "title": "Labor Market: Unemployed Count",
        "ylabel": "Unemployed Agents",
        "plots": [("Unemployed Workforce", unemployment_history, "tab:orange", "-")]
    },
    {
        "title": "Workforce Distribution by Sector",
        "ylabel": "Employed Workers",
        "plots": [
            ("Total Employed", total_employed_count, "tab:gray", "--"),
            ("Agri Workforce", agri_employed_count, "tab:cyan", "-"),
            ("Tech Workforce", tech_employed_count, "tab:olive", "-"),
            ("Secondary Workforce", sec_employed_count, "tab:red", "-"),
        ]
    },
    {
        "title": "Industry Sector Profits Overview",
        "ylabel": "Net Profits ($)",
        "plots": [
            ("Agri Profits", agri_biz_count, "tab:green", "-"),
            ("Tech Profits", tech_biz_count, "tab:purple", "-"),
            ("Secondary Profits", sec_biz_profits, "tab:orange", "-"),
        ]
    }
]

# Pagination Map: 2 Dashboards followed by 7 isolated single views
views = [
    {"type": "grid", "title": "Dashboard 1: Macroeconomy & Population", "charts": [0, 1, 2, 3]},
    {"type": "grid", "title": "Dashboard 2: Labor Market & Industries", "charts": [4, 5, 6]},
    {"type": "single", "chart": 0},
    {"type": "single", "chart": 1},
    {"type": "single", "chart": 2},
    {"type": "single", "chart": 3},
    {"type": "single", "chart": 4},
    {"type": "single", "chart": 5},
    {"type": "single", "chart": 6}
]

fig = plt.figure(figsize=(16, 9), dpi=100)
fig.canvas.manager.set_window_title("Economy Simulation - Hybrid Metric Explorer")

try:
    fig.canvas.manager.full_screen_toggle()
except Exception:
    try:
        fig.canvas.manager.maximize()
    except Exception:
        pass

# Global layout padding (applies to both single and grid subplots seamlessly)
fig.subplots_adjust(bottom=0.14, top=0.90, left=0.08, right=0.82, hspace=0.35, wspace=0.25)

# Layer 1: Single full-screen axis
ax_single = fig.add_subplot(1, 1, 1)

# Layer 2: 2x2 grid axes
axes_grid = [
    fig.add_subplot(2, 2, 1),
    fig.add_subplot(2, 2, 2),
    fig.add_subplot(2, 2, 3),
    fig.add_subplot(2, 2, 4)
]

current_view = 0

def draw_chart(ax, cfg, is_single):
    for label, data, color, linestyle in cfg["plots"]:
        ax.plot(
            days_x, 
            data[::STEP], 
            label=label, 
            color=color, 
            linestyle=linestyle, 
            linewidth=2.5 if is_single else 1.8
        )
        
    if not is_single:
        ax.set_title(cfg["title"], fontsize=12, fontweight='bold')
        
    ax.set_xlabel("Simulation Days", fontsize=12 if is_single else 10, fontweight='bold')
    ax.set_ylabel(cfg["ylabel"], fontsize=12 if is_single else 10, fontweight='bold')
    ax.grid(True, linestyle="--", alpha=0.6)
    
    # Render legend (pushed outside to the right for single view, tucked inside for grid)
    if len(cfg["plots"]) > 1 or (len(cfg["plots"]) == 1 and cfg["plots"][0][0] != cfg["title"]):
        if is_single:
            ax.legend(fontsize=11, loc="upper left", bbox_to_anchor=(1.02, 1.0), framealpha=0.9)
        else:
            ax.legend(fontsize=9, loc="upper left", framealpha=0.8)

def render_current_view():
    view = views[current_view]
    
    # Hide all axes to prevent overlap
    ax_single.set_visible(False)
    for ax in axes_grid:
        ax.set_visible(False)
    
    # Set main window title
    if view["type"] == "grid":
        main_title = view["title"]
    else:
        main_title = f"Fullscreen: {charts_config[view['chart']]['title']}"
    
    fig.suptitle(f"{main_title} (View {current_view + 1}/{len(views)})", fontsize=16, fontweight='bold')
    
    # Render based on view type
    if view["type"] == "single":
        ax = ax_single
        ax.clear()
        ax.set_visible(True)
        cfg = charts_config[view["chart"]]
        draw_chart(ax, cfg, is_single=True)
        
    elif view["type"] == "grid":
        for i, chart_idx in enumerate(view["charts"]):
            ax = axes_grid[i]
            ax.clear()
            ax.set_visible(True)
            cfg = charts_config[chart_idx]
            draw_chart(ax, cfg, is_single=False)

    fig.canvas.draw_idle()

# --- Navigation Buttons ---
ax_prev = fig.add_axes([0.38, 0.03, 0.10, 0.05])
ax_next = fig.add_axes([0.52, 0.03, 0.10, 0.05])

btn_prev = Button(ax_prev, '◄ Prev View', color='lightgray', hovercolor='0.85')
btn_next = Button(ax_next, 'Next View ➔', color='lightgray', hovercolor='0.85')

def next_view_event(event):
    global current_view
    current_view = (current_view + 1) % len(views)
    render_current_view()

def prev_view_event(event):
    global current_view
    current_view = (current_view - 1) % len(views)
    render_current_view()

btn_next.on_clicked(next_view_event)
btn_prev.on_clicked(prev_view_event)

render_current_view()
plt.show()