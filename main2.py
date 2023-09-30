import logging
import os

import game
import mcts
import player
#import playerish
import deck
from phases import Phases
from cards import Card, Land, Creature, Sorcery
import pickle


#grows={'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Generic': 0}
grows={'Red': 0, 'Green': 0}
deff_strategy={'Defensive':0 , 'Agresive':0 , 'Kamikaze':0 , 'Neutral':0}

def configure_logging():
    """
    Configures logging
    :return:
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("[%(levelname)-5.5s]  %(message)s"))
    file_handler = logging.FileHandler("open_mtg.log", 'a', 'utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter("%(asctime)s  [%(levelname)-5.5s]  %(message)s"))

    # code for later when stream output level can be set by command line argument
    """
    if args.verbose:
        stream_handler.setLevel(logging.INFO)
    elif args.silent:
        stream_handler.setLevel(logging.ERROR)
    elif args.debug:
        stream_handler.setLevel(logging.DEBUG)
    else:
        stream_handler.setLevel(logging.WARNING)
    """

    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)


def start_games(amount_of_games):
    for igen in range(1):
        player_a_wins = 0
        player_b_wins = 0
        games_played = 0
        infoed_attackers_blockers=False
        attackers = False
        turn_warden=1000
        bool_warden= False
        bool_warden1= False
        """
        Stadistic values
        """
        #Lost
        mean_turns0=0
        life_remain0=0
        #Won
        mean_turns1=0 
        life_remain1=0
        ratio=0
        life_remain1=0
        #Both
        cards_remain=0
        vengances=0
        repulses=0

        volcanics=0

        #meta Info
        """
        with open("meta.data", "rb") as f:
            obj = pickle.load(f)
        #Seguro para borrar el obj
        obj=[]    
        """   
        lglmove=[]
        logging.info(" ")
        print("     ")
        print("/////////////////////")
        print("/////////////////////")
        print("/////////////////////")

        logging.info("Starting Open MTG. Playing {0} games".format(amount_of_games))
        #60s para 40*20=800partidas
        for i in range(amount_of_games):
            gold_deck = deck.get_8ed_core_gold_deck()
            silver_deck = deck.get_8ed_core_silver_deck()
            #current_game = game.Game([player.Player(silver_deck,{'White', 'Blue'},"metaS",igen), player.Player(silver_deck,{'White', 'Blue'},"sparring",1)])
            current_game = game.Game([player.Player(gold_deck,{'Green', 'Red'},"metaG",0), player.Player(gold_deck,{'Green', 'Red'},"metaG",0)])
            current_game.start_game()

            if current_game.active_player.index == 0:
                print("Gold player Starts")
            else:
                print("Silver player Starts")

            current_game.players[0].get_metas()
            current_game.players[1].get_metas()

            while not current_game.is_over():
                if current_game.active_player.index is 0:


                    if not turn_warden==current_game.turns:
                        turn_warden=current_game.turns
                        bool_warden= True
                        bool_warden1= False
                        #logging.info("Gold player's turn {0}".format(current_game.turns))

                else:


                    if not turn_warden==current_game.turns:
                        turn_warden=current_game.turns
                        bool_warden= True
                        bool_warden1= False
                        #logging.info("Silver player's turn {0}".format(current_game.turns))
                        #print("%s" %(move))


                current_phase = current_game.current_phase_index
                if current_game.current_phase_index == Phases.MAIN_PHASE_PRE_COMBAT and bool_warden:
                    move=current_game.active_player.determine_move(current_game)
                    if move==["Pass"]:
                        bool_warden= False
                        bool_warden1= True
                    else:
                        move=current_game.make_move(move, False)
                        bool_warden= False
                        bool_warden1= True


                if current_game.current_phase_index == Phases.DECLARE_ATTACKERS_STEP and bool_warden1:
                    move=current_game.active_player.determine_move(current_game)
                    current_game.attackers = move
                    #print("%s" %(current_game.attackers))

                    if len(current_game.attackers)>0:
                        attackers = True
                if current_game.current_phase_index == Phases.DECLARE_BLOCKERS_STEP and attackers:
                    move=current_game.nonactive_player.determine_move(current_game)
                    current_game.blockers = move
                    #print("%s" %(current_game.blockers))
                if current_game.current_phase_index == Phases.COMBAT_DAMAGE_STEP_510_1c and attackers:
                    attackers=False
                    bool_warden1= False
                    move =current_game.combat()

                if current_game.current_phase_index == Phases.ENDING_PHASE and not bool_warden1 and not bool_warden:

                    attackers = False
                    infoed_attackers_blockers = False
                    bool_warden= True
                    current_game.clean_up_after_combat()
                    gold_permanents = []
                    gold_used_mana=[]
                    silver_permanents = []
                    silver_used_mana=[]
                    #logging.info("  Current phase is: {0}".format(current_phase)) 
                    #logging.info("Gold player's life: {0}, Silver player's life: {1}" .format(current_game.players[0].life, current_game.players[1].life))
                    for permanent in current_game.battlefield:
                        if permanent.owner.index == 0:
                            if permanent.is_tapped and not isinstance(permanent, Creature):
                                gold_used_mana.append(permanent)
                            else:
                                gold_permanents.append(permanent)
                        else:
                            if permanent.is_tapped and not isinstance(permanent, Creature):
                                silver_used_mana.append(permanent)
                            else:
                                silver_permanents.append(permanent)

                    #logging.info("  gold's permanents: *{0}* {1}".format(gold_used_mana, gold_permanents))
                    #logging.info("  silver's permanents: *{0}* {1} \n\n".format(silver_used_mana, silver_permanents))

                current_game.go_to_next_phase()

            current_game.players[0].lose_life(0)
            current_game.players[1].lose_life(0)

            if current_game.players[1].has_lost:
                player_a_wins += 1
                mean_turns1+=current_game.turns
                life_remain1+=current_game.players[0].life
            elif current_game.players[0].has_lost:
                player_b_wins += 1
                mean_turns0+=current_game.turns
                life_remain0+=current_game.players[1].life
            games_played += 1
            cards_remain+=len(current_game.players[0].deck)+len(current_game.players[0].hand)
            vengances+=current_game.players[1].vengance+current_game.players[0].vengance
            repulses+=current_game.players[1].repulse+current_game.players[0].repulse

            volcanics+=current_game.players[1].volcanic+current_game.players[0].volcanic
            for key in grows:
                grows[key]=grows[key]+current_game.players[0].growths[key]
            for key in deff_strategy:
                deff_strategy[key]=deff_strategy[key]+current_game.players[0].deff_strategy[key]


            print("P1 %s" %(current_game.players[0].life))
            print("P2 %s" %(current_game.players[1].life))
            print("Turn Nº %s" %(current_game.turns))
            print("Growths %s" %(current_game.players[0].growths))
            print("Game %s is over! current standings:  %s - %s" %(games_played, player_a_wins, player_b_wins))
            print("///////////////////////////////////")
            print("///////////////////////////////////")
            print("--------++++++++++++++++++---------")
            print("///////////////////////////////////")
            print("///////////////////////////////////")



        ratio=player_a_wins/games_played
        mean_turns0=mean_turns0/(games_played-player_a_wins)
        mean_turns1=mean_turns1/player_a_wins
        cards_remain=cards_remain/games_played
        life_remain0=life_remain0/(games_played-player_a_wins)
        life_remain1=life_remain1/player_a_wins
        logging.info("--->Player Gold P1 won {0} out of {1}".format(player_a_wins, games_played))
        #logging.info("--->Player Silv P2 won {0} out of {1}".format(player_b_wins, games_played))
        print("Nº of Vengances %s" %(vengances))
        print("Nº of Repulses %s" %(repulses))

        print("Nº of Volcanics %s" %(volcanics))
        print("Total Growths %s" %(grows))
        print("Strategies %s" %(current_game.players[0].deff_strategy))


        print("    Stats       [ratio, played, l_turns, w_turns, cards remain, other_l_life, self_w_life")
        logging.info("[ {0} , {1} , {2} , {3} , {4} , {5} , {6} ]".format(ratio, games_played, mean_turns0, mean_turns1, cards_remain, life_remain0, life_remain1))

        """
        with open("meta.data", "wb") as f:
            obj.append(current_game.players[0].meta)
            pickle.dump(obj, f)
            print("/// Meta data used %s ///" %(obj[len(obj)-1]))
        """
        info_end=[ratio, games_played, mean_turns0, mean_turns1, cards_remain, life_remain0, life_remain1]

        #current_game.players[0].messure_well(info_end)

        #current_game.players[0].save_metas()


        
    
if __name__ == "__main__":
    #pithon main.py
    user_input = input("Enter the amount of matches: ")
    number = int(user_input)
    #Parece que mas hechizos hace que las victorias sean menos pero mas rapidas, es decir, agresivo mal llevado
    
    try:
        configure_logging()
        start_games(number)
    except SystemExit:
        pass
    except KeyboardInterrupt:
        logging.error("Open-mtg stopped by Keyboard Interrupt{0}{0}".format(os.linesep))
    except:
        logging.exception("Unexpected exception")

