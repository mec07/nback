#!/usr/bin/python
import os
import json
from bisect import bisect_left
from evaluation import *
from generate_stimuli import *
from Verbosity import *
from my_input import *
from random import randint
import pdb


def game_loop(spec,score,lives,level):
    stimulus_store=[]
    evaluate_store=[]
    # if the stimulus is "random" then choose a possibility
    stimuli_types=["letters","primes","animals"] # exclude "badwords" as that may not be desired
    if spec['type_stimulus']=="random": 
        index = randint(0,len(stimuli_types)-1)
        stimulus_choice=stimuli_types[index]
    else: stimulus_choice=spec['type_stimulus']
    # start loop
    for ii in range(spec['present_stimuli']+2*level):
        if lives<=0:
            verboseprint(spec['verbose'],"Break out of loop in game_loop")
            break
        # randomly generate stimulus
        stimulus = generate_stimulus(stimulus_choice,spec['num_stimuli'])
    
        # store stimulus (up to max_nback+1)
        if len(stimulus_store)>(spec['max_nback']+(level-1)):
            stimulus_store = stimulus_store[1:]
            stimulus_store.append(stimulus)
        else: 
            stimulus_store.append(stimulus)
        # present stimulus to user and wait for response
        os.system("clear")
        print "\n\n\n\n"
        print "\t"+str(stimulus)
        response = input_integer(0,spec['max_nback']+level-1)
        # evaluate response
        answer = evaluate_response(spec['verbose'],stimulus_store,response)
        if not answer:
            lives-=1
        # store evaluation
        evaluate_store.append(answer)

        # update score based upon evaluation
        if answer:
            score+=10**response
    # present a breakdown of game
    os.system("clear")
    print "Number of correct responses: " + str(evaluate_store.count(True))
    print "Number of incorrect responses: " + str(evaluate_store.count(False))
    print "Number of lives left: "+str(lives)
    # present the final score
    print "Score: " + str(score)
    return score,lives


def nback_game(level,spec):
    information = "\t\t\t WELCOME TO "+spec['gamename']+"\n\n"
    information += "This game has been designed to be a workout for your working memory, a.k.a. short term memory.\n\n"
    information += "Insert 1 to see instructions.\n\n"
    information += "Hit Enter to start level "+str(level)+", with the maximum N = "+str(spec['max_nback']+level-1)
    print information
    want_to_play=input_integer(0,1)

    while want_to_play ==1:
        # Explain game to user
        instructions = "\n\nThe point of the game is to remember the stimuli that are presented to you so that "
        instructions+= "whenever a new stimuli is presented you can enter a number representing how far back "
        instructions+= "the last time you saw that stimuli was. "
        instructions+= "For example, If you see 'A' followed by 'D' then you should type '0' because it is the first "
        instructions+= "time you see 'D', if that is correct, up to "+str(spec['max_nback']+level-1)+" then you get 1 point."
        instructions+= "If you see the sequence 'AD' followed by another 'D' you can type '1' and you get 10 points, "
        instructions+= "because it is 1-back. "
        instructions+= "However, if you see the sequence 'ADJ' followed by another 'D' you can type '2' and get 100 "
        instructions+= "points, because it is 2-back. "
        instructions+= "Similarly, if you see the sequence 'ADJ' followed by another 'A' you can type '3' and get 1000 "
        instructions+= "points. This continus up to a maximum of "+str(spec['max_nback']+level-1)+", where the score is calculated "
        instructions+= "as '10^n' where 'n' is the number back the last time the stimulus occured, up to a maximum of "
        instructions+= str(spec['max_nback']+level-1)+".\n\n\nYou loose a life for every mistake you make. You start with "
        instructions+= str(spec['num_lives'])+" lives. Once you reach "+str(spec['max_score']*(10**(level-1)))+" points you advance to the next level!"
        instructions+= "\n\n\nPress Enter to start the game."
        print instructions
        want_to_play=input_integer(0,1)

        
    # initialisation
    lives=spec['num_lives']
    score=0
    

    
    # if you have enough lives and you want to keep going then continue playing the game
    while (score<spec['max_score']*(10**(level-1)) and lives>0 and want_to_play==0 and level <= spec['max_level']):
        score,lives = game_loop(spec,score,lives,level)
        if lives<=0:
            print "\n\nGAME OVER"
        elif score > spec['max_score']*(10**(level-1)):
            print "\n\nYou beat level "+str(level)+"!!!!!\n\n"
            level+=1
            if level>spec['max_level']: 
                print "\n\nYOU WIN!!!"
            else:
                print "The maximum N has now increased to: "+str(spec['max_nback']+(level-1))
        else:
            print "To keep playing hit enter or insert 1 to stop: "
            want_to_play=input_integer(0,1)
    
    # Check the highscore file
    # high scores should be stores from highest to lowest
    if os.path.isfile(spec['highscorefile']): # make sure that it already exists
        with open(spec['highscorefile'],'r') as f:
            highscores=json.load(f)
        # to avoid an annoying bug, if there is nothing in the highscore file, just enter in a zero score
        if highscores['scores']==None:
            highscores['scores']=[0]
            highscores['names']=[":)"]
        # check to see if the high score list is not yet full
        if abs(spec['num_high_scores'])>len(highscores['scores']):
            # check to see where the new score will fit into the highscore list
            ascending_scores = highscores['scores']
            ascending_scores.reverse() # have to reverse order for the bisect algorithm
            ascending_names = highscores['names']
            ascending_names.reverse()
            new_score_position = bisect_left(ascending_scores,score)
            # add the new high score
            ascending_scores.insert(new_score_position,score)
            print "You got onto the high score list!\nPlease insert your name, up to a maximum of "+str(spec['max_name_length'])+" characters."
            new_name = input_string(spec['max_name_length'])
            ascending_names.insert(new_score_position,new_name)
            # put them back into the correct order
            ascending_scores.reverse()
            ascending_names.reverse()
            highscores['scores'] = ascending_scores
            highscores['names'] = ascending_names
        else:# i.e. list is full, so you have to fight for your position!
            # remove any extra high scores
            while abs(spec['num_high_scores'])<len(highscores['scores']):
                highscores['scores'].pop()
                highscores['names'].pop()
            # check to see where the new score will fit into the highscore list
            ascending_scores = highscores['scores']
            ascending_scores.reverse() # have to reverse order for the bisect algorithm
            new_score_position = bisect_left(ascending_scores,score)
            if new_score_position==0:# i.e. not on the high score list
                pass
            else:
                # add the new high score
                ascending_scores.insert(new_score_position,score)
                ascending_names = highscores['names']
                ascending_names.reverse()
                print "You got onto the high score list!!\nPlease insert your name, up to a maximum of "+str(spec['max_name_length'])+" characters."
                new_name = input_string(spec['max_name_length'])
                ascending_names.insert(new_score_position,new_name)
                ascending_scores.reverse()
                ascending_names.reverse()
                highscores['scores'] = ascending_scores
                highscores['names'] = ascending_names
    
    else: # i.e. the high score list does not yet exist
        # initialise dictionary
        highscores={}
        highscores['scores']=[score]
        print "You got onto the high score list!!!\nPlease insert your name, up to a maximum of "+str(spec['max_name_length'])+" characters."
        new_name = input_string(spec['max_name_length'])
        highscores['names']=[new_name]
    
    
    # print highscores
    print "\t HIGHSCORES LIST:\n"
    # pdb.set_trace()
    for ii in range(len(highscores['scores'])):
        print highscores['names'][ii]+"\t"+str(highscores['scores'][ii])

    # write the high scores back to file
    with open(spec['highscorefile'],'w') as f:
        json.dump(highscores,f)


    print "\n\n\nTo play again hit enter or insert 1 to exit. "
    want_to_play = input_integer(0,1)
    return want_to_play