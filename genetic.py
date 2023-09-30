import copy
import random
import numpy as np
import logging
import minimax
import json
import random

import main
import game
import mcts
import player
import gold
import genetic

class Genetic:
    def __init__(self):
        self.meta={'costmin': [], 'powmin':[], 'toughmin':[], 'ag_lif':[], 'ag_crit':[],'def_lif':[], 'def_crit':[]}
        self.baseMeta={'costmin': [], 'powmin':[], 'toughmin':[], 'ag_lif':[], 'ag_crit':[],'def_lif':[], 'def_crit':[]}
        self.well=[1]


    def get_metas(self, file, player, gens):
        gen=gens
        
        with open(file, 'r') as f:
            data = json.load(f)
            #print(data)
        
        for key in self.meta: 
            self.meta[key].append(data[key][gen])
        print("///Player %s using meta datas %s ///" %((player.index+1),self.meta))
        #base value in case of reset 
        #{"costmin": [2], "powmin": [3], "toughmin": [3], "ag_ratio": [0.5],  "def_ratio": [0.5]}
        #{"costmin": [2], "powmin": [3], "toughmin": [3], "ag_lif": [0.5],, "ag_crit": [0.5], "def_lif": [0.5]  "def_crit": [0.5]}
        return self.meta


    def save_metas(self,player, file, gens, wells):
        gen1=gens
        well=[]
        well.append(wells)
        with open(file, 'r') as f:
            self.well = json.load(f)
        self.well[gen1]=well
        print("/// Actual well %s ///" %(self.well[gen1][len(self.well[gen1])-1])) 
        with open(file, 'w') as f:
            json.dump(self.well, f)
            
            #print("/// Meta data used %s ///" %(obj[len(obj)-1]))
        
            
    def wellness(self, player, info):    
        #[ratio, games_played, mean_turns0, mean_turns1, cards_remain, life_remain0, life_remain1] 1means win // 0means lose
        if player.index ==0:
            well=100*info[0]-0.5*info[3]+(info[6])+(20-info[5])
        return well


    def mutate(self, fileM, fileW, player, gens, genson):
        mutation_rate=0.2
        with open(fileM, 'r') as f:
            data = json.load(f)
        #print(data)
        for key in self.meta: 
            valor=(data[key][gens[0]]+data[key][gens[1]])/2
            if random.random() < mutation_rate:
                if key=='def_ratio' or key=='ag_ratio':
                    valor=self.mutate_ratios(valor)
                else:
                    valor=self.mutate_ints(valor)
                    
                    
            data[key][genson]=(valor)
        
        #print(data)
        with open(fileM, 'w') as f:
            json.dump(data, f)
        
        
    def mutate_ratios(self,gene):
        mutated_gene = gene + gene*random.uniform(-1.0, 1.0)
        mutated_gene = max(0.0, min(1.0, mutated_gene)) 
        return mutated_gene 

    
    def mutate_ints(self,gene):
        mutated_gene = gene + random.randint(-1, 1)
        mutated_gene = max(0, min(5, mutated_gene)) 
        return mutated_gene

    
    

    def get_high_well(self, file, n):
        with open(file, 'r') as f:
            data = json.load(f)
            
        indexed_lst = list(enumerate(data))
        sorted_lst = sorted(indexed_lst, key=lambda x: x[1][0], reverse=True)
        highest_positions = [index for index, _ in sorted_lst[:n]]
        
        return highest_positions
    
    def get_high_well_direct(self, data, n):
        
        indexed_lst = list(enumerate(data))
        sorted_lst = sorted(indexed_lst, key=lambda x: x[1][0], reverse=True)
        highest_positions = [index for index, _ in sorted_lst[:n]]
        
        return highest_positions

    def update_generation(self, genPop, genW, mutatePop, mutateW):
        for key in self.meta:
            for i in range(len(mutatePop[key])):
                genPop[key].append(mutatePop[key][i])
        for i in range(len(mutateW)):
            genW.append(mutateW[i])
            
            
        fix_gen=self.get_high_well_direct(genW, 40)
        
        genAns={'costmin': [], 'powmin':[], 'toughmin':[], 'ag_lif':[], 'ag_crit':[],'def_lif':[], 'def_crit':[]}
        wellAns=[]
        ans=[]
        for i in range(len(fix_gen)):
            for key in genAns:
                genAns[key].append(genPop[key][fix_gen[i]])
            wellAns.append(genW[fix_gen[i]])
        ans.append(genAns)
        ans.append(wellAns)
        return ans
        
        
def mutate2():
    
    file='metaG'
    #file = input("Enter the file's name: ")
    
    fileM=file+'.txt'
    fileW=file+'well.txt'
    genetico=genetic.Genetic()

    for generacion in range(40):
        gens=genetico.get_high_well(fileW, 20)

        #--hacer los hijos de los 20 mejores
        mutation_rate=0.1
        hijos={'costmin': [], 'powmin':[], 'toughmin':[], 'ag_lif':[], 'ag_crit':[],'def_lif':[], 'def_crit':[]}

        with open(fileM, 'r') as f:
            data = json.load(f)
        #print(data)
        for n in range(len(gens)//2):
           
            i=n*2
            print("mutating")
            print(generacion)
            for key in genetico.meta:
                
                select=random.choice([0,1])
                valor1=data[key][gens[i+select]]
                valor2=data[key][gens[i+1-select]]

                if random.random() <= mutation_rate:
                    if key=='def_crit' or key=='ag_lif' or key=='def_lif' or key=='ag_crit':
                        valor1=genetico.mutate_ratios(valor1)
                    else:
                        valor1=genetico.mutate_ints(valor1)


                if random.random() <= mutation_rate:
                    if key=='def_crit' or key=='ag_lif' or key=='def_lif' or key=='ag_crit':
                        valor2=genetico.mutate_ratios(valor2)
                    else:
                        valor2=genetico.mutate_ints(valor2)

                hijos[key].append(valor1)
                hijos[key].append(valor2)

        #print(data)
        with open('mutateG.txt', 'w') as f:
            json.dump(hijos, f)

        #-- testear los hijos-- recordar cambiar jugadores
        print("calling")
        print(generacion)
        main.call_me()
        #-- fin partida
        #-- Calcular los mejores individuos y usarlos
        with open('mutateGwell.txt', 'r') as f:
            mutateW = json.load(f)

        with open(fileW, 'r') as f:
            genW = json.load(f)
        print("called")
        print(generacion)
        newGen=genetico.update_generation(data, genW, hijos, mutateW)

        with open(fileM, 'w') as f:
            json.dump(newGen[0], f)
        with open(fileW, 'w') as f:
            json.dump(newGen[1], f)
    
        
if __name__ == "__main__":
    mutate2()
   #{"costmin": [2, 2, 2.0], "powmin": [3, 3, 3.0], "toughmin": [3, 3, 3.0], "ag_ratio": [0.75, 0.45, 0.6], "def_ratio": [0.5, 0.65, 0.575]} 
        
        
        
        
        
            
            
            