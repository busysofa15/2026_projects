import numpy as np
import plotly.graph_objects as pg
import streamlit as st
import pandas as pd
N_AGENTS = 100000
land = np.array([5000, 1000, 500, 200, 300])
base_cost_land = np.array([100, 120, 200, 150, 130])
unitsproducedandpopulationdenisty = np.array([1, 4, 10, 1, 1])
power_plant_power = 100
agent_metabolism = 0.2
agent_talent = np.random.normal(loc=1, scale=0.2, size=N_AGENTS)
rng = np.random.default_rng()
fields = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
# 0 = agri 2 = mining 3= manufacturing 4 = venture capitals 5 = transport 6 = transport 7 = tech 8 = medical
# 9 = construction
agents_alive = np.zeros(N_AGENTS)
agents_alive[:100] = 1
total_alive = np.sum(agents_alive).astype(int)
is_working_age = np.zeros(total_alive)
is_working_age[:100] = 1
total_no_of_working_age = np.sum(is_working_age).astype(int)
working_age_id = np.arange(total_no_of_working_age)
agent_id = np.arange(N_AGENTS)
government_id = 101


agent_business_sectorspawning = np.random.randint(
    0, 10, size=total_no_of_working_age)
p_business = 0.5
p_agent_starting_business = rng.random(total_no_of_working_age)
business_started = (p_agent_starting_business < p_business)
business_field_id = agent_business_sectorspawning[business_started]
total_businesses = np.sum(business_started)
business_id = np.arange(total_businesses)
business_owner_id = working_age_id[business_started]
medical_price = (1e-9)
food_price = np.random.normal(
    loc=100, scale=4, size=total_businesses)
money_recieved_by_market = (1e-9)
money_by_everyone = (1e-9)
agent_wages = np.random.normal(loc=200, scale=50, size=total_no_of_working_age)
agent_money = agent_wages
employed_id = np.zeros(total_no_of_working_age, dtype=int)
agent_food_stock = np.zeros(total_no_of_working_age)
agent_food_stock -= agent_metabolism
want_buy_food = (agent_food_stock <= 0.4)
# buying
business_inventory = np.random.normal(
    loc=10, scale=3, size=total_businesses).astype(int)
business_revenue = np.zeros(total_businesses)
stock_available = (business_inventory > 0)
sorted_businesses = np.argsort(food_price[stock_available])
unit_prices = np.repeat(food_price, business_inventory)
total_food_available = len(unit_prices)
potential_buyers = np.where(want_buy_food)[0]
random_buyers = min(total_food_available, len(potential_buyers))
unit_sellers = np.repeat(business_id, business_inventory)
if random_buyers > 0:
    market_participants = rng.choice(
        potential_buyers, size=random_buyers, replace=False)
else:
    market_participants = np.array([])
n_sales = min(len(market_participants), len(unit_prices))
if n_sales > 0:
    potential_sellers = unit_sellers[:n_sales]
    potential_buyers = market_participants[:n_sales]
    potential_prices = unit_prices[:n_sales]
    can_buy = (agent_money[potential_buyers] >= potential_prices)
    actual_sellers = potential_sellers[can_buy]
    actual_buyers = potential_buyers[can_buy]
    actual_prices = potential_prices[can_buy]
    agent_food_stock[actual_buyers] += 1
    agent_money[actual_buyers] -= actual_prices
    np.add.at(
        business_revenue, actual_sellers, actual_prices)
    np.add.at(business_inventory, actual_sellers, -1)
    print(np.sum(business_revenue))
total_money_in_field = np.bincount(fields, weights=money_by_everyone)
money_taken_by_comp = money_recieved_by_market
available_money_in_field = total_money_in_field - money_taken_by_comp
opportunity = available_money_in_field/total_money_in_field
