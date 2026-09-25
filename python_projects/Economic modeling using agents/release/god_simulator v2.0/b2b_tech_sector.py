from __future__ import annotations
import numpy as np
from parameters import *
from agents import *
from sectors_and_tick import *
class tech_biz_data:
    def __init__(self,sectors: "sector_data"):
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
        self.daily_revenue = np.zeros(no_of_tech_businesses,dtype=np.float32)
    def tick (self,agents:"agent_data"):
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
        self.profits = np.float32(self.daily_revenue - self.operational_costs)
        self.tech_market = np.repeat(self.sorted_selling_id,self.sorted_items_to_be_sold)