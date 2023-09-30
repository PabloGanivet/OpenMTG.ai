import copy
import random
import numpy as np
import logging
import minimax

import mcts
import gold
import json

from phases import Phases
from cards import Card, Land, Creature, Sorcery
import genetic

class Player:
    def __init__(self, deck, req_mana, metaf,gen):
        self.index = None
        self.deck = deck
        self.life = 20
        self.generic_debt = 0
        self.can_play_land = False
        self.has_lost = False
        self.hand = []
        self.attackers = []
        self.eligible_attackers= []
        self.blockers = []
        self.graveyard = []
        self.has_attacked = False
        self.has_blocked = False
        self.passed_priority = True
        self.casting_spell = ""
        self.manapool = {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 0}
        
        self.made=[]
        self.manacosts = {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 0}
        
        self.req_mana =req_mana
        self.gold=gold.Gold(self, req_mana)
        self.genetic=genetic.Genetic()
        #Historico
        self.ofen_strategy={'Defensive':0 , 'Agresive':0 , 'Kamikaze':0 , 'Neutral':0}
        self.deff_strategy={'Defensive':0 , 'Agresive':0 , 'Kamikaze':0 , 'Neutral':0}
        
        #Por cada hechizo nuevo, editar esto, y buscar Newspells
        self.vengance=0
        self.repulse=0
        
        self.volcanic=0
        self.growths={'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 0}
        
        #Meta data
        self.gen=gen
        #self.parents=[1,2]
        #self.genson=2
        self.well=0
        self.metaf=metaf+'.txt'
        self.wellf=metaf+'well.txt'
        
        self.costmin=[]
        self.powmin=[]
        self.toughmin=[]
        
        self.ag_lif=[]
        self.ag_crit=[]
        self.def_lif=[]
        self.def_crit=[]
        
        self.meta={'costmin': self.costmin, 'powmin':self.powmin, 'toughmin':self.toughmin, 'ag_lif':self.ag_lif, 'ag_crit':self.ag_crit, 'def_lif':self.def_lif, 'def_crit':self.def_crit}

    def get_mp_as_list(self):
        mp_list = []
        for key in self.manapool:
            for i in range(self.manapool[key]):
                mp_list.append(key)
        return mp_list

    def take_damage(self, amount):
        self.lose_life(amount)

    def lose_life(self, amount):
        self.life -= amount
        if self.life < 1:
            self.has_lost = True
            print("          Player lost their life" )

    def get_metas(self):
        
        self.meta=self.genetic.get_metas(self.metaf,self,self.gen)
        meta=self.meta
        
        self.costmin=meta['costmin']
        self.powmin=meta['powmin']
        self.toughmin=meta['toughmin']
        self.def_lif=meta['def_lif']
        self.ag_crit=meta['ag_crit']
        self.ag_lif=meta['ag_lif']
        self.def_crit=meta['def_crit']
        #base value in case of reset 
        #{"costmin": [2], "powmin": [3], "toughmin": [3], "ag_ratio": [0.5],  "def_ratio": [0.5]}
        
    def messure_well(self, info):
        self.well=self.genetic.wellness(self, info)
        
        print("/// Players well %s ///" %(self.well)) 
            
            
    def save_metas(self):
        if self.index==0:
            self.genetic.save_metas(self, self.wellf,self.gen, self.well)
            for key in self.meta: 
                print("%s : " %(key))
                print("               %s " %(self.meta[key][-1]))
            #print("/// Meta data used %s ///" %(obj[len(obj)-1]))
            print("Wellness : ")
            print("               %s " %(self.well))
        #self.mutate_metas()
    """       
    def mutate_metas(self):
        genes=self.parents
        geneson=self.genson
        self.genetic.mutate(self.metaf, self.wellf, self, genes, geneson)
        
    """    
    def determine_move(self, game):
        self.made=[]
        legal_moves = self.gold.determine(game, game.get_legal_moves(self))
        move=[]
        self.reset_mcosts
        payed= False
        """
        if len(legal_moves)==0:
            return ["Pass"]
        """
        if game.current_phase_index == Phases.MAIN_PHASE_PRE_COMBAT:
            if legal_moves!=["Pass"]:
                payed= True
            
            while payed and len(legal_moves)>0:
                """
                legal_moves = game.get_legal_moves(self)
                """
                if len(legal_moves)>0:
                    card=legal_moves.pop(0)
                    #print("cost %s" %(self.hand[card]))
                    payed= self.can_pay(card)
                    #print("%s" %(payed))
                    if payed:
                        self.play_card(card, game, verbose=True)
                    #print("%s" %(len(legal_moves)))
            return move
            
        if game.current_phase_index == Phases.DECLARE_ATTACKERS_STEP:
            #legal is every attacker, in gold we choose wich, gold is called at the begining
            self.attackers=legal_moves
            return legal_moves
        if game.current_phase_index == Phases.DECLARE_BLOCKERS_STEP:
            self.blockers=legal_moves
            return legal_moves
            """
            attack_number=len(game.attackers)
            if len(legal_moves)<attack_number:
                return legal_moves
            else:
                move=legal_moves[0:(attack_number-1)]
                return move
            """
            
    def plan_move(self, game, legal_moves):
        #More like plan lands
        #Need improve, last card may not be added
        
        if game.current_phase_index == Phases.MAIN_PHASE_PRE_COMBAT:
            for i in range(len(legal_moves)):
                m=legal_moves[i]
                if isinstance(self.hand[m], Land):
                    legal_moves.pop(i)
            
        return  legal_moves
      
    def can_pay(self, index):
        #And also add it to the "bill"
        #Because of that is actually paying it, 'cause there is no paying process anymore
        print(" index %s" %(index))
        print("name %s" %(self.hand[index].name))
        card=self.hand[index]
        #Tiene que mirar que no hayan quitado una carta de antes, si vas a jugar la 9/9 que no hayan jugado la 8/9 dejandote a jugar la 9/8 que no existe. en general aunque no se salga, eso no es bueno.
        """
        print("   ")
        print("%s" %(card.mc))
        print("%s" %(self.manapool))
        print("   ")
        """
        costs=[]
        remain=0
        generic=0
        for key in self.manacosts:
            costs=self.manacosts[key]+ card.mc[key]
            
            if key is not 'Generic':
                remain=self.manapool[key]-costs
                if remain>=0:
                    generic+=remain
                else:
                    return False
            if key is 'Generic' and (generic-costs)>=0:
                for key in self.manacosts:
                    self.manacosts[key]+=card.mc[key]
                return True
            elif key is 'Generic' and (generic-costs)<0:
                return False 
        
    def reset_mcosts(self):
        self.manacosts = {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 0}     
        
    #Por cada hechizo nuevo, editar esto, y buscar Newspells
    def determine_target(self, game):
        targets=game.get_legal_spell(self)
        # Add another AI logic for each player
        if self.casting_spell != "" and len(targets)>0:
            # logging.debug("Returning a spell move now")
            if self.casting_spell == "Vengeance":
                self.vengance+=1
                #return self.gold.casting_vengance(targets, game)
                return targets[0]
            if self.casting_spell == "Repulse":
                self.repulse+=1
                return targets[0]
                #return random.choice(targets)
            if self.casting_spell == "Stone Rain":
                return random.choice(targets)
            if self.casting_spell == "Index":
                return self.deck
            if self.casting_spell == "Lava Axe":
                return [0, 1]
            if self.casting_spell == "Volcanic Hammer":
                self.volcanic+=1
                #ans=self.gold.hammer(targets,game)
                ans=targets
                return ans
            if self.casting_spell == "Sacred Nectar":
                return ["Resolve Spell"]
            if self.casting_spell == "Rampant Growth":
                return targets
        else:
            return False
            
        


    def can_afford_card(self, card):
        """
        print("%s" %(card.mc))
        print("%s" %(self.manapool))
        """
        for key in self.manapool:
            if key is not 'Generic':
                if (self.manapool[key] - card.mc[key] -self.manacosts[key]) < 0:
                    return False
            elif sum(self.manapool.values()) < (sum(card.mc.values())+sum(self.manacosts.values())):
                return False
        return True
    
    #Por cada hechizo nuevo, editar esto, y buscar Newspells
    def has_legal_targets(self, card, game):
        if card.name == "Vengeance" and len(game.get_tapped_creature_indices()) == 0:
            return False
        if card.name == "Repulse" and len(self.get_repulsables(game)) == 0:
            return False
        if card.name == "Stone Rain" and len(game.get_land_indices()) == 0:
            return False
        if card.name == "Rampant Growth" and len(self.deck) <= 1:
            return False
        if card.name == "Volcanic Hammer" and len(self.get_hammer(game))<1 :
            return False
        return True

    def get_opponent(self, game):
        return game.players[1 - self.index]

    def get_playable_cards(self, game):
        playable_indices = []
        for i, card in enumerate(self.hand):
            # logging.debug(card.name)

            if isinstance(card, Land):
                if self.can_play_land:
                    self.play_card(i,game, verbose=True )
            elif isinstance(card, Creature):
                if self.can_afford_card(card):
                    playable_indices.append(i)
            elif isinstance(card, Sorcery):
                if self.can_afford_card(card) and self.has_legal_targets(card, game):
                    playable_indices.append(i)
            else:
                assert False
        return playable_indices

    def find_land_in_library(self, land_type):
        for i in range(len(self.deck)):
            if isinstance(self.deck[i], Land):
                if land_type in self.deck[i].subtypes:
                    return i

    def get_library_land_indices(self):
        land_indices = []
        for i in range(len(self.deck)):
            if isinstance(self.deck[i], Land):
                land_indices.append(i)
        return land_indices

    def extra_mp_append(self, landcard, game):
        landcard.playX(self, game, verbose=False)
        
        
    def reset_mp(self):
        self.manapool = {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Colorless': 0}

    def add_mana(self, mana):
        self.manapool = {x: self.manapool.get(x, 0) + mana.get(x, 0) for x in set(self.manapool).union(mana)}

    def subtract_color_mana(self, mana):
        for key in self.manapool:
            if key!='Colorless':
                self.manapool[key] -= mana[key]
                self.manacosts[key] -= mana[key]
        return mana['Generic']
    
    
    def subtract_generic_mana(self, mana):
        for key in self.manapool:
            if key!='Colorless' and mana>0:
                spare=self.manapool[key]-self.manacosts[key]
                if spare>0 and spare<=mana:
                    self.manapool[key] -= spare
                    self.manacosts[key] -= spare
                    mana-= spare
                elif spare>0 and spare>=mana:
                    self.manapool[key] -= mana
                    self.manacosts[key] -= mana
                    mana=0
        return mana
                

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def draw_card(self):
        if len(self.deck) == 0:
            self.has_lost = True
            print("          Player has no more cards" )
            return False
        drawn_card = self.deck.pop(random.randrange(len(self.deck)))
        self.hand.append(drawn_card)
        return drawn_card

    def play_card(self, index, game, verbose):
        #assert index in self.get_playable_cards(game)
        card = self.hand.pop(index)
        print("play %s" %(card.name))
        """
        self.generic_debt = self.subtract_color_mana(card.mc)
        self.generic_debt= self.subtract_generic_mana(self.generic_debt)
        if self.generic_debt==0:
        """
        card.play(self, game, verbose)
        if not(self.casting_spell=="") and isinstance(card, Sorcery):
            target= self.determine_target(game)
            if target is not False:
                card.make_sorcery(self, game, target)
            else:
                self.hand.append(card)
                self.add_mana(card.mc)
        return card

    def get_activated_abilities(self, game):
        callable_permanents = []
        number_of_abilities = []
        for permanent in game.battlefield:
            if permanent.owner.index is self.index:
                if len(permanent.tapped_abilities) > 0 and not permanent.is_tapped:
                    callable_permanents.append(permanent)
                    number_of_abilities.append(len(permanent.tapped_abilities))
        return callable_permanents, number_of_abilities

    def get_eligible_attackers(self, game):
        eligible_attackers = []
        for permanent in game.battlefield:
            if permanent.owner.index is self.index:
                if isinstance(permanent, Creature) and not permanent.is_tapped:
                    #print("%s" %(permanent))
                    if not permanent.summoning_sick:
                        eligible_attackers.append(permanent)
                     # Attackers and blockers will be always chosen, but here is where ai goes to plan move again
        self.eligible_attackers = eligible_attackers
        #print("%s" %(self.attackers))
        return self.eligible_attackers

    def get_eligible_blockers(self, game):
        eligible_blockers = []
        for permanent in game.battlefield:
            if permanent.owner.index is self.index:
                
                if isinstance(permanent, Creature) and not permanent.is_tapped and not permanent.cannot_block:
                    eligible_blockers.append(permanent)
        self.blockers = eligible_blockers
        #print("%s" %(self.blockers))
        return self.blockers
    #Por cada hechizo nuevo, editar esto, y buscar Newspells
    def get_vengables(self, game):
        vengables = []
        ans=[]
        for i in range(len(game.battlefield)):
            if game.battlefield[i].owner.index is not self.index:
                
                if isinstance(game.battlefield[i], Creature) and game.battlefield[i].is_tapped:
                    vengables.append(i)
        ans=self.gold.casting_vengance(vengables, game)            
        if len(ans)>0:
            print("precessed vengables %s" %(ans))
        return ans

    def get_repulsables(self, game):
        repulsables = []
        ans=[]
        for i in range(len(game.battlefield)):
            if game.battlefield[i].owner.index is not self.index:
                
                if isinstance(game.battlefield[i], Creature):
                    repulsables.append(i)
        ans=self.gold.casting_repulse(repulsables, game) 
        if len(ans)>0:
            print("processed repulsables %s" %(ans))
        return ans
    
    def get_hammer(self, game):
        repulsables = []
        ans=[]
        for i in range(len(game.battlefield)):
            if game.battlefield[i].owner.index is not self.index:
                if isinstance(game.battlefield[i], Creature):
                    repulsables.append(i)
        ans=self.gold.hammer(repulsables, game) 
        if len(ans)>0:
            print("processed hammers %s" %(ans))
        return ans

    def get_nonempty_mana_colors(self):
        mana_colors = []
        for key in self.manapool:
            if key is not 'Generic':
                if self.manapool[key] > 0:
                    mana_colors.append(key)
        return mana_colors

    def pay_generic_debt(self, color):
        self.manapool[color] -= 1
        self.generic_debt -= 1
        return self.generic_debt
