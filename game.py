import math
import random
import logging
import numpy as np
import itertools

from phases import Phases
from cards import Card, Sorcery, Creature, Land


from player import Player

class Game:
    def __init__(self, players):
        self.players = players
        for index, player in enumerate(self.players):
            player.index = index

        self.starting_hand_size = 7
        self.attackers = []
        self.blockers = []
        self.battlefield = []
        self.stack_is_empty = True
        self.temporary_zone = []
        self.damage_targets = []
        self.active_player = self.players[random.randint(0, len(self.players) - 1)]
        self.nonactive_player = self.players[1 - self.active_player.index]
        self.player_just_moved = self.active_player
        self.player_with_priority = self.active_player
        self.current_phase_index = Phases.BEGINNING_PHASE
        # two counters to help keep track of damage assignment - per attacker - per blocker, respectively
        self.attacker_counter = 0
        self.blocker_counter = 0
        self.eligible_attackers=[]
        self.eligible_blockers=[]
        self.turns = 0
        
        self.cardlist=[]

    def update_damage_targets(self):
        self.damage_targets = []
        self.damage_targets = self.get_battlefield_creatures()

    def get_moves(self):
        player = self.player_with_priority
        return self.get_legal_moves(player)

    def get_results(self, player_index):
        player = self.players[player_index]
        opponent = self.players[1 - player.index]
        assert self.is_over()
        if player.has_lost and opponent.has_lost:
            return 0.5
        if player.has_lost:
            return 0.0
        if opponent.has_lost:
            return 1.0
        
    def make_move(self, move, verbose=False):
        player = self.player_with_priority
        self.player_just_moved = player
        aux=[]
        
        if self.current_phase_index == Phases.MAIN_PHASE_PRE_COMBAT:
            for i in range(len(move)):
                done=False
                for h in len(player.hand):
                    if not done and player.hand[h].name is move[i]:
                        aux[i]=player.hand[h].name
                        player.play_card(h, self, verbose)
                        done=True
                    if player.casting_spell != "":
                        target=player.determine_target(self)
                        Sorcery.make_sorcery(player, self, target)
                        player.casting_spell = ""
            return aux
        

    def assign_damage_deterministically(self, player, attacker, index, amount):
        attacker.assign_damage(index, amount)
        return attacker.damage_to_assign > 0

    # NOTE: this function might be too specialized when more spells than 8ed have been added

    def get_tapped_creature_indices(self):
        
        tapped_creature_indices = self.active_player.get_vengables(self)
        """
        tapped_creature_indices =[]
        for i in range(len(self.battlefield)):
            if isinstance(self.battlefield[i], Creature):
                #print("/*--*/%s" %(self.battlefield[i].name))
                if self.battlefield[i].is_tapped:
                    print("/*--*/%s" %(self.battlefield[i].name))
                    #print("/*--*/")
                    tapped_creature_indices.append(i)
        print("/*--*/%s" %(tapped_creature_indices))
        """
        return tapped_creature_indices

    def get_land_indices(self):
        land_indices = []
        for i in range(len(self.battlefield)):
            if isinstance(self.battlefield[i], Land):
                land_indices.append(i)
        return land_indices

    def get_battlefield_creatures(self):
        creatures = []
        for i in range(len(self.battlefield)):
            if isinstance(self.battlefield[i], Creature):
                creatures.append(self.battlefield[i])
        return creatures

    #Por cada hechizo nuevo, editar esto, y buscar Newspells
    def get_legal_spell(self,player):
        if player.casting_spell != "":
            # logging.debug("Returning a spell move now")
            if player.casting_spell == "Vengeance":
                return self.get_tapped_creature_indices()
            if player.casting_spell == "Repulse":
                return self.active_player.get_repulsables(self)
            if player.casting_spell == "Stone Rain":
                return self.get_land_indices()
            if player.casting_spell == "Index":
                return list(itertools.permutations(list(range(min(5, len(player.deck))))))
            if player.casting_spell == "Lava Axe":
                return [0, 1]
            if player.casting_spell == "Volcanic Hammer":
                #return list(range(len(self.damage_targets)))
                return self.active_player.get_hammer(self)
            if player.casting_spell == "Sacred Nectar":
                return ["Resolve Spell"]
            if player.casting_spell == "Rampant Growth":
                ans=player.gold.land_needs()
                return ans[0]
            
            
    # NOTE: this function might have become too crowded, consider refactoring
    
    def get_legal_moves(self, player):
        aux=[]
        self.cardlist=[]
        if self.is_over():
            return []
        if self.current_phase_index == Phases.MAIN_PHASE_PRE_COMBAT:
            aux=player.get_playable_cards(self)
            #Twice because for the sake of Gold, plan_move has been merged partially into get... so unclean
            aux=player.get_playable_cards(self)
            self.cardlist=player.plan_move(self, aux)
            return self.cardlist
        
        
        if self.current_phase_index == Phases.DECLARE_ATTACKERS_STEP:
            attacking_player = self.active_player
            if attacking_player.has_attacked or player is not attacking_player:
                return []
                #return ["Pass"]
            # next two lines get the power set of attackers
            self.eligible_attackers = attacking_player.get_eligible_attackers(self)
            return self.eligible_attackers
        if self.current_phase_index == Phases.DECLARE_BLOCKERS_STEP:
            blocking_player = self.nonactive_player
            if blocking_player.has_blocked or player is not blocking_player:
                return []
                #return ["Pass"]
            self.eligible_blockers = blocking_player.get_eligible_blockers(self)
            return self.eligible_blockers
            #return list(range(np.power(len(self.attackers) + 1, len(eligible_blockers))))        

        
    def combat(self):
        self.attackers=self.active_player.attackers
        print("%s" %(self.attackers))
        #self.blockers=self.nonactive_player.blockers
        print("%s" %(self.blockers))
        for i in range(len(self.attackers)):
            self.attackers[i].is_tapped = True
            deff_dmg=0
            if len(self.blockers)>i:
                if isinstance(self.blockers[i], Creature):
                    self.blockers[i].take_damage(self.attackers[i].power)
                    self.attackers[i].take_damage(self.blockers[i].power)
                    #In case of implement multiple blck for any attack
                elif len(self.blockers[i])>0:
                    for j in range(len(self.blockers[i])):
                        self.blockers[i][j].take_damage(self.attackers[i].deal_damage(self.blockers[i][j].toughness))
                        deff_dmg+=self.blockers[i][j].power
                    self.attackers[i].take_damage(deff_dmg)
                else:
                    self.attackers[i].deal_combat_damage_to_opponent(self)
            else:
                self.attackers[i].deal_combat_damage_to_opponent(self)
                
        self.clean_up_after_combat()
                
    @staticmethod
    def get_possible_damage_assignments(player, attacker, index):
        if len(attacker.damage_assignment_order) is 0:
            return ["Pass"]
        blocker_i = attacker.damage_assignment_order[index]
        remaining_health = blocker_i.toughness - blocker_i.damage_taken
        if attacker.damage_to_assign < remaining_health or index == len(attacker.damage_assignment_order) - 1:
            return list(range(attacker.damage_to_assign, attacker.damage_to_assign + 1))
        else:
            return list(range(remaining_health, attacker.damage_to_assign + 1))

    def start_game(self):
        self.turns =0
        self.active_player.passed_priority = False
        self.active_player.can_play_land = True
        for i in range(len(self.players)):
            self.players[i].shuffle_deck()
            for j in range(self.starting_hand_size):
                self.players[i].draw_card()
        

    def start_new_turn(self):
        print("P1   %s" %(self.players[0].life))
        print("P2   %s" %(self.players[1].life))
        self.active_player.attackers=[]
        self.nonactive_player.blockers=[]
        self.current_phase_index = Phases.BEGINNING_PHASE
        if self.active_player.index==1:
            self.active_player = self.players[0]
            print("+++++++++++++++++++++++++++++++++++++++++++++>P1 turn")
        else:
            self.active_player = self.players[1]
            print("--------------------------------------------->P2 turn")
        self.turns += 1
        print("Turn number %s" %(self.turns))
        #print("turn %i Started! "%(self.turns))
        #if self.active_player.index == 0:
            #logging.info("Turn number {0} for Gold player".format(self.turns))
        #else :
            #logging.info("Turn number {0} for Silver player".format(self.turns))
            
        self.player_with_priority = self.active_player
        self.nonactive_player = self.players[1 - self.active_player.index]
        self.active_player.draw_card()
        print("     %s" %(self.active_player.hand))
        #print("     %s" %(self.active_player.manapool))
        self.active_player.can_play_land = True
        for permanent in self.battlefield:
            if permanent.owner.index==self.active_player.index:
                permanent.is_tapped = False
            if isinstance(permanent, Creature):
                permanent.summoning_sick = False
                permanent.damage = 0
                permanent.damage_to_assign = permanent.power
                permanent.damage_taken=0
        for i in range(len(self.players)):
            self.players[i].reset_mcosts()
            self.players[i].has_attacked = False
            self.players[i].has_blocked = False

    def go_to_next_phase(self):
        # logging.debug(self.current_phase_index)
        self.current_phase_index = self.current_phase_index.next()

        if self.current_phase_index == Phases.CLEANUP_STEP:
            self.start_new_turn()
            return True
        elif self.current_phase_index ==Phases.END_STEP:
            self.start_new_turn()
            return True
        elif self.current_phase_index == Phases.COMBAT_DAMAGE_STEP:
            #if self.apply_combat_damage():
            self.check_state_based_actions()
            self.clean_up_after_combat()
        elif self.current_phase_index == Phases.DECLARE_BLOCKERS_STEP:
            self.nonactive_player.has_passed = False
            self.active_player.has_passed = True
            self.player_with_priority = self.nonactive_player
        else:
            self.nonactive_player.has_passed = True
            self.active_player.has_passed = False
            self.player_with_priority = self.active_player

    def is_over(self):
        for i in range(len(self.players)):
            if self.players[i].has_lost:
                return True
        return False

    def apply_combat_damage(self):
        any_attackers = False
        for permanent in self.battlefield:
            if isinstance(permanent, Creature):
                if permanent in self.attackers:
                    if len(permanent.is_blocked_by) > 0:
                        for i in range(len(permanent.is_blocked_by)):
                            permanent.is_blocked_by[i].take_damage(permanent.damage_assignment[i])
                            permanent.take_damage(permanent.is_blocked_by[i].power)
                    else:
                        permanent.deal_combat_damage_to_opponent(self)
                any_attackers = True
        return any_attackers

    def check_state_based_actions(self):
        # 704.5g
        for permanent in self.battlefield:
            if isinstance(permanent, Creature):
                if permanent.is_dead:
                    permanent.summoning_sick = False
                    permanent.damage = 0
                    permanent.damage_to_assign = permanent.power
                    permanent.damage_taken=0
                    self.battlefield.remove(permanent)
                    permanent.owner.graveyard.append(permanent)

    def clean_up_after_combat(self):
        # TODO: Simplify this and test!
        self.attackers = []
        self.blockers = []
        self.attacker_counter = 0
        self.blocker_counter = 0
        for permanent in self.battlefield:
            if isinstance(permanent, Creature):
                # TODO: attribute "is_attacking" seems to be useless, remove this from everywhere
                permanent.is_attacking = []
                permanent.is_blocking = []
                permanent.is_blocked_by = []
                permanent.damage_assignment_order = []
                permanent.damage_assignment = []
                permanent.damage_taken = 0
                permanent.damage_to_assign = permanent.power
                
                if permanent.is_dead:
                    print("%s is dead" %(permanent.name))
                    self.battlefield.remove(permanent)
                    
