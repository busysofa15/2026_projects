import numpy as np
import plotly.graph_objects as pg
import streamlit as st
import pandas as pd
N_AGENTS = 100000
land = np.array([5000, 1000, 500, 500, 500, 150])
# 0 = agro, 1 = resid, 2 = offices , 3=  mining 4= industries, 5= energy sector
base_cost_land = np.array([100, 120, 200, 150, 130])
unitsproducedandpopulationdensity = np.array([1, 4, 10, 1, 1])
# 0=agro 1=resi 2=offi 3=mining 4=energy
agent_metabolism = 0.2
health_deterioration = 0.1
fields = np.array([0, 1, 2, 3, 4, 5, 6, 7])
opportunity = np.ones(len(fields)) / len(fields)
###
rng = np.random.default_rng()
opportunity_probs = opportunity / np.clip(np.sum(opportunity), 1e-9, None)
total_money_in_field = np.zeros(len(fields))
government_id = 101
# 0 = agri 1 = mining 2= manufacturing 3 = venture capitals 4 = tech 5 = medical
# 6 = construction  #7 = energy
agents_alive = np.zeros(N_AGENTS)
agents_alive[:100] = 1
total_alive = np.sum(agents_alive).astype(int)
age = np.zeros(total_alive)
age = (age+1)/365
age_when_work = (age >= 18)
age_when_stop_work = (age >= 62)
is_working_age = np.zeros(total_alive)
is_working_age = (age >= 18) & (age < 62)
is_working_age[:100] = 1
print(is_working_age)
total_no_of_working_age = np.sum(is_working_age).astype(int)
agent_talent = np.random.normal(loc=1, scale=0.2, size=total_no_of_working_age)
agent_productivity = np.random.normal(
    loc=0.9, scale=0.1, size=total_no_of_working_age)
agent_id = np.arange(N_AGENTS)
alive_agent_ids = agent_id[agents_alive == 1]
working_age_id = alive_agent_ids[is_working_age]
agent_experience = np.ones(total_no_of_working_age)
agent_learning_rate = np.random.normal(
    loc=1.04, scale=0.03, size=total_no_of_working_age)
agent_learning_rate = np.clip(agent_learning_rate, 0, None)
agent_experience = (agent_experience+agent_learning_rate[is_working_age])/365
agent_business_sectorspawning = rng.choice(
    fields, size=total_no_of_working_age, p=opportunity_probs)
p_business = 0.5
p_agent_starting_business = rng.random(total_no_of_working_age)
business_started = (p_agent_starting_business < p_business)
business_field_id = agent_business_sectorspawning[business_started]
total_businesses = np.sum(business_started)
business_id = np.arange(total_businesses)
print(business_id)
business_owner_id = working_age_id[business_started]
money_by_everyone = (1e-9)
agent_wages = np.random.normal(loc=200, scale=50, size=total_no_of_working_age)
agent_money = agent_wages
employed_id = np.zeros(total_no_of_working_age, dtype=int)
business_employed_in_id = np.full(
    total_no_of_working_age, total_businesses)
agent_food_stock = np.zeros(total_alive)
agent_health_bar = np.ones(total_alive)
agent_health_bar -= health_deterioration
agent_food_stock -= agent_metabolism
urgency = np.maximum(0, 1 - agent_food_stock)
food_money_per_agent = agent_money*urgency
market_share = np.zeros(total_businesses)
sales_inventory = np.zeros(total_businesses)
sales_inventory = np.clip(sales_inventory, 1, None)
total_money_in_field[0] = np.sum(food_money_per_agent)
money_per_business_sector = total_money_in_field[business_field_id]
medical_price = (1e-9)
production = np.zeros(total_businesses)
labor = agent_productivity[is_working_age] * \
    agent_talent[is_working_age]*agent_experience[is_working_age]
total_labor_with_unemployed = np.bincount(business_employed_in_id,
                                          labor, minlength=total_businesses)
total_labor = total_labor_with_unemployed[:total_businesses]
inventory_building = np.random.normal(
    loc=2, scale=1, size=total_businesses).astype(int)
total_no_of_inventory_buildings = np.bincount(business_id, inventory_building)
inventory_storage_per_inventory_building = 50
business_inventory_storage = total_no_of_inventory_buildings * \
    inventory_storage_per_inventory_building
infinite_storage_mask = (business_field_id == 4) | (business_field_id == 5)
business_inventory_storage[infinite_storage_mask] = 1e12
business_inventory = np.zeros(total_businesses)
business_inventory = np.clip(business_inventory, 0, business_inventory_storage)
sales_inventory_mask = (sales_inventory > 1e-9)
business_opportunity_mapped = opportunity[business_field_id]
units_sold_per_business = np.zeros(total_businesses)
tech_units_brought = np.zeros(total_businesses)
tools_units_used = np.zeros(total_businesses)
total_agro_businesses = len(business_id[business_field_id == 0])
print(total_agro_businesses)
fertilizer_units_brought = np.zeros(total_agro_businesses)
land_units_brought = np.zeros(total_businesses)
land_units_brought = np.clip(land_units_brought, 1e-9, None)
production_cost = np.zeros(total_businesses)
tech_units_per_module = tech_units_brought/land_units_brought
tool_unit_per_module = tools_units_used/land_units_brought
labor_per_module = total_labor/land_units_brought
mask_0 = (business_field_id == 0)
fertilizer_units_per_module = fertilizer_units_brought / \
    land_units_brought[mask_0]
# MANUFACTURING#
mask_2 = (business_field_id == 2)
production[mask_2] = (
    0.9**tech_units_per_module[mask_2]*tech_units_per_module[mask_2] *
    0.9**labor_per_module[mask_2]*labor_per_module[mask_2]
    * 0.92**tool_unit_per_module[mask_2]*tool_unit_per_module[mask_2]+0.1*labor_per_module[mask_2]
)*land_units_brought[mask_2]
production_cost[mask_2]
# TECH#
mask_4 = (business_field_id == 4)
production[mask_4] = (
    0.9**labor_per_module[mask_4]*labor_per_module[mask_4] *
    0.95**tool_unit_per_module[mask_4]
    * tool_unit_per_module[mask_4]
)*land_units_brought[mask_4]
production_cost[mask_4]
# MINING#
mask_1 = (business_field_id == 1)
production[mask_1] = (
    0.9**labor_per_module[mask_1]*labor_per_module[mask_1] *
    0.93**tool_unit_per_module[mask_1]*tool_unit_per_module[mask_1]
    * 0.85**tech_units_per_module[mask_1]*tech_units_per_module[mask_1] + unitsproducedandpopulationdensity[3]*labor_per_module[mask_1]
)*land_units_brought[mask_1]
production_cost[mask_1]
# AGRO#
production[mask_0] = (
    0.8**fertilizer_units_per_module*fertilizer_units_per_module *
    0.9**labor_per_module[mask_0]*labor_per_module[mask_0]
    * 0.9**tech_units_per_module[mask_0]*tech_units_per_module[mask_0]*tool_unit_per_module[mask_0]*tool_unit_per_module[mask_0]
    + labor_per_module[mask_0]
)*land_units_brought[mask_0]
# ENERGY#
mask_7 = (business_field_id == 7)
production[mask_7] = (
    0.8**labor_per_module[mask_7]*labor_per_module[mask_7] *
    0.95**tool_unit_per_module[mask_7]*tool_unit_per_module[mask_7]
    * 0.9**tech_units_per_module[mask_7]*tech_units_per_module[mask_7]+labor_per_module[mask_7]
)*land_units_brought[mask_7]
production_cost[mask_7]
# MEDICAL#
mask_5 = (business_field_id == 5)
production[mask_5] = (
    0.9**labor_per_module[mask_5]*labor_per_module[mask_5] *
    0.9**tech_units_per_module[mask_5]*tech_units_per_module[mask_5]
    * 0.9**tool_unit_per_module[mask_5]*tool_unit_per_module[mask_5]+labor_per_module[mask_5]
)*land_units_brought[mask_5]
production_cost[mask_5]
delta = 1e-5
production_delta = np.zeros(total_businesses)

# --- A. Derivative with respect to Labor ---
labor_delta = total_labor + delta
labor_per_module_delta = labor_delta / land_units_brought

production_delta[mask_2] = (0.9**tech_units_per_module[mask_2]*tech_units_per_module[mask_2] * 0.9**labor_per_module_delta[mask_2]*labor_per_module_delta[mask_2]
                            * 0.92**tool_unit_per_module[mask_2]*tool_unit_per_module[mask_2] + 0.1*labor_per_module_delta[mask_2]) * land_units_brought[mask_2]
production_delta[mask_4] = (0.9**labor_per_module_delta[mask_4]*labor_per_module_delta[mask_4]
                            * 0.95**tool_unit_per_module[mask_4]*tool_unit_per_module[mask_4]) * land_units_brought[mask_4]
production_delta[mask_1] = (0.9**labor_per_module_delta[mask_1]*labor_per_module_delta[mask_1] * 0.93**tool_unit_per_module[mask_1]*tool_unit_per_module[mask_1] *
                            0.85**tech_units_per_module[mask_1]*tech_units_per_module[mask_1] + unitsproducedandpopulationdensity[3]*labor_per_module_delta[mask_1]) * land_units_brought[mask_1]
production_delta[mask_0] = (0.8**fertilizer_units_per_module*fertilizer_units_per_module * 0.9**labor_per_module_delta[mask_0]*labor_per_module_delta[mask_0] * 0.9 **
                            tech_units_per_module[mask_0]*tech_units_per_module[mask_0]*tool_unit_per_module[mask_0]*tool_unit_per_module[mask_0] + labor_per_module_delta[mask_0]) * land_units_brought[mask_0]
production_delta[mask_7] = (0.8**labor_per_module_delta[mask_7]*labor_per_module_delta[mask_7] * 0.95**tool_unit_per_module[mask_7]*tool_unit_per_module[mask_7]
                            * 0.9**tech_units_per_module[mask_7]*tech_units_per_module[mask_7] + labor_per_module_delta[mask_7]) * land_units_brought[mask_7]
production_delta[mask_5] = (0.9**labor_per_module_delta[mask_5]*labor_per_module_delta[mask_5] * 0.9**tech_units_per_module[mask_5]*tech_units_per_module[mask_5]
                            * 0.9**tool_unit_per_module[mask_5]*tool_unit_per_module[mask_5] + labor_per_module_delta[mask_5]) * land_units_brought[mask_5]

dProd_dLabor = (production_delta - production) / delta


# --- B. Derivative with respect to Tools ---
tools_delta = tools_units_used + delta
tool_unit_per_module_delta = tools_delta / land_units_brought

production_delta[mask_2] = (0.9**tech_units_per_module[mask_2]*tech_units_per_module[mask_2] * 0.9**labor_per_module[mask_2]*labor_per_module[mask_2]
                            * 0.92**tool_unit_per_module_delta[mask_2]*tool_unit_per_module_delta[mask_2] + 0.1*labor_per_module[mask_2]) * land_units_brought[mask_2]
production_delta[mask_4] = (0.9**labor_per_module[mask_4]*labor_per_module[mask_4] * 0.95 **
                            tool_unit_per_module_delta[mask_4]*tool_unit_per_module_delta[mask_4]) * land_units_brought[mask_4]
production_delta[mask_1] = (0.9**labor_per_module[mask_1]*labor_per_module[mask_1] * 0.93**tool_unit_per_module_delta[mask_1]*tool_unit_per_module_delta[mask_1]
                            * 0.85**tech_units_per_module[mask_1]*tech_units_per_module[mask_1] + unitsproducedandpopulationdensity[3]*labor_per_module[mask_1]) * land_units_brought[mask_1]
production_delta[mask_0] = (0.8**fertilizer_units_per_module*fertilizer_units_per_module * 0.9**labor_per_module[mask_0]*labor_per_module[mask_0] * 0.9**tech_units_per_module[mask_0]
                            * tech_units_per_module[mask_0]*tool_unit_per_module_delta[mask_0]*tool_unit_per_module_delta[mask_0] + labor_per_module[mask_0]) * land_units_brought[mask_0]
production_delta[mask_7] = (0.8**labor_per_module[mask_7]*labor_per_module[mask_7] * 0.95**tool_unit_per_module_delta[mask_7]*tool_unit_per_module_delta[mask_7]
                            * 0.9**tech_units_per_module[mask_7]*tech_units_per_module[mask_7] + labor_per_module[mask_7]) * land_units_brought[mask_7]
production_delta[mask_5] = (0.9**labor_per_module[mask_5]*labor_per_module[mask_5] * 0.9**tech_units_per_module[mask_5]*tech_units_per_module[mask_5]
                            * 0.9**tool_unit_per_module_delta[mask_5]*tool_unit_per_module_delta[mask_5] + labor_per_module[mask_5]) * land_units_brought[mask_5]

dProd_dTools = (production_delta - production) / delta


# --- C. Derivative with respect to Tech ---
tech_delta = tech_units_brought + delta
tech_units_per_module_delta = tech_delta / land_units_brought

production_delta[mask_2] = (0.9**tech_units_per_module_delta[mask_2]*tech_units_per_module_delta[mask_2] * 0.9**labor_per_module[mask_2] *
                            labor_per_module[mask_2] * 0.92**tool_unit_per_module[mask_2]*tool_unit_per_module[mask_2] + 0.1*labor_per_module[mask_2]) * land_units_brought[mask_2]
production_delta[mask_4] = (0.9**labor_per_module[mask_4]*labor_per_module[mask_4] * 0.95 **
                            tool_unit_per_module[mask_4]*tool_unit_per_module[mask_4]) * land_units_brought[mask_4]
production_delta[mask_1] = (0.9**labor_per_module[mask_1]*labor_per_module[mask_1] * 0.93**tool_unit_per_module[mask_1]*tool_unit_per_module[mask_1] * 0.85 **
                            tech_units_per_module_delta[mask_1]*tech_units_per_module_delta[mask_1] + unitsproducedandpopulationdensity[3]*labor_per_module[mask_1]) * land_units_brought[mask_1]
production_delta[mask_0] = (0.8**fertilizer_units_per_module*fertilizer_units_per_module * 0.9**labor_per_module[mask_0]*labor_per_module[mask_0] * 0.9**tech_units_per_module_delta[mask_0]
                            * tech_units_per_module_delta[mask_0]*tool_unit_per_module[mask_0]*tool_unit_per_module[mask_0] + labor_per_module[mask_0]) * land_units_brought[mask_0]
production_delta[mask_7] = (0.8**labor_per_module[mask_7]*labor_per_module[mask_7] * 0.95**tool_unit_per_module[mask_7]*tool_unit_per_module[mask_7]
                            * 0.9**tech_units_per_module_delta[mask_7]*tech_units_per_module_delta[mask_7] + labor_per_module[mask_7]) * land_units_brought[mask_7]
production_delta[mask_5] = (0.9**labor_per_module[mask_5]*labor_per_module[mask_5] * 0.9**tech_units_per_module_delta[mask_5]*tech_units_per_module_delta[mask_5]
                            * 0.9**tool_unit_per_module[mask_5]*tool_unit_per_module[mask_5] + labor_per_module[mask_5]) * land_units_brought[mask_5]

dProd_dTech = (production_delta - production) / delta


# --- D. Derivative with respect to Fertilizer (Agro Only) ---
fertilizer_delta = fertilizer_units_brought + delta
fertilizer_units_per_module_delta = fertilizer_delta / \
    land_units_brought[mask_0]

production_delta[:] = production
production_delta[mask_0] = (
    0.8**fertilizer_units_per_module_delta * fertilizer_units_per_module_delta *
    0.9**labor_per_module[mask_0] * labor_per_module[mask_0] *
    0.9**tech_units_per_module[mask_0] * tech_units_per_module[mask_0] * tool_unit_per_module[mask_0] * tool_unit_per_module[mask_0] +
    labor_per_module[mask_0]
) * land_units_brought[mask_0]

dProd_dFertilizer = (production_delta - production) / delta


# --- E. Derivative with respect to Land ---
land_delta = land_units_brought + delta

tech_units_per_module_delta = tech_units_brought / land_delta
tool_unit_per_module_delta = tools_units_used / land_delta
labor_per_module_delta = total_labor / land_delta
fertilizer_units_per_module_delta = fertilizer_units_brought / \
    land_delta[mask_0]

production_delta[mask_2] = (0.9**tech_units_per_module_delta[mask_2]*tech_units_per_module_delta[mask_2] * 0.9**labor_per_module_delta[mask_2]*labor_per_module_delta[mask_2]
                            * 0.92**tool_unit_per_module_delta[mask_2]*tool_unit_per_module_delta[mask_2] + 0.1*labor_per_module_delta[mask_2]) * land_delta[mask_2]
production_delta[mask_4] = (0.9**labor_per_module_delta[mask_4]*labor_per_module_delta[mask_4] *
                            0.95**tool_unit_per_module_delta[mask_4]*tool_unit_per_module_delta[mask_4]) * land_delta[mask_4]
production_delta[mask_1] = (0.9**labor_per_module_delta[mask_1]*labor_per_module_delta[mask_1] * 0.93**tool_unit_per_module_delta[mask_1]*tool_unit_per_module_delta[mask_1]
                            * 0.85**tech_units_per_module_delta[mask_1]*tech_units_per_module_delta[mask_1] + unitsproducedandpopulationdensity[3]*labor_per_module_delta[mask_1]) * land_delta[mask_1]
production_delta[mask_0] = (0.8**fertilizer_units_per_module_delta*fertilizer_units_per_module_delta * 0.9**labor_per_module_delta[mask_0]*labor_per_module_delta[mask_0] * 0.9 **
                            tech_units_per_module_delta[mask_0]*tech_units_per_module_delta[mask_0]*tool_unit_per_module_delta[mask_0]*tool_unit_per_module_delta[mask_0] + labor_per_module_delta[mask_0]) * land_delta[mask_0]
production_delta[mask_7] = (0.8**labor_per_module_delta[mask_7]*labor_per_module_delta[mask_7] * 0.95**tool_unit_per_module_delta[mask_7]*tool_unit_per_module_delta[mask_7]
                            * 0.9**tech_units_per_module_delta[mask_7]*tech_units_per_module_delta[mask_7] + labor_per_module_delta[mask_7]) * land_delta[mask_7]
production_delta[mask_5] = (0.9**labor_per_module_delta[mask_5]*labor_per_module_delta[mask_5] * 0.9**tech_units_per_module_delta[mask_5]*tech_units_per_module_delta[mask_5]
                            * 0.9**tool_unit_per_module_delta[mask_5]*tool_unit_per_module_delta[mask_5] + labor_per_module_delta[mask_5]) * land_delta[mask_5]

dProd_dLand = (production_delta - production) / delta
business_inventory += production
price = market_share*money_per_business_sector/sales_inventory
sales_inventory_transfer = units_sold_per_business + \
    (business_opportunity_mapped*business_inventory)
price = np.maximum(price, production_cost)
food_price = price[business_field_id == 0]
want_buy_food = (agent_food_stock <= 1.00)
# buying
sales_inventory += sales_inventory_transfer
business_inventory -= sales_inventory_transfer
sales_inventory = sales_inventory.astype(int)
agri_inv = sales_inventory[business_field_id == 0]
agri_id = business_id[business_field_id == 0]
business_revenue = np.zeros(total_businesses)
business_revenue = np.clip(business_revenue, 1e-9, None)
stock_available = (agri_inv > 0)
unit_prices = np.repeat(food_price, agri_inv)
total_food_available = len(unit_prices)
potential_buyers = np.where(want_buy_food)[0]
random_buyers = min(total_food_available, len(potential_buyers))
unit_sellers = np.repeat(agri_id, agri_inv)
if random_buyers > 0:
    market_participants = rng.choice(
        potential_buyers, size=random_buyers, replace=False)
else:
    market_participants = np.array([])
n_sales = min(len(market_participants), len(unit_prices))
actual_sellers = np.array([], dtype=int)
actual_prices = np.array([], dtype=float)
actual_buyers = np.array([], dtype=int)
if n_sales > 0:
    shuffled_indices = rng.permutation(total_food_available)[:random_buyers]
    potential_sellers = unit_sellers[shuffled_indices]
    potential_buyers = market_participants[shuffled_indices]
    potential_prices = unit_prices[:n_sales]
    can_buy = (agent_money[potential_buyers] >= potential_prices)
    actual_sellers = potential_sellers[can_buy]
    actual_buyers = potential_buyers[can_buy]
    actual_prices = potential_prices[can_buy]
    agent_food_stock[actual_buyers] += 1
    agent_money[actual_buyers] -= actual_prices
    np.add.at(
        business_revenue, actual_sellers, actual_prices)
    np.add.at(sales_inventory, actual_sellers, -1)
units_sold_per_business = np.bincount(
    actual_sellers, actual_prices, minlength=total_businesses)
urgency2 = np.maximum(0, 1-agent_health_bar)
medical_money_per_agent = agent_money*urgency2
total_money_in_field[5] = np.sum(medical_money_per_agent)
money_taken_by_comp = np.bincount(
    business_field_id, business_revenue, minlength=len(fields))
money_taken_by_comp = np.clip(money_taken_by_comp, 1e-9, None)
available_money_in_field = total_money_in_field - money_taken_by_comp
sector_totals = money_taken_by_comp[business_field_id]
total_money_in_field = np.clip(total_money_in_field, 1e-9, None)
opportunity = available_money_in_field/total_money_in_field
market_share = business_revenue/sector_totals
