from __future__ import annotations
import numpy as np
from agents import *
from b2b_tech_sector import *
from agricultural_sector import *
from parameters import *
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
         self.amt_to_be_reduced = np.float32(0)
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
             seed_capital = np.float32((self.global_bank_money*seed_capital_ratio) / self.new_biz_count)
             business_info.business_money[self.newly_active_mask] += seed_capital
             self.global_bank_money -= np.float32(seed_capital_ratio*self.global_bank_money)
         self.newly_active_tech_mask = agents.tech_business_starts_succesfully
         self.new_tech_biz_count = np.sum(self.newly_active_tech_mask)
         if (self.new_tech_biz_count > 0 )and (self.global_bank_money > 0):
            seed_capital_tech = np.float32((self.global_bank_money) / self.new_tech_biz_count)
            business_info.business_money[self.newly_active_tech_mask] += seed_capital_tech
            self.global_bank_money -= np.float32(self.global_bank_money) 
         self.taxable_mask = (agents.employed)&(agents.alive)&(agents.working_age_mask)
         self.taxable_amt = tax_ratio*(agents.agents_wages[self.taxable_mask])
         agents.money[self.taxable_mask] -= self.taxable_amt
         self.ubi_bank_money += np.sum(self.taxable_amt)
         self.agents_need_ubi_mask = (~agents.employed)&(agents.alive)&(agents.food_stock < 2.1)&(~agents.employed_in_tech)
         self.agents_need_ubi_count = np.sum(self.agents_need_ubi_mask)
         self.money_to_be_distributed_per_agent = np.float32(agents.mean_price + 0.1*agents.mean_price)
         self.amt_to_be_reduced = (self.agents_need_ubi_count*self.money_to_be_distributed_per_agent)
         if (self.agents_need_ubi_count>0) and (self.ubi_bank_money > self.amt_to_be_reduced):
             agents.money[self.agents_need_ubi_mask] += self.money_to_be_distributed_per_agent
             self.ubi_bank_money -= self.amt_to_be_reduced 
        ##experimental_features
         self.net_population_change = np.float32(agents.current_population_count - agents.previous_population)
         if self.net_population_change > 0:
             money_per_capita_initial = 10*agents.mean_price
             self.ubi_bank_money += np.float32(self.net_population_change*money_per_capita_initial)
         self.total_tax_collections = np.sum(self.taxable_amt)
         self.transfer_between_banks_trigger_potentially = (self.total_tax_collections > self.amt_to_be_reduced)|(self.ubi_bank_money < starting_alive_money)
         self.transfer_amt_needed_for_ubi_bank = self.amt_to_be_reduced - self.total_tax_collections
         self.transfer_between_banks_trigger = (self.transfer_between_banks_trigger_potentially)&(self.global_bank_money > self.transfer_amt_needed_for_ubi_bank)
         if self.transfer_between_banks_trigger:
             self.global_bank_money -= self.transfer_amt_needed_for_ubi_bank
             self.ubi_bank_money += self.transfer_amt_needed_for_ubi_bank
         ######


    def tick_tech (self,business_info:business_data,tech):
        self.potential_biz_customers_mask = (business_info.business_is_active)
        self.potential_biz_customers = business_info.business_id[self.potential_biz_customers_mask]
        self.potential_biz_customers = rng.permutation(self.potential_biz_customers)
        self.potential_tech_market  = tech.tech_market
        self.viable_count = min(np.sum(self.potential_biz_customers_mask),len(self.potential_tech_market))
        self.potential_biz_customers = self.potential_biz_customers[:self.viable_count]
        self.potential_tech_market = self.potential_tech_market[:self.viable_count]
        tech.items_sold.fill(0)
        tech.daily_revenue.fill(0)
        if (np.sum(self.potential_biz_customers_mask)>0) and (len(self.potential_tech_market)>0):
            self.tech_item_prices = tech.selling_price[self.potential_tech_market]
            self.afford_tech_mask = ((business_info.business_money[self.potential_biz_customers])>self.tech_item_prices)
            self.final_biz_customers = self.potential_biz_customers[self.afford_tech_mask]
            self.final_tech_market = self.potential_tech_market[self.afford_tech_mask]
            self.final_tech_price = self.tech_item_prices[self.afford_tech_mask]
            if (len(self.final_biz_customers)>0) and (len(self.final_tech_market)>0):
                business_info.business_money[self.final_biz_customers] -= self.final_tech_price
                np.add.at(tech.business_money,self.final_tech_market,self.final_tech_price)
                np.add.at(tech.profits,self.final_tech_market,self.final_tech_price)
                np.add.at(tech.inventory,self.final_tech_market,-1)
                np.add.at(tech.items_sold,self.final_tech_market,1)
                np.add.at(business_info.no_of_tech_units_brought, self.final_biz_customers, 1)
                self.tech_transactions = np.sum(self.final_tech_price)
        tech.items_not_sold = np.maximum(0,(tech.items_to_be_sold - tech.items_sold))
        self.opportunity_tech_sector = 1 - (self.tech_transactions/((np.sum(business_info.money_assigned_to_tech))+1))
        