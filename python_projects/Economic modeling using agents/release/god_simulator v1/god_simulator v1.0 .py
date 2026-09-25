import time
import numpy as np
import matplotlib.pyplot as plt  
##for predefined array
no_of_agents = 1000
no_of_businesses = no_of_agents
no_of_tech_businesses = no_of_agents
starting_alive_agents = 100
inventory_storage = 20
no_of_inventory_buildings_available = 100
metabolism = 0.2
starting_food = 5
tax_ratio = 0
rot_percentage = 0.1
rot_ratio = (1-rot_percentage)
tech_investment_ratio = 0.9
age_step = 1
NUM_DAYS = 1000
STEP = 1
unemployed_id = np.int32(no_of_businesses)
##SENSITIVITY TO INVENTORY_CHANGES
k = 0.1

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

class agent_data:
    def __init__(self):
        self.id = np.arange(no_of_agents, dtype=np.int32)
        self.money = np.zeros(no_of_agents,dtype = np.float32)
        self.money[:starting_alive_agents] = np.float32(300)
        self.alive = np.zeros(no_of_agents, dtype=bool)
        self.alive[:starting_alive_agents] = True
        self.age = np.zeros(no_of_agents, dtype=np.float32)
        self.age[:starting_alive_agents] = np.float32(18)
        self.employed = np.zeros(no_of_agents, dtype=bool)
        self.employed_in_tech = np.zeros(no_of_agents,dtype=bool)
        self.employer_id = np.full(no_of_agents, unemployed_id, dtype=np.int32)
        self.tech_employer_id = np.full(no_of_agents, unemployed_id, dtype=np.int32)
        self.talent = np.random.normal(loc=0.7,scale=0.05, size=no_of_agents).astype(np.float32)
        self.talent = np.clip(self.talent,0.2,2)
        self.food_stock = rng.random(no_of_agents,dtype=np.float32)
        self.food_stock += starting_food
        self.business_spawning_probability_per_agent = np.empty(no_of_agents, dtype=np.float32)
        # METABOLISM CRUCIAALLL FEATUREEEE IN CASE U WANNA FW ECONOMY
        self.metabolism = metabolism
        self.productivity = np.empty(no_of_agents, dtype=np.float32)
        self.money_spent_on_food = np.empty(no_of_agents,dtype=np.float32)
        self.food_urgency = np.empty(no_of_agents,dtype=np.float32)
        self.business_starts_successfully = np.zeros(no_of_agents, dtype=bool)
        self.tech_business_starts_succesfully = np.zeros(no_of_agents,dtype=bool)
        self.items_produced_per_agent = np.empty(no_of_agents,dtype=np.float32)   
        self.penalty_ticks = np.zeros(no_of_agents,dtype=np.int32)
        self.agents_wages = np.zeros(no_of_agents,dtype=np.float32)
        self.mean_price = np.float32(0)
        self.minimum_wages_amt = np.float32(120)
    def tick(self,sectors,business_info):
        rng.standard_normal(out=self.productivity, dtype=np.float32)
        self.productivity *= np.float32(0.05)  #  standard deviation
        self.productivity += np.float32(1)  #  mean
        np.clip(self.productivity,0.1,21.1,out=self.productivity)
        self.business_spawning_probability = 0.1*sectors.opportunity_of_agriculture_sector
        self.alive_agents_mask = (self.alive == True)
        self.food_stock[self.alive_agents_mask] -= metabolism
        self.food_stock = np.maximum(0.0, self.food_stock)
        self.working_age_mask = (self.age >= 18) & (self.age <= 65)
        tech_rolls = rng.random(no_of_agents, dtype=np.float32)
        rng.random(out=self.business_spawning_probability_per_agent, dtype=np.float32)
        self.business_starts_successfully = (self.business_spawning_probability_per_agent
            < self.business_spawning_probability)&(self.money > 3*self.agents_wages)&(self.working_age_mask)
        self.business_starts_successfully[~self.alive_agents_mask] = False
        self.business_spawning_probability_per_agent[self.business_starts_successfully] = np.float32(0)
        self.tech_biz_spawning_probability = np.float32(sectors.opportunity_tech_sector)
        self.tech_business_starts_succesfully = (tech_rolls < self.tech_biz_spawning_probability)&(self.money > 3*self.agents_wages)&(self.working_age_mask)
        self.tech_business_starts_succesfully[~self.alive] = False
        self.agents_wages.fill(0.0)
        self.recent_starvations = np.sum((self.food_stock <= 0) & self.alive)
        self.dead_mask = (self.age>80 )|(self.food_stock <= 0)
        self.productivity = np.clip(self.productivity,0.1, 2.5)
        self.age[self.alive_agents_mask] += np.float32(age_step)
        self.alive[self.dead_mask] = False
        sectors.global_bank_money+= np.float32(np.sum(self.money[self.dead_mask]))
        self.money[self.dead_mask] = np.float32(0)
        self.employed[self.dead_mask] = False
        self.employed_in_tech[self.dead_mask] = False
        self.age[self.dead_mask] = np.float32(0)
        self.employer_id[self.dead_mask] = unemployed_id
        self.tech_employer_id[self.dead_mask] = unemployed_id
        self.food_stock[self.dead_mask] = np.float32(1)
        active_mask = business_info.business_is_active
        self.mean_price = np.mean(business_info.selling_price[active_mask]) if np.any(active_mask) else sectors.base_price
        self.minimum_wages_smoothed = np.float32(0.75*self.minimum_wages_amt+0.25*self.mean_price)
        self.minimum_wages_amt = np.float32(self.minimum_wages_smoothed * metabolism * 1)
        self.minimum_wages = np.full(no_of_agents,self.minimum_wages_amt,dtype = np.float32)
        self.minimum_wages = np.maximum(self.minimum_wages, 1.0)
        np.multiply(self.talent,self.productivity,out=self.items_produced_per_agent)
        np.subtract(5, self.food_stock, dtype=np.float32, out=self.food_urgency)
        self.money_spent_on_food = self.food_urgency * self.mean_price
        self.money_spent_on_food = np.maximum(0, self.money_spent_on_food)
        self.money_spent_on_food = np.minimum(self.money, self.money_spent_on_food)
        self.dead_slots = np.where(~self.alive)[0]
        if len(self.dead_slots) > 0:
            self.parent_mask = ((self.money > (np.float32(3*self.minimum_wages))) & (self.food_stock > 5)
            &(self.penalty_ticks == 0)&(self.age> (18+(10/365)))&(self.age<50))
            self.potential_parents = np.where(self.parent_mask)[0]
            if len(self.potential_parents)>0:
                self.potential_parents = rng.permutation(self.potential_parents)
                self.no_of_births = min(len(self.potential_parents),len(self.dead_slots))
                self.chosen_parents = self.potential_parents[:self.no_of_births]
                self.assigned_slots = self.dead_slots[:self.no_of_births]
                self.alive[self.assigned_slots] = True
                self.age[self.assigned_slots] = np.float32(0.0)
                self.food_stock[self.assigned_slots] = np.float32(5.0)
                self.employed[self.assigned_slots] = False
                self.employer_id[self.assigned_slots] = unemployed_id
                self.tech_employer_id[self.assigned_slots] = unemployed_id
                self.money[self.assigned_slots] += np.float32(0.2*self.money[self.chosen_parents])
                self.money[self.chosen_parents] -= np.float32(0.2*self.money[self.chosen_parents])
                self.penalty_ticks[self.chosen_parents] = np.int32(18*(1/age_step))
        self.are_parents_mask = (self.penalty_ticks > 0)&(self.alive)
        self.penalty_ticks[self.are_parents_mask] -= np.int32(1)
        self.minimum_wages[self.are_parents_mask] *= np.float32(1.5)
        self.child_mask = (self.age<18)&(self.alive)
        self.child_id = self.id[self.child_mask]
        self.are_almost_not_parents = (self.penalty_ticks == 1)
        self.minimum_wages[self.are_almost_not_parents] *= np.float32(1/2)
        if (np.sum(self.child_mask)>0) and (np.sum(self.are_parents_mask)>0):
            self.possible_transfers = min(np.sum(self.child_mask),np.sum(self.are_parents_mask))
            self.child_id = rng.permutation(self.child_id)
            self.random_parent = rng.permutation(self.id[self.are_parents_mask])
            self.final_child_id = self.child_id[:self.possible_transfers]
            self.final_parent_id = self.random_parent[:self.possible_transfers]
            self.money_to_be_transferred = (self.mean_price)*(self.food_urgency[self.final_child_id])
            self.money_to_be_transferred = np.maximum(0,self.money_to_be_transferred)
            self.money_to_be_transferred = np.minimum(self.money[self.final_parent_id],self.money_to_be_transferred)
            self.money[self.final_child_id] += self.money_to_be_transferred
            self.money[self.final_parent_id] -= self.money_to_be_transferred
               
class business_data:
    def __init__(self):
        self.business_money = np.full(no_of_businesses,10000,dtype=np.float32)
        self.business_id = np.arange(no_of_businesses,dtype=np.int32)
        self.business_is_active = np.zeros(no_of_businesses, dtype=bool)
        self.business_owner = np.full(no_of_businesses,-1,dtype=np.int32)
        self.selling_price = np.full(no_of_businesses,sectors.base_price, dtype=np.float32)
        self.inventory_buildings_per_business = np.ones(no_of_businesses,dtype=np.int16)
        self.inventory = np.zeros(no_of_businesses,dtype=np.int32)
        self.items_produced_raw = np.zeros(no_of_businesses,dtype=np.float32)
        self.target_no_of_ppl_to_hire = np.zeros(no_of_businesses,dtype=np.int32)
        self.items_sold = np.zeros(no_of_businesses,dtype=np.int32)
        self.items_to_be_sold = np.zeros(no_of_businesses,dtype=np.int32)
        self.items_not_sold = np.zeros(no_of_businesses,dtype=np.int32)
        self.no_of_employees = np.zeros(no_of_businesses,dtype=np.int32)
        self.no_of_tech_units_brought = np.zeros(no_of_businesses,dtype=np.int32)
        self.daily_revenue = np.zeros(no_of_businesses,dtype=np.float32)
        self.global_market = np.array([], dtype=np.int32)
        self.money_assigned_to_tech = np.zeros(no_of_businesses,dtype=np.float32)
    def tick(self, agents: agent_data):
        self.business_needs_money = (self.business_money == 0)
        self.inventory_capacity = self.inventory_buildings_per_business*inventory_storage
        self.business_is_active[agents.business_starts_successfully] = True
        self.sold_out_mask = (self.business_money > 0)&(self.business_is_active)&(self.items_sold == self.items_to_be_sold)&(self.items_to_be_sold>0)
        self.new_biz_mask = (self.items_to_be_sold == 0)
        self.businesses_who_want_to_hire_mask = (
         self.business_is_active & 
         (self.new_biz_mask | self.sold_out_mask) & 
         (self.business_money > 0)
         )
        self.hire_mask = (agents.alive)&(~agents.employed)&(agents.working_age_mask)&(~agents.employed_in_tech)
        self.valid_ids = agents.id[self.hire_mask]
        self.valid_ids = rng.permutation(self.valid_ids)
        self.target_no_of_ppl_to_hire[self.businesses_who_want_to_hire_mask] = np.int32(np.ceil((1/20)*self.no_of_employees[self.businesses_who_want_to_hire_mask]))
        self.target_no_of_ppl_to_hire[self.businesses_who_want_to_hire_mask] = np.maximum(1,self.target_no_of_ppl_to_hire[self.businesses_who_want_to_hire_mask])
        self.target_no_of_ppl_to_hire = np.maximum(0, np.int32(np.nan_to_num(self.target_no_of_ppl_to_hire, nan=0.0)))
        np.minimum(self.target_no_of_ppl_to_hire,len(self.valid_ids),out=self.target_no_of_ppl_to_hire)
        self.business_ids_who_hired_agents= np.repeat(self.business_id,self.target_no_of_ppl_to_hire)
        self.assigned_workers = self.valid_ids[:len(self.business_ids_who_hired_agents)]
        self.business_ids_who_hired_agents = rng.permutation(self.business_ids_who_hired_agents)
        self.business_ids_who_hired_agents = self.business_ids_who_hired_agents[:len(self.assigned_workers)]
        agents.employer_id[self.assigned_workers] = self.business_ids_who_hired_agents
        agents.employed[self.assigned_workers] = True
        self.individual_wages =  (agents.minimum_wages[agents.employed])*(agents.talent[agents.employed])
        self.money_to_be_subtracted_from_business = np.bincount(agents.employer_id[agents.employed], weights=self.individual_wages, minlength=no_of_businesses)[:no_of_businesses]
        self.businesses_who_gonna_explode = self.business_id[(self.money_to_be_subtracted_from_business>self.business_money)]
        self.workers_to_fire_mask = np.isin(agents.employer_id, self.businesses_who_gonna_explode)
        agents.employed[self.workers_to_fire_mask] = False
        agents.employer_id[self.workers_to_fire_mask] = unemployed_id
        self.too_much_inventory_mask = (self.inventory > 2 * self.items_sold) & self.business_is_active
        self.workers_to_fire_mask = np.isin(agents.employer_id, self.business_id[self.too_much_inventory_mask])
        agents.employed[self.workers_to_fire_mask] = False
        agents.employer_id[self.workers_to_fire_mask] = unemployed_id
        self.money_to_be_subtracted_from_business[self.businesses_who_gonna_explode] = np.float32(0)
        self.no_of_employees = np.bincount(agents.employer_id,minlength=no_of_businesses+1)
        self.no_of_employees = self.no_of_employees[:no_of_businesses]
        self.business_with_no_employees = (self.no_of_employees == 0)
        self.business_is_active[self.business_with_no_employees] = False
        self.dead_mask = (self.business_money <= 0)
        self.business_is_active[self.dead_mask] = False
        self.individual_wages = (agents.minimum_wages[agents.employed]) * (agents.talent[agents.employed])
        agents.money[agents.employed] += self.individual_wages
        agents.agents_wages[agents.employed] += self.individual_wages
        self.items_produced_raw = np.bincount(agents.employer_id[agents.employed],weights=agents.items_produced_per_agent[agents.employed],minlength=no_of_businesses)[:no_of_businesses]
        self.items_produced = np.maximum(1, np.int32(np.ceil(self.items_produced_raw)))
        self.tech_units_brought_mask = (self.no_of_tech_units_brought>0)
        self.items_produced[self.tech_units_brought_mask] *= np.int32(10*self.no_of_tech_units_brought[self.tech_units_brought_mask])
        self.no_of_tech_units_brought.fill(0)
        self.production_cost_per_item = np.where(
            self.items_produced > 0,
            self.money_to_be_subtracted_from_business / self.items_produced,
            0.0
        ).astype(np.float32)
        self.production_cost_per_item = np.nan_to_num(self.production_cost_per_item, nan=0.0)
        self.business_money -= self.money_to_be_subtracted_from_business
        self.inventory += self.items_produced
        self.inventory = (self.inventory * rot_ratio).astype(np.int32) 
        self.inventory = np.maximum(0, self.inventory)
        self.items_to_be_sold = np.copy(self.inventory)
        self.velocity_ratio = np.float32(self.items_sold / (self.items_not_sold + 1))
        target_markup = k * (self.velocity_ratio - 1.0)
        self.profit_margin = np.clip(target_markup, 0.25 , 1) 
        self.selling_price = self.production_cost_per_item * (1.0 + self.profit_margin)
        self.selling_price = np.maximum(1.0, self.selling_price).astype(np.float32)
        self.sorted_selling_price = np.argsort(self.selling_price)
        self.sorted_selling_price_id = self.business_id[self.sorted_selling_price]
        self.sorted_items_to_be_sold = self.items_to_be_sold[self.sorted_selling_price_id]
        self.global_market = np.repeat(self.sorted_selling_price_id,self.sorted_items_to_be_sold)
        self.profits = np.float32(self.daily_revenue - self.money_to_be_subtracted_from_business)
        self.money_assigned_to_tech = np.maximum(0.0, np.float32(tech_investment_ratio * self.profits))
        self.money_assigned_to_tech = np.minimum(0,self.money_assigned_to_tech)
class tech_biz_data:
    def __init__(self):
        self.business_money = np.full(no_of_tech_businesses,10000,dtype=np.float32)
        self.business_id = np.arange(no_of_tech_businesses,dtype=np.int32)
        self.inventory = np.zeros(no_of_tech_businesses, dtype=np.int32)
        self.business_is_active = np.zeros(no_of_tech_businesses,dtype=bool)
        self.selling_price = np.zeros(no_of_tech_businesses,dtype=np.float32)
        self.target_hires = np.zeros(no_of_tech_businesses,dtype = np.int32)
        self.items_sold = np.zeros(no_of_tech_businesses,dtype=np.int32)
        self.items_not_sold = np.zeros(no_of_tech_businesses,dtype=np.int32)
        self.items_to_be_sold = np.zeros(no_of_tech_businesses,dtype=np.int32)
        self.target_no_of_ppl_to_hire = np.zeros(no_of_tech_businesses,dtype=np.int32)
        self.no_of_employees = np.zeros(no_of_tech_businesses,dtype=np.int32)
        self.selling_price = np.full(no_of_tech_businesses,sectors.base_tech_price,dtype=np.float32)
        self.tech_market = np.array([], dtype=np.int32)
    def tick (self,agents:agent_data):
        self.business_is_active[agents.tech_business_starts_succesfully] = True
        self.sold_out_mask = (self.business_money > 0)&(self.business_is_active)&(self.items_sold == self.items_to_be_sold)&(self.items_to_be_sold>0)
        self.new_biz_mask = (self.items_to_be_sold == 0)
        self.businesses_who_want_to_hire_mask = (
                self.business_is_active & 
            (self.new_biz_mask | self.sold_out_mask) & 
            (self.business_money > 0)
            )
        self.hiring_mask = (~agents.employed)&(~agents.employed_in_tech)&(agents.working_age_mask)
        self.valid_id = agents.id[self.hiring_mask]
        self.available_agents = np.sum(agents.alive[self.valid_id])
        self.target_no_of_ppl_to_hire[self.businesses_who_want_to_hire_mask] = np.int32(np.ceil((1/5)*self.no_of_employees[self.businesses_who_want_to_hire_mask]))
        self.target_no_of_ppl_to_hire[self.businesses_who_want_to_hire_mask] = np.maximum(5,self.target_no_of_ppl_to_hire[self.businesses_who_want_to_hire_mask])
        self.target_no_of_ppl_to_hire = np.maximum(0, np.int32(np.nan_to_num(self.target_no_of_ppl_to_hire, nan=0.0)))
        np.minimum(self.target_no_of_ppl_to_hire,len(self.valid_id),out=self.target_no_of_ppl_to_hire)
        if (self.available_agents>0) and (np.sum(self.target_no_of_ppl_to_hire)>0):
            self.valid_id = rng.permutation(self.valid_id)
            self.valid_biz_id = rng.permutation(self.business_id[self.businesses_who_want_to_hire_mask])
            self.biz_id_to_be_assigned = np.repeat(self.valid_biz_id,self.target_no_of_ppl_to_hire[self.valid_biz_id])
            self.valid_length = min(self.available_agents,len(self.biz_id_to_be_assigned))
            self.hired_id = self.valid_id[:self.valid_length]
            self.biz_id_to_be_assigned = self.biz_id_to_be_assigned[:self.valid_length]
            agents.tech_employer_id[self.hired_id] = self.biz_id_to_be_assigned
            agents.employed_in_tech[self.hired_id] = True
        self.no_of_employees = np.bincount(agents.tech_employer_id[agents.employed_in_tech],minlength=no_of_businesses)[:no_of_tech_businesses]
        self.individual_wages =  (agents.minimum_wages[agents.employed_in_tech])*(agents.talent[agents.employed_in_tech])
        self.operational_costs = np.bincount(agents.tech_employer_id[agents.employed_in_tech],weights=self.individual_wages,minlength=no_of_businesses)[:no_of_tech_businesses]
        self.business_is_dead_mask = (self.no_of_employees == 0)
        self.business_is_active[self.business_is_dead_mask] = False
        self.biz_is_gonna_explode_mask = (self.operational_costs>self.business_money)
        self.biz_is_gonna_explode = self.business_id[self.biz_is_gonna_explode_mask]
        self.agents_fire_mask = np.isin(agents.tech_employer_id,self.biz_is_gonna_explode)
        agents.tech_employer_id[self.agents_fire_mask] = unemployed_id
        agents.employed_in_tech[self.agents_fire_mask] = False
        self.items_produced_raw = np.bincount(agents.tech_employer_id[agents.employed_in_tech],weights=agents.items_produced_per_agent[agents.employed_in_tech],minlength=no_of_businesses)[:no_of_tech_businesses]
        self.items_produced_raw = self.items_produced_raw*(1/5)
        self.items_produced = np.maximum(1, np.int32(np.ceil(self.items_produced_raw)))
        self.production_cost_per_item = np.where(
         self.items_produced > 0,
            self.operational_costs / self.items_produced,
             0.0
            ).astype(np.float32)
        self.individual_wages = (agents.minimum_wages[agents.employed_in_tech]) * (agents.talent[agents.employed_in_tech])
        agents.money[agents.employed_in_tech] += self.individual_wages
        agents.agents_wages[agents.employed_in_tech] += self.individual_wages
        self.production_cost_per_item = np.nan_to_num(self.production_cost_per_item, nan=0.0)
        self.business_money -= self.operational_costs
        self.inventory += self.items_produced
        self.inventory = np.maximum(0, self.inventory)
        self.items_to_be_sold = np.copy(self.inventory)
        self.velocity_ratio = np.float32(self.items_sold / (self.items_not_sold + 1))
        target_markup = k * (self.velocity_ratio - 1.0)
        self.profit_margin = np.clip(target_markup, 0.25, 1.0)
        self.selling_price = self.production_cost_per_item * (1.0 + self.profit_margin)
        self.selling_price = np.maximum(1.0, self.selling_price).astype(np.float32)
        self.sorted_selling_price = np.argsort(self.selling_price)
        self.sorted_selling_id = self.business_id[self.sorted_selling_price]
        self.sorted_items_to_be_sold = self.items_to_be_sold[self.sorted_selling_id]
        self.tech_market = np.repeat(self.sorted_selling_id,self.sorted_items_to_be_sold)
class sector_data:
    def __init__(self):
         self.opportunity_of_agriculture_sector = np.float32(0)
         self.opportunity_tech_sector = np.float32(0)
         self.base_price = np.float32(100)
         self.base_tech_price = np.float32(1200)
         self.global_bank_money = np.float32(0)
         self.total_transactions = np.float32(0)
         self.tech_transactions = np.float32(0)
         self.ubi_bank_money = np.float32(100000)
    def tick(self,agents:agent_data,business_info:business_data):
         self.total_transactions = np.float32(0)
         self.potential_customers_mask= (agents.alive)&(agents.food_stock<5)
         self.potential_customers_id = agents.id[self.potential_customers_mask]
         self.potential_customers_id = rng.permutation(self.potential_customers_id)
         self.possible_transactions = min(len(self.potential_customers_id),len(business_info.global_market))
         self.potential_market = business_info.global_market[:self.possible_transactions]
         self.potential_customers_id = self.potential_customers_id[:self.possible_transactions]
         business_info.items_sold.fill(0)
         business_info.daily_revenue.fill(0)
         if (len(self.potential_customers_id) >0) and (len(self.potential_market)>0):
            self.item_prices = business_info.selling_price[self.potential_market]
            self.afford_mask = (agents.money[self.potential_customers_id] >= self.item_prices)
            self.final_customers = self.potential_customers_id[self.afford_mask]
            self.final_market = self.potential_market[self.afford_mask]
            self.final_prices = self.item_prices[self.afford_mask]
            if (len(self.final_customers)>0) and (len(self.final_market)>0):
                agents.money[self.final_customers] -= self.final_prices
                np.add.at(business_info.business_money,self.final_market,self.final_prices)
                np.add.at(business_info.daily_revenue,self.final_market,self.final_prices)
                np.add.at(business_info.inventory,self.final_market, -1)
                np.add.at(business_info.items_sold,self.final_market,1)
                agents.food_stock[self.final_customers] += 1
                self.total_transactions = np.sum(self.final_prices)
         business_info.items_not_sold = np.maximum(0, business_info.items_to_be_sold - business_info.items_sold)
         self.opportunity_of_agriculture_sector = np.float32(1) - (((np.sum(self.total_transactions))/(np.sum(agents.money_spent_on_food)+1)))
         self.opportunity_of_agriculture_sector = np.clip(self.opportunity_of_agriculture_sector,0,1)
         self.newly_active_mask = agents.business_starts_successfully
         self.new_biz_count = np.sum(self.newly_active_mask)
         if (self.new_biz_count > 0 )and (self.global_bank_money > 0):
             seed_capital = np.float32((self.global_bank_money/2) / self.new_biz_count)
             business_info.business_money[self.newly_active_mask] += seed_capital
             self.global_bank_money *= np.float32(1/2)
         self.newly_active_tech_mask = agents.tech_business_starts_succesfully
         self.new_tech_biz_count = np.sum(self.newly_active_tech_mask)
         if (self.new_tech_biz_count > 0 )and (self.global_bank_money > 0):
            seed_capital_tech = np.float32((self.global_bank_money) / self.new_tech_biz_count)
            business_info.business_money[self.newly_active_tech_mask] += seed_capital_tech
            self.global_bank_money = np.float32(0) 
         self.taxable_mask = (agents.employed)&(agents.alive)&(agents.working_age_mask)
         self.taxable_amt = tax_ratio*(agents.agents_wages[self.taxable_mask])
         agents.money[self.taxable_mask] -= self.taxable_amt
         self.ubi_bank_money += np.sum(self.taxable_amt)
         self.agents_need_ubi_mask = (~agents.employed)&(agents.alive)&(agents.age > 18)&(~agents.employed_in_tech)
         self.agents_need_ubi_count = np.sum(self.agents_need_ubi_mask)
         if (self.agents_need_ubi_count>0) and (self.ubi_bank_money > 0):
             self.money_to_be_distributed = ((self.ubi_bank_money/10)/(self.agents_need_ubi_count))
             agents.money[self.agents_need_ubi_mask] += self.money_to_be_distributed
             self.amt_to_be_reduced = (self.agents_need_ubi_count*self.money_to_be_distributed)
             self.ubi_bank_money -= self.amt_to_be_reduced 
    def tick_tech (self,business_info:business_data,tech:tech_biz_data):
        self.potential_biz_customers_mask = (business_info.business_is_active)
        self.potential_biz_customers = business_info.business_id[self.potential_biz_customers_mask]
        self.potential_biz_customers = rng.permutation(self.potential_biz_customers)
        self.potential_tech_market  = tech.tech_market
        self.viable_count = min(np.sum(self.potential_biz_customers_mask),len(self.potential_tech_market))
        self.potential_biz_customers = self.potential_biz_customers[:self.viable_count]
        self.potential_tech_market = self.potential_tech_market[:self.viable_count]
        tech.items_sold.fill(0)
        tech.items_sold.fill(0)
        if (np.sum(self.potential_biz_customers_mask)>0) and (len(self.potential_tech_market)>0):
            self.tech_item_prices = tech.selling_price[self.potential_tech_market]
            self.afford_tech_mask = ((business_info.business_money[self.potential_biz_customers])>self.tech_item_prices)
            self.final_biz_customers = self.potential_biz_customers[self.afford_tech_mask]
            self.final_tech_market = self.potential_tech_market[self.afford_tech_mask]
            self.final_tech_price = self.tech_item_prices[self.afford_tech_mask]
            if (len(self.final_biz_customers)>0) and (len(self.final_tech_market)>0):
                business_info.business_money[self.final_biz_customers] -= self.final_tech_price
                np.add.at(tech.business_money,self.final_tech_market,self.final_tech_price)
                np.add.at(tech.inventory,self.final_tech_market,-1)
                np.add.at(tech.items_sold,self.final_tech_market,1)
                np.add.at(business_info.no_of_tech_units_brought, self.final_biz_customers, 1)
                self.tech_transactions = np.sum(self.final_tech_price)
        tech.items_not_sold = np.maximum(0,(tech.items_to_be_sold - tech.items_sold))
        self.opportunity_tech_sector = 1 - (self.tech_transactions/((np.sum(business_info.money_assigned_to_tech))+1))
        


class simulation_tick:
    def __init__(self):
        self.business_info = business_data()
        self.tech = tech_biz_data()
        self.sectors = sector_data()
        self.agents = agent_data()

sectors = sector_data()
agents = agent_data()
business_info = business_data()
tech = tech_biz_data()
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
    agri_biz_count[day] = np.sum(business_info.business_is_active)
    tech_biz_count[day] = np.sum(tech.business_is_active)
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

axes[2, 2].plot(days_x, agri_biz_count[::STEP], label='Agri Biz', color='tab:green')
axes[2, 2].plot(days_x, tech_biz_count[::STEP], label='Tech Biz', color='tab:purple')
axes[2, 2].set_title("Active Businesses")
axes[2, 2].legend()
axes[2, 2].grid(True)

plt.tight_layout()
plt.show()
