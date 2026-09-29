from __future__ import annotations
import numpy as np
from parameters import *
from agents import *
from sectors_and_tick import *
from firing_logic_rehaul import process_firings_rust
class secondary_goods_and_services:
    def __init__(self,sectors: "sector_data"):
        self.business_money = np.full(no_of_tech_businesses,500,dtype=np.float32)
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
        self.selling_price = np.full(no_of_tech_businesses,sectors.base_secondary_goods_and_services_price,dtype=np.float32)
        self.secondary_goods_and_services_market = np.array([], dtype=np.int32)
        self.daily_revenue = np.zeros(no_of_tech_businesses,dtype=np.float32)
        self.no_of_fires_raw = np.zeros(no_of_businesses,dtype=np.float32)
        self.no_of_fires = np.zeros(no_of_businesses,dtype=np.int32)
    def tick (self,agents:"agent_data"):
        self.business_is_active[agents.secondary_services_and_goods_businesses_spawned_successfully] = True
        self.sold_out_mask = (self.business_money > 0)&(self.business_is_active)&(self.items_sold == self.items_to_be_sold)&(self.items_to_be_sold>0)
        self.new_biz_mask = (self.items_to_be_sold == 0)
        self.businesses_who_want_to_hire_mask = (
                self.business_is_active & 
            (self.new_biz_mask | self.sold_out_mask) & 
            (self.business_money > 0)
            )
        self.hiring_mask = (~agents.employed)&(~agents.employed_in_tech)&(agents.working_age_mask)&(~agents.employed_in_secondary_services_and_goods)
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
            agents.secondary_services_and_goods_id[self.hired_id] = self.biz_id_to_be_assigned
            agents.employed_in_secondary_services_and_goods[self.hired_id] = True
        self.no_of_employees = np.bincount(agents.secondary_services_and_goods_id[agents.employed_in_secondary_services_and_goods],minlength=no_of_businesses)[:no_of_tech_businesses]
        self.individual_wages =  (agents.minimum_wages[agents.employed_in_secondary_services_and_goods])*(agents.talent[agents.employed_in_secondary_services_and_goods])
        self.operational_costs = np.bincount(agents.secondary_services_and_goods_id[agents.employed_in_secondary_services_and_goods],weights=self.individual_wages,minlength=no_of_businesses)[:no_of_tech_businesses]
        self.business_is_dead_mask = (self.no_of_employees == 0)
        self.business_is_active[self.business_is_dead_mask] = False
        self.no_of_employees[self.business_is_dead_mask] = 0
        self.biz_is_gonna_explode_mask = (self.operational_costs>self.business_money)
        self.biz_is_gonna_explode = self.business_id[self.biz_is_gonna_explode_mask]
        self.agents_fire_mask = np.isin(agents.secondary_services_and_goods_id,self.biz_is_gonna_explode)
        if np.sum(self.biz_is_gonna_explode_mask) > 0:
            self.no_of_fires_raw[self.biz_is_gonna_explode_mask] = np.float32((self.operational_costs[self.biz_is_gonna_explode_mask] - self.business_money[self.biz_is_gonna_explode_mask])/np.mean(self.individual_wages))
            self.no_of_fires[self.biz_is_gonna_explode_mask] = np.int32(np.ceil(self.no_of_fires_raw[self.biz_is_gonna_explode_mask]))
            process_firings_rust(agents.secondary_services_and_goods_id,self.biz_is_gonna_explode.tolist(),self.no_of_fires.tolist(),unemployed_id)
        unemployed_mask = (agents.secondary_services_and_goods_id == unemployed_id)
        agents.employed_in_secondary_services_and_goods[unemployed_mask] = False
        self.items_produced_raw = np.bincount(agents.secondary_services_and_goods_id[agents.employed_in_secondary_services_and_goods],weights=agents.items_produced_per_agent[agents.employed_in_secondary_services_and_goods],minlength=no_of_businesses)[:no_of_tech_businesses]
        self.items_produced = np.maximum(0, np.int32(np.ceil(self.items_produced_raw)))
        self.production_cost_per_item = np.where(
         self.items_produced > 0,
            self.operational_costs / self.items_produced,
             0.0
            ).astype(np.float32)
        agents.agents_wages.fill(0)
        self.individual_wages = (agents.minimum_wages[agents.employed_in_secondary_services_and_goods]) * (agents.talent[agents.employed_in_secondary_services_and_goods])
        agents.money[agents.employed_in_secondary_services_and_goods] += self.individual_wages
        agents.agents_wages[agents.employed_in_secondary_services_and_goods] += self.individual_wages
        self.production_cost_per_item = np.nan_to_num(self.production_cost_per_item, nan=0.0)
        self.business_money -= self.operational_costs
        self.inventory += self.items_produced
        self.inventory = np.maximum(0, self.inventory)
        self.items_to_be_sold = np.copy(self.inventory)
        self.velocity_ratio = np.float32(self.items_sold / (self.items_not_sold + 1))
        target_markup = k * (self.velocity_ratio - 1.0)
        self.profit_margin = np.clip(target_markup, -1000, 1000)
        self.selling_price = self.production_cost_per_item * (1.0 + self.profit_margin)
        self.selling_price = np.maximum(1.0, self.selling_price).astype(np.float32)
        self.sorted_selling_price = np.argsort(self.selling_price)
        self.sorted_selling_id = self.business_id[self.sorted_selling_price]
        self.sorted_items_to_be_sold = self.items_to_be_sold[self.sorted_selling_price]
        self.profits = np.float32(self.daily_revenue - self.operational_costs)
        self.secondary_goods_and_services_market = np.repeat(self.sorted_selling_id,self.sorted_items_to_be_sold)
