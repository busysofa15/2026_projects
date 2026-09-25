from __future__ import annotations
import numpy as np
from parameters import *
from agricultural_sector import *
class agent_data:
    def __init__(self,sectors):
        self.id = np.arange(no_of_agents, dtype=np.int32)
        self.money = np.zeros(no_of_agents,dtype = np.float32)
        self.money[:starting_alive_agents] = np.float32(starting_alive_money)
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
        ##experimental_features
        self.previous_population = np.sum(self.alive)
        #######
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
            self.parent_mask = ((self.money > (np.float32(3*self.minimum_wages))) & (self.food_stock > 3)
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
                #self.money[self.assigned_slots] += np.float32(0.2*self.money[self.chosen_parents])
                #self.money[self.chosen_parents] -= np.float32(0.2*self.money[self.chosen_parents])
                ### experimental
                #self.money[self.assigned_slots] += np.float32(10000)
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
        ##experimental_features
        self.current_population_count = np.sum(self.alive)