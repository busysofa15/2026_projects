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
         self.opportunity_secondary_services_and_goods = np.float32(0)
         self.base_price = np.float32(100)
         self.base_tech_price = np.float32(1200)
         self.base_secondary_goods_and_services_price = np.float32(100)
         self.global_bank_money = np.float32(0)
         self.total_transactions = np.float32(0)
         self.tech_transactions = np.float32(0)
         self.ubi_bank_money = np.float32(1000000)
         self.amt_to_be_reduced = np.float32(0)
         self.secondary_goods_and_services_transactions = np.float32(0)
         self.total_transaction = np.float32(0)
         self.tech_transactions = np.float32(0)
    def tick(self,agents:agent_data,business_info:business_data,tech,secondary):
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
            self.afford_mask = (agents.money_spent_on_food[self.potential_customers_id] >= self.item_prices)
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
         capital_for_businesses = self.global_bank_money*seed_capital_ratio
         if (self.new_biz_count > 0 )and (self.global_bank_money > 0):
             seed_capital = np.float32(capital_for_businesses / self.new_biz_count)
             business_info.business_money[self.newly_active_mask] += seed_capital
             self.global_bank_money -= np.float32(seed_capital_ratio*self.global_bank_money)
         self.newly_active_tech_mask = agents.tech_business_starts_succesfully
         self.new_tech_biz_count = np.sum(self.newly_active_tech_mask)
         if (self.new_tech_biz_count > 0 )and (self.global_bank_money > 0):
            seed_capital_tech = np.float32(capital_for_businesses / self.new_tech_biz_count)
            tech.business_money[self.newly_active_tech_mask] += seed_capital_tech
            self.global_bank_money -= np.sum(seed_capital_tech)
         self.new_secondary_biz_count = np.sum(agents.secondary_services_and_goods_businesses_spawned_successfully)
         if (self.new_secondary_biz_count > 0) and (self.global_bank_money > 0):
             seed_capital_secondary = (capital_for_businesses/self.new_secondary_biz_count)
             secondary.business_money[agents.secondary_services_and_goods_businesses_spawned_successfully] += seed_capital_secondary
             self.global_bank_money -= np.sum(seed_capital_secondary)
         self.taxable_mask = (agents.employed)&(agents.alive)&(agents.working_age_mask)
         self.taxable_amt = tax_ratio*(agents.agents_wages[self.taxable_mask])
         agents.money[self.taxable_mask] -= self.taxable_amt
         self.ubi_bank_money += np.sum(self.taxable_amt)
         self.agents_need_ubi_mask = (~agents.employed)&(agents.alive)&(agents.food_stock < 2.1)&(~agents.employed_in_tech)&(~agents.employed_in_secondary_services_and_goods)
         self.agents_need_ubi_count = np.sum(self.agents_need_ubi_mask)
         if self.agents_need_ubi_count > 0:
            updated_items_to_be_sold = np.copy(business_info.inventory)
            sorted_items_to_be_sold = updated_items_to_be_sold[business_info.sorted_selling_price_id]
            self.sorted_government_grain_market = np.repeat(business_info.sorted_selling_price_id,sorted_items_to_be_sold)
            self.sorted_selling_price_government_grain = np.repeat(business_info.selling_price[business_info.sorted_selling_price],sorted_items_to_be_sold)
            if (self.agents_need_ubi_count>0) and (len(self.sorted_government_grain_market)>0):
                cumsum_selling_price = np.cumsum(self.sorted_selling_price_government_grain)
                amt_of_grain_that_can_be_brought = np.sum(self.ubi_bank_money > cumsum_selling_price)
                if amt_of_grain_that_can_be_brought > 0:
                    viable_count_grain_market = min(amt_of_grain_that_can_be_brought, self.agents_need_ubi_count)
                    rations_id = agents.id[self.agents_need_ubi_mask]
                    viable_rations_id = rations_id[:viable_count_grain_market]
                    viable_market = self.sorted_government_grain_market[:viable_count_grain_market]
                    viable_prices = self.sorted_selling_price_government_grain[:viable_count_grain_market]
                    agents.food_stock[viable_rations_id] += 1
                    np.add.at(business_info.business_money, viable_market, viable_prices)
                    np.add.at(business_info.daily_revenue, viable_market, viable_prices)
                    np.add.at(business_info.inventory, viable_market, -1)
                    np.add.at(business_info.items_sold, viable_market, 1)
                    self.amt_to_be_reduced = np.sum(viable_prices)
                    self.ubi_bank_money -= self.amt_to_be_reduced
         self.net_population_change = np.float32(agents.current_population_count - agents.previous_population)
         if self.net_population_change > 0:
             money_per_capita_initial = 10*agents.mean_price
             self.global_bank_money += np.float32((1)*(self.net_population_change*money_per_capita_initial))
         self.total_tax_collections = np.sum(self.taxable_amt)
         self.transfer_between_banks_trigger_potentially = (self.total_tax_collections > self.amt_to_be_reduced)|(self.ubi_bank_money < starting_alive_money)
         self.transfer_amt_needed_for_ubi_bank = self.amt_to_be_reduced - self.total_tax_collections
         self.transfer_between_banks_trigger = (self.transfer_between_banks_trigger_potentially)&(self.global_bank_money > self.transfer_amt_needed_for_ubi_bank)
         if self.transfer_between_banks_trigger:
             self.global_bank_money -= self.transfer_amt_needed_for_ubi_bank
             self.ubi_bank_money += self.transfer_amt_needed_for_ubi_bank
         ######


    def tick_tech (self,business_info:business_data,tech,secondary,agents:agent_data):
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
        ###################################### secondary_goods_and_services
        self.potential_customers_mask = (agents.secondary_services_and_goods_items < 5)&(agents.alive)
        self.potential_customers = agents.id[self.potential_customers_mask]
        self.potential_customers = rng.permutation(self.potential_customers)
        self.potential_services_and_goods_market  = secondary.secondary_goods_and_services_market
        self.viable_count_s = min(np.sum(self.potential_customers_mask),len(self.potential_services_and_goods_market))
        self.potential_customers = self.potential_customers[:self.viable_count_s]
        self.potential_services_and_goods_market = self.potential_services_and_goods_market[:self.viable_count_s]
        secondary.items_sold.fill(0)
        secondary.daily_revenue.fill(0)
        if (np.sum(self.potential_customers_mask)>0) and (len(self.potential_services_and_goods_market)>0):
            self.secondary_goods_and_services_item_price = secondary.selling_price[self.potential_services_and_goods_market]
            self.afford_secondary_goods_and_services_mask = (agents.money_spending_on_secondary_services_and_goods[self.potential_customers] > self.secondary_goods_and_services_item_price)
            self.final_customers_s = self.potential_customers[self.afford_secondary_goods_and_services_mask]
            self.final_secondary_goods_and_services_market = self.potential_services_and_goods_market[self.afford_secondary_goods_and_services_mask]
            self.final_secondary_goods_and_services_item_prices = self.secondary_goods_and_services_item_price[self.afford_secondary_goods_and_services_mask]
            if (len(self.final_customers_s)>0) and (len(self.final_secondary_goods_and_services_market)>0):
                agents.money[self.final_customers_s] -= self.final_secondary_goods_and_services_item_prices
                np.add.at(secondary.business_money,self.final_secondary_goods_and_services_market,self.final_secondary_goods_and_services_item_prices)
                np.add.at(secondary.daily_revenue,self.final_secondary_goods_and_services_market,self.final_secondary_goods_and_services_item_prices)
                np.add.at(secondary.inventory,self.final_secondary_goods_and_services_market,-1)
                np.add.at(secondary.items_sold,self.final_secondary_goods_and_services_market,1)
                np.add.at(agents.secondary_services_and_goods_items, self.final_customers_s, 1)
                self.secondary_goods_and_services_transactions = np.sum(self.final_secondary_goods_and_services_item_prices)
        secondary.items_not_sold = np.maximum(0,(secondary.items_to_be_sold - secondary.items_sold))
        self.opportunity_secondary_services_and_goods = 1 - (self.secondary_goods_and_services_transactions/((np.sum(agents.money_spending_on_secondary_services_and_goods))+1))