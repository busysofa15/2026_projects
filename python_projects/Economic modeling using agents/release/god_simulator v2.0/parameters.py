import numpy as np
##for predefined array
no_of_agents = 10000
no_of_businesses = no_of_agents
no_of_tech_businesses = no_of_agents
starting_alive_agents = 100
starting_alive_money = 1000
inventory_storage = 20
no_of_inventory_buildings_available = 100
metabolism = 0.7
starting_food = 5
tax_ratio = 0.1
seed_capital_ratio = 0.5
rot_percentage = 0.1
rot_ratio = (1-rot_percentage)
tech_investment_ratio = 0.9
age_step = 1
NUM_DAYS = 1000
STEP = 10
unemployed_id = np.int32(no_of_businesses)
##SENSITIVITY TO INVENTORY_CHANGES
k = 1.0
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
agri_biz_count = np.zeros(NUM_DAYS, dtype=np.int32)
tech_biz_count = np.zeros(NUM_DAYS, dtype=np.int32)

rng = np.random.default_rng()