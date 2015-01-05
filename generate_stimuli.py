#!/usr/bin/python
from random import randint


def generate_stimulus(type_stimulus,num_stimuli):
    # Choose the stimuli
    if type_stimulus=='letters':
        STIMULI='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    elif type_stimulus=='badwords':
        STIMULI=["FUCK","PENIS","CLITORIS","VAGINA","ASS","BUTT","BITCH","BOLLOCKS","SHIT","COCK","CUNT","DICK","DILDO","DIPSHIT","DUMB","DAMN","FAG","FELLATIO","FORNICATE","HANDJOB","HUMP","JERK","JACKASS","JIZZ","MINGE","PISS"]
    elif type_stimulus=='primes':
        STIMULI=[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    elif type_stimulus=='animals':
        STIMULI=["DOG","CAT","HORSE","TIGER","WOLF","GIRAFFE","ELEPHANT","SNAKE","LEOPARD","RHINO","DEER","LYNX","BEAR"]
    else:
        print "ERROR: THE TYPE_STIMULUS IS NOT VALID."

    # Choose the max number of stimuli to use
    if len(STIMULI)>num_stimuli:
        maxnum=int(num_stimuli)
    else:
        maxnum=len(STIMULI)

    # Generate a random number 
    index = randint(0,maxnum-1)
    return STIMULI[index]



