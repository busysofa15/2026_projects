from __future__ import annotations
import numpy as np
from parameters import *
from agents import *
class business_data:
    def __init__(self,sectors):
        self.business_money = np.full(no_of_businesses,10000,dtype=np.float32)
        self.business_id = np.arange(no_of_businesses,dtype=np.int32)
        self.business_is_active = np.zeros(no_of_businesses, dtype=bool)
        self.business_owner = np.full(no_of_businesses,-1,dtype=np.int32)
        self.selling_price = np.full(no_of_businesses,sectors.base_tech_price, dtype=np.float32)
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
    def tick(self, agents):
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
        self.profit_margin = np.clip(target_markup, 0.05 ,1000) 
        self.selling_price = self.production_cost_per_item * (1.0 + self.profit_margin)
        self.selling_price = np.maximum(1.0, self.selling_price).astype(np.float32)
        self.sorted_selling_price = np.argsort(self.selling_price)
        self.sorted_selling_price_id = self.business_id[self.sorted_selling_price]
        self.sorted_items_to_be_sold = self.items_to_be_sold[self.sorted_selling_price_id]
        self.global_market = np.repeat(self.sorted_selling_price_id,self.sorted_items_to_be_sold)
        self.profits = np.float32(self.daily_revenue - self.money_to_be_subtracted_from_business)
        self.money_assigned_to_tech = np.maximum(0.0, np.float32(tech_investment_ratio * self.profits))