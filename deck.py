import cards


def get_bear_wars_deck():
    decklist = []
    for i in range(12):
        decklist.append(cards.Creature("Grizzly Bears 1", "bear", {'Green': 3, 'Generic': 0}, 3, 1))
        decklist.append(cards.Creature("Grizzly Bears 2", "bear", {'Green': 3, 'Generic': 0}, 4, 1))
        decklist.append(cards.Creature("Grizzly Bears 3", "bear", {'Green': 3, 'Generic': 0}, 5, 1))
        decklist.append(cards.Creature("Grizzly Bears 4", "bear", {'Green': 3, 'Generic': 0}, 6, 1))
        decklist.append(cards.Creature("Grizzly Bears 5", "bear", {'Green': 3, 'Generic': 0}, 7, 1))
        decklist.append(cards.Land("Forest", "Basic Land", "Forest", [lambda self: self.owner.add_mana({"Green": 1})]))
        decklist.append(cards.Land("Taiga", "Land", "Mountain Forest", [lambda self: self.owner.add_mana({"Green": 1}),
                                                                        lambda self: self.owner.add_mana({"Red": 1})]))
    return decklist


def get_8ed_core_gold_deck():
    decklist = []
    #req_mana={'Red', 'Green', 'Generic'}
    for i in range(8):  # (8):
        decklist.append(
            cards.Land("Mountain", "Basic Land", "Mountain", "Red"))
    for i in range(8):  # (7):
        decklist.append(cards.Land("Forest", "Basic Land", "Forest", "Green"))
    for i in range(2):
        decklist.append(cards.Creature("Norwood Ranger", "Elf Scout", {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 1, 'Generic': 0}, 1, 2))
        decklist.append(cards.Sorcery("Stone Rain", [0 , 3], {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 1, 'Green': 0, 'Generic': 2}))
        decklist.append(cards.Creature("Grizzly Bears", "Bear", {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 1, 'Generic': 1}, 2, 2))
        decklist.append(cards.Creature("Magical troop", "Bear", {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 1, 'Generic': 1}, 3, 1))
        decklist.append(cards.Creature("Enormous Baloth", "Beast", {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 1, 'Generic': 6}, 7, 7))
        decklist.append(cards.Creature("Scoria Elemental", "Beast", {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 2, 'Green': 0, 'Generic': 3}, 5, 3))
        decklist.append(cards.Creature("Goblin Raider", "Goblin Warrior", {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 1, 'Green': 0, 'Generic': 1}, 2, 2, True))
    for i in range(2):
        decklist.append(cards.Creature("Hill Giant", "Giant", {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 1, 'Green': 0, 'Generic': 3}, 3, 3))
        decklist.append(cards.Sorcery("Volcanic Hammer", [1 , 4], {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 1, 'Green': 0, 'Generic': 1}))
    for i in range(4):
        decklist.append(cards.Creature("Spined Wurm", "Wurm", {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 1, 'Generic': 4}, 4, 3))
        decklist.append(cards.Creature("Ogre Taskmaster", "Ogre", {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 1, 'Green': 0, 'Generic': 3}, 4, 4))
        decklist.append(cards.Sorcery("Lava Axe", [1 , 5], {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 1, 'Green': 0, 'Generic': 4}))
       
        decklist.append(cards.Creature("Norwood Ranger", "Elf Scout", {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 1, 'Generic': 0}, 1, 2))
        decklist.append(cards.Sorcery("Rampant Growth", [0 , 2], {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 1, 'Generic': 1}))
    return decklist


def get_8ed_core_silver_deck():
    decklist = []
    #req_mana={'White', 'Blue', 'Generic'}
    for i in range(8):
        decklist.append(cards.Land("Plains", "Basic Land", "Plains", "White"))
    for i in range(7):
        decklist.append(cards.Land("Island", "Basic Land", "Island", "Blue"))
    for i in range(4):
        decklist.append(cards.Creature("Glory Seeker", "Human Soldier", {'White': 1, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 0}, 2, 2))
    for i in range(4):
        decklist.append(cards.Creature("Giant Octopus", "Octopus", {'White': 0, 'Blue': 1, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 2}, 3, 3))
        decklist.append(cards.Creature("Magical Defender", "Human Wizard", {'White': 0, 'Blue': 1, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 1}, 1, 4))
        decklist.append(cards.Sorcery("Repulse", [-1 , 2], {'White': 0, 'Blue': 1, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 0}))
    for i in range(3):
        decklist.append(cards.Creature("Coral Eel", "Eel", {'White': 0, 'Blue': 1, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 1}, 2, 2))
        decklist.append(cards.Creature("Vizzerdrix", "Beast", {'White': 0, 'Blue': 1, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 5}, 6, 6))
        decklist.append(cards.Sorcery("Sacred Nectar", [-1 , 4], {'White': 1, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 1}))
        decklist.append(cards.Sorcery("Vengeance", [0 , 6], {'White': 1, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 1}))
    for i in range(3):
        decklist.append(cards.Creature("Eager Cadet", "Human Soldier", {'White': 1, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 0}, 1, 1))
        decklist.append(cards.Creature("Fugitive Wizard", "Human Wizard", {'White': 0, 'Blue': 1, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 0}, 1, 2))
        #decklist.append(cards.Sorcery("Index", "", {'White': 0, 'Blue': 1, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 0}))
    return decklist
