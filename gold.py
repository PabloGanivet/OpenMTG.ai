import game
import mcts
import player
import deck
from phases import Phases
from cards import Card, Land, Creature, Sorcery
import pickle


class Gold:
    def __init__(self, player,req_mana):
        self.player=player
        self.manapool=self.player.manapool
        self.manacosts=self.player.manacosts
        self.manaplan = {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 0}
        self.land_convert = ['Plains', 'Island' , 'Swamp' , 'Mountain' , 'Forest']
        
        self.deck = self.player.deck
        self.req_mana =req_mana
        
        self.blockers=[]
        self.block_memory=[]
        
        self.cardlist=[]
        self.legalmoves=[]
        
        #Historicos
        self.repulseds=0
        
        #Info y prints
        self.def_choose=""
        self.def_val=0
        
        
    def determine(self, game, legal):
        if game.current_phase_index == Phases.MAIN_PHASE_PRE_COMBAT:
            print("     %s" %(self.player.manapool))
            self.legalmoves=legal
            self.cardlist=[]
            if self.greed_move(game):
                #print("len del move¡¡¡ %s ¡¡¡" %(len(self.cardlist)))
                self.relative_move()
                print("jugada/ %s /////" %(self.cardlist))
                return self.cardlist
            else:
                return []
                #return ["Pass"]
        elif game.current_phase_index == Phases.DECLARE_ATTACKERS_STEP:
            attackers=self.attack_select(game, legal)
            attackers=self.order_vector(attackers)
            return attackers
        elif game.current_phase_index == Phases.DECLARE_BLOCKERS_STEP:
            self.blockers=[]
            defenders=self.defend_select(game, legal)
            #print("defiende con//// %s /////" %(defenders))
            return defenders
        else:
            return legal
        
 

        """
        elif game.current_phase_index == Phases.DECLARE_BLOCKERS_STEP:
            self.blockers=[]
            defenders=self.defend_select(game, legal)
            return defenders
        """

    """
            ---------------------------------------------------Think and Choose
    """
    """
    ---------------------------------------------------Mana and Cards
    """
    def can_pay_planner(self, index):
        #print("can pay/ %s /////" %(index))
        card=self.player.hand[index]
        costs=[]
        remain=0
        generic=0
        
        
        for key in self.req_mana:
            costs=self.manaplan[key]+ card.mc[key]
            #print("costs / %s /////" %(costs))
            if key is not 'Generic':
                remain=self.manapool[key]-costs
                #print("remain / %s /////" %(remain))
                if remain>=0:
                    generic+=remain
                    #print("gen / %s /////" %(generic))
                else:
                    return False
                
                
        if (generic-card.mc['Generic']-self.manaplan['Generic'])>=0:
            for key in self.manacosts:
                self.manaplan[key]+=card.mc[key]
            #print("true")
            return True
        else:
            #print("false g  cost %s  generic %s" %(card.mc['Generic'], generic))
            return False 
        
    def greed_move(self, game):
        #Return true if planned any move and false if not, if false must use "pass" as a move
        proto_cardlist=["Pass"]
        move_well=-100
        self.manaplan = {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 0}
        remain=self.remain_mana()
        planned=False
        print(" ")
        #print("legal / %s /////" %(self.legalmoves))
        for i in range(len(self.legalmoves)):
            proto_cardlist=[]
            self.manapool=self.player.manapool
            #print("super/ %s /////" %(i))
            self.manaplan = {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 0}
            for j in range(len(self.legalmoves)):
                index=i+j
                
                if index>=len(self.legalmoves):
                    index=index-len(self.legalmoves)
                #print("legal index/ %s /////" %(index))
                #print("hand index/-> %s <-////" %(self.legalmoves[index]))
                if self.legalmoves[index] <len(self.player.hand):
                    if self.can_pay_planner(self.legalmoves[index]):
                        proto_cardlist.append(self.legalmoves[index])
            #print("remain--- %s /////" %(remain))        
            if  move_well<=self.play_well(proto_cardlist):
                move_well=self.play_well(proto_cardlist)
                self.cardlist=proto_cardlist
                print("jugada/ %s/ Valor/ %s ////" %(self.cardlist,move_well))
                planned=True
        return planned
    def play_well(self,card_list):
        result=0
        card_list=self.rescale(card_list)
        for i in range(len(card_list)):
            #print("name %s" %(self.player.hand[card_list[i]].name))
            if isinstance(card_list[i], Creature):
                result+=card_list[i].power*self.player.ag_lif[-1] + card_list[i].toughness*(self.player.def_lif[-1])
                print("%s name %s" %(i, card_list[i].name))
            elif isinstance(card_list[i], Sorcery):
                if card_list[i].subtype[0]==1:
                    result+=(card_list[i].subtype[1]*self.player.ag_crit[-1]+card_list[i].subtype[1]*self.player.ag_lif[-1])*0.5
                    print("name %s subtipe %s" %(card_list[i].name,card_list[i].subtype))
                elif card_list[i].subtype[0]==-1:
                    result+=(card_list[i].subtype[1]*(self.player.def_crit[-1])+card_list[i].subtype[1]*(self.player.def_lif[-1]))*0.5
                else:
                    result+=card_list[i].subtype[1]*0.25*(self.player.def_crit[-1]+self.player.ag_crit[-1] +self.player.def_lif[-1]+self.player.ag_lif[-1])
        result-=self.remain_mana()
            
        return result  
    
    def rescale(self,card_list):
        
        new=[]
        for i in range(len(card_list)):
            new.append(self.player.hand[card_list[i]])
            
        return new
                       
    def remain_mana(self):
        remain=0
        
        for key in self.req_mana:
            if key is not 'Generic':
                remain+= self.player.manapool[key] - self.manaplan[key]
                #print("color %s - cost %s" %(self.player.manapool[key] , self.manaplan[key]))
            else:
                #print("generic cost %s /////" %(self.manaplan[key])) 
                remain-=self.manaplan[key]
        #print("new remain--- %s /////" %(remain)) 
        return remain
    
    def relative_move(self):
        for i in range(len(self.cardlist)):
            counter=self.cardlist[i]
            for j in range(i):
                if self.cardlist[i]>self.cardlist[j]:
                    counter-=1
            self.cardlist[i]=counter
            




    """
    ---------------------------------------------------Attack and Defend
    """
    def attack_select(self, game, legal):
        print("opt att %s" %(legal))
        enemy_blockers=self.get_enemy_blockers(game)
        print("actual deff %s" %(enemy_blockers))
        enemy_not_blockers=self.get_enemy_not_blockers(game)
        print("------------Select")
        if len(legal)>0:
            if len(self.get_enemy_creatures(game))==0:
                print("------------no crit")
                return legal
            elif len(enemy_blockers)==0:
                legal=self.attack_think(legal, "oportunism", game)
                print("------------oportunism")
            elif len(enemy_blockers)<=3:
                posible=self.attack_think(legal, "oportunism2", game)
                print("------------oport >2<")
                if len(posible)>0:
                    legal=posible
                else:
                    legal=self.attack_think(legal, "greatest", game)
                    print("------------greatest")
            else:
                legal=self.attack_think(legal, "greatest", game)
                print("------------greatest")
        return legal
                



    def attack_think(self, legal, option, game):
        resolve=[]
        if option=="oportunism":
            for i in range(len(legal)):
                if legal[i].power<=2 or legal[i].toughness<2:
                    resolve.append(legal[i])
            return resolve
        elif option=="oportunism2":
            dmg_min=self.get_enemy_n_dmg(self.get_enemy_blockers(game),2)
            print("dmg_min %s" %(dmg_min))
            print("troops %s" %(legal))
            for i in range(len(legal)):
                print("tough %s" %(legal[i].toughness))
                if legal[i].toughness>=dmg_min:
                    resolve.append(legal[i])
            return resolve
        elif option=="greatest":
            for i in range(len(legal)):
                if legal[i].power>2 :
                    resolve.append(legal[i])
            return resolve
        

    def defend_select(self, game, legal):
        print("opt deff %s" %(legal))
        enemy_attackers=self.get_enemy_attackers(game)
        print("att %s" %(enemy_attackers[0]))
        self.blockers=[]
        if len(legal)>0 and (len(enemy_attackers)>0 and enemy_attackers!=["Pass"]):
            if self.defend_think(legal, enemy_attackers)<10000:
                print("Defender Strategy %s" %(self.def_choose))
                print("Strategy Value %s" %(self.def_val))
                self.defend_historical()
                return self.blockers
            else:
                self.blockers=[]
        return self.blockers
                

    def defend_historical(self):
        print("Defender Strategy %s"%(self.def_choose))
        if self.def_choose=="Safe Killing":
            print("Defender Strategy %s"%(self.player.deff_strategy))
            self.player.deff_strategy['Neutral']+=1
        elif self.def_choose=="Safe Standing":
            print("Defender Strategy %s"%(self.player.deff_strategy))
            self.player.deff_strategy['Defensive']+=1
        elif self.def_choose=="Kill and Keep":
            print("Defender Strategy %s"%(self.player.deff_strategy))
            self.player.deff_strategy['Agresive']+=1
        elif self.def_choose=="Kill All":
            print("Defender Strategy %s"%(self.player.deff_strategy))
            self.player.deff_strategy['Kamikaze']+=1
     
    def defend_think(self, legal, enemy_attackers):
        remain_life=self.player.life
        legal=self.order_vector(legal)
        self.def_val=0
        
        vector_result=[]
        opt_vector_result=[]
        
        self.block_memory=[]
        self.blockers=[]
        """
        dmg_taken
        att_vector
        deff_vector
        killed
        dead
        """
        
        # Safe Killing
        last=0
        for i in range(len(enemy_attackers)):
            aux=[]
            for j in range(len(legal)):
                if legal[j].power>enemy_attackers[i].toughness and legal[j].toughness>enemy_attackers[i].power and j>last:
                    last=j
                    aux.append(legal[j])
            self.blockers.append(aux)
                
        self.block_memory=  self.blockers       
        vector_result= self.combat_simulator(self.blockers, enemy_attackers)
        self.def_val=self.wellness(vector_result)
        self.def_choose="Safe Killing"
        
        self.blockers=[]
        # Safe Standing
        last=0
        for i in range(len(enemy_attackers)):
            aux=[]
            for j in range(len(legal)):
                if legal[j].toughness>enemy_attackers[i].power and j>last:
                    last=j
                    aux.append(legal[j])
            self.blockers.append(aux)
             
                
        opt_vector_result= self.combat_simulator(self.blockers, enemy_attackers)
        
        if self.wellness(opt_vector_result)>self.wellness(vector_result):
            vector_result=[]
            vector_result=opt_vector_result
            opt_vector_result=[]
            self.block_memory=  []
            self.block_memory=self.blockers
            self.blockers=[]
            self.def_val=self.wellness(vector_result)
            self.def_choose="Safe Standing"
            
            
        self.blockers=[]    
        #Kill All
        last=0
        blck=[]
        for i in range(len(enemy_attackers)):
            aux=[]
            killed= False
            dmg=0
            for j in range(len(legal)):
                if j not in blck and not killed:
                    blck.append(j)
                    aux.append(legal[j])
                    dmg+=legal[j].power
                    if dmg>=enemy_attackers[i].toughness:
                        killed=True
                        self.blockers.append(aux)
                        
        
        opt_vector_result= self.combat_simulator(self.blockers, enemy_attackers)
        
        if self.wellness(opt_vector_result)>self.wellness(vector_result):
            vector_result=[]
            vector_result=opt_vector_result
            opt_vector_result=[]
            self.block_memory=  []
            self.block_memory=self.blockers
            self.blockers=[]
            self.def_val=self.wellness(vector_result)
            self.def_choose="Kill All"
        
        
        
        
        self.blockers=[]
        #Kill and Keep
        last=0
        blck=[]
        for i in range(len(enemy_attackers)):
            aux=[]
            first= True
            killed=False
            dmg=0
            toug=0
            for j in range(len(legal)):
                if j not in blck:
                    if not killed:
                        if first:
                            blck.append(j)
                            aux.append(legal[j])
                            dmg+=legal[j].power
                            toug+=legal[j].toughness
                            first=False
                        else :
                            if (dmg+legal[j].power)>=enemy_attackers[i].toughness and (toug+legal[j].toughness)>enemy_attackers[i].power:
                                blck.append(j)
                                aux.append(legal[j])
                                dmg+=legal[j].power
                                toug+=legal[j].toughness
                        if dmg>=enemy_attackers[i].toughness:
                            killed=True
                            self.blockers.append(aux)
        
            if not killed and not first:
                #Por si ha habido un first pero no se ha podido matar, para no perder esa opcion
                blck.pop()
        
        opt_vector_result= self.combat_simulator(self.blockers, enemy_attackers)
        
        if self.wellness(opt_vector_result)>self.wellness(vector_result):
            vector_result=opt_vector_result
            self.block_memory=  []
            self.block_memory=self.blockers
            self.blockers=[]
            self.def_val=self.wellness(vector_result)
            self.def_choose="Kill and Keep"
            
        self.blockers =  self.block_memory
        
        return vector_result[0]
        
    

    """
            ---------------------------------------------------Info 
    """    
    
    def order_vector(self, vector):
        
        pos=0
        aux=vector
        ans=[]
        for i in range(len(vector)):
            vmax=0
            for j in range(len(aux)):
                if aux[j].power>= vmax:
                    vmax=aux[j].power
                    pos=j
            ans.append(aux[pos])
            aux.pop(pos)
        print("ans %s" %(ans))
        return ans
    
    def get_cost(self, card):
        #print("can pay/ %s /////" %(card))
        cost=0
        
        
        for key in card.mc:
            cost+=card.mc[key]
        return cost
    
    #enemy data

    def get_enemy_creatures(self, game):
        creatures=[]
        for permanent in game.battlefield:
            if permanent.owner.index is game.nonactive_player.index and isinstance(permanent, Creature):
                creatures.append(permanent)
        return creatures
    
    def get_enemy_blockers(self, game):
        creatures=[]
        for permanent in game.battlefield:
            if permanent.owner.index is game.nonactive_player.index and isinstance(permanent, Creature) and not permanent.is_tapped and not permanent.cannot_block:
                creatures.append(permanent)
        return creatures
    
    
    def get_enemy_n_dmg(self, vector,n):
        
        pos=0
        aux=vector
        dmg=0
        
        if n>len(vector):
            n=len(vector)
        for i in range(len(vector)):
            vmax=0
            for j in range(len(aux)):
                if aux[j].power>= vmax:
                    vmax=aux[j].power
                    pos=j
            if n>0:
                dmg+=aux[pos].power
                aux.pop(pos)
                n-=1
        return dmg
    
    def get_enemy_not_blockers(self, game):
        creatures=[]
        for permanent in game.battlefield:
            if permanent.owner.index is game.nonactive_player.index and isinstance(permanent, Creature):
                if permanent.is_tapped or permanent.cannot_block:
                    creatures.append(permanent)
        return creatures
    
    
    
    
    def get_enemy_attackers(self, game):
        attackers =game.attackers
        return attackers
    
    # Could change the wllness to adap to certain mechanics or attitudes
    def wellness(self, vector_result):
        grade=0
        enem =0
        mine =0
        if self.player.life<vector_result[0] or self.player.life==0:
            return -1000
        else:
            for i in range(len(vector_result[1])):
                enem+=vector_result[1][i]
            for i in range(len(vector_result[2])):
                mine+=vector_result[2][i]
            grade+=enem*(self.player.ag_crit[-1])+mine*(self.player.def_crit[-1])
            if grade!=0 :
                grade-=(vector_result[0]/self.player.life)*(self.player.def_lif[-1])*100
            return grade
    #Historic_wellness da dos valores que dicen como ha sido la perdida respecto a un valor anterior, como combat
    # simulator no mata, sabes siempre que hay en el mapa, luego si simulator te dice que ha "muerto", tu puedes 
    # ver que estaba vivo y ver cual ha sido el cambio  
    """
    def historic_welness(self, game, results):
        creatures= game.get_battlefield_creatures()
        mines=[]
        others=[]
        for i in range(len(creatures)):
            if creatures[i].owner==self.player.index:
                mines.append(creatures[i])
            elif creatures[i].owner==(1-self.player.index):
                others.append(creatures[i])
            else:
                print("                                 ////////")
                print("                  Algo ha ido mal////////")
                print("                                 ////////")
        
        mines_aftercombat=[]
        others_aftercombat=[]        
        for i in range(len(mines)):
    """
        
    #Anadir una manera de ver que tenia el enemigo en la mesa, que tenias tu, y como ha quedado despues,
    # para luego cambiar dead y killed por un porcentaje de como queda la mesa, luego esos valores se calculan 
    # con historic_wellness
    def combat_simulator(self, defensor, enemy_attackers):
        
        att_vector=[]
        deff_vector=[]
        att_dmg=0
        deff_dmg=0
        dmg_comb=0
        
        dmg_taken=0
        dead=0
        killed=0
        for i in range(len(enemy_attackers)):
            att_dmg=enemy_attackers[i].power
            deff_dmg=0
            dmg_comb=0
            deff_vector.append(0)
            att_vector.append(0)
            if len(defensor)>i:
                if len(defensor[i])>0:
                    for j in range(len(defensor[i])):
                        deff_dmg+=defensor[i][j].power
                        dmg_comb+=defensor[i][j].toughness
                        if dmg_comb<=att_dmg:
                            deff_vector[i]-=defensor[i][j].toughness*(self.player.def_crit[-1])
                            deff_vector[i]-=defensor[i][j].power*(self.player.ag_crit[-1])
                            dead+=1
                            
                else:
                    dmg_taken+=enemy_attackers[i].power
            else:
                dmg_taken+=enemy_attackers[i].power
            if enemy_attackers[i].toughness<=deff_dmg:
                att_vector[i]+=enemy_attackers[i].power*(self.player.ag_crit[-1])
                att_vector[i]+=enemy_attackers[i].toughness*(self.player.def_crit[-1])
                killed+=1
        vector_result=[]
        vector_result.append(dmg_taken)
        vector_result.append(att_vector)
        # 1   enemy dead tou+pow
        vector_result.append(deff_vector)
        # 2   self dead tou+pow
        vector_result.append(killed)
        # 3   Nº enemy dead
        vector_result.append(dead)
        # 4   Nº self dead
        return vector_result
        
        
        
      
    
    

    """
    ---------------------------------------------------spells
    Por cada hechizo nuevo, editar esto, y buscar Newspells
    """
    #Vengance y repulse se parecen demasiado, sospecho que puede seguir pasando, un castig general que los auna
    # no seria descabellado, que empiece como castig spell de player para elegir los threshold y luego el targeting es general.
    def casting_vengance(self, legally, game):
        """
        Recordar el cambio de legal a legally en esta funcion
        """
        costmin=self.player.costmin[-1]
        powmin=self.player.powmin[-1]
        toughmin=self.player.toughmin[-1]
        quit=[] 
        legal=[]
        ans=[]
        for i in range(len(legally)):
            legal.append(game.battlefield[legally[i]])
        
        
        for i in range(len(legal)):
            if legal[i].owner.index is self.player.index :
                quit.append(i)
            elif legal[i].power<powmin and legal[i].toughness<toughmin:
                quit.append(i)
            elif self.get_cost(legal[i])<=costmin:
                quit.append(i)
        if len(quit)<=len(legally):
            for i in range(len(quit)):
                legally.pop(quit[i]-i)
                legal.pop(quit[i]-i)
                
        legal=self.order_vector(legal)
        for i in range(len(legally)):
            if game.battlefield[legally[i]] ==legal[0]:
                ans.append(legally[i])
        
        return ans
    
    def casting_repulse(self, legally, game):
        """
        Recordar el cambio de legal a legally en esta funcion
        """
        #Un sistema parecido al real, cuanto más usas un hechizo mas vale, porque ahora escaseara mas
        costmin=self.player.costmin[-1]+self.repulseds-2
        if costmin>3:
            costmin=4
        powmin=2
        toughmin=2
        quit=[] 
        legal=[]
        ans=[]
        for i in range(len(legally)):
            legal.append(game.battlefield[legally[i]])
        
        
        for i in range(len(legal)):
            if legal[i].owner.index is self.player.index :
                quit.append(i)
            elif legal[i].power<powmin and legal[i].toughness<toughmin:
                quit.append(i)
            elif self.get_cost(legal[i])<=costmin:
                quit.append(i)
        if len(quit)<=len(legally):
            for i in range(len(quit)):
                legally.pop(quit[i]-i)
                legal.pop(quit[i]-i)
                
        legal=self.order_vector(legal)
        for i in range(len(legally)):
            if game.battlefield[legally[i]] ==legal[0]:
                ans.append(legally[i])
        
        self.repulseds+=1
        return ans
    
        
    def hammer(self, targets, game):
        target=[]
        power=0
        ans=[]
        for i in range(len(targets)):
            print("              posible ans %s ++" %((game.battlefield[targets[i]])))
            if game.battlefield[targets[i]].toughness<=3:
                target.append(targets[i])
        for i in range(len(target)):
            if game.battlefield[targets[i]].power>power:
                ans=[targets[i]]
                power=game.battlefield[targets[i]].power
        if self.player.life<(20*self.player.ag_lif[-1]):
            print("              ++ Volcanic Hammer went to player %s ++" %((1 - self.player.index)))
            return [0, (1 - self.player.index)]
        elif len(ans)>0:
            print("              ++ Volcanic Hammer went to %s ++" %((ans)))
            return [ans]
        else:
            return[]
        
        
    
        
    def land_needs(self):
        lesser=1000
        ans=[]
        times=0
        growthed=""
        
        for i in self.req_mana:
            land=0
            for key in self.manapool:
                
                if key is i and self.manapool[key]<=lesser and self.manapool[key]<=8:
                    lesser=self.manapool[key]
                    times+=1
                    ans.append(self.land_convert[land])
                    growthed=key
                land+=1
                
                
        if times>1:     
            ans=ans[len(ans)-1]        
        self.player.growths[growthed]+=1
        return ans









