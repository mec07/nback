#!/usr/bin/python
# -----------------------------------------------------------------------------------------
# The idea of the game is to test out the concept of turning the n-back scheme [1] into a
# point based game. It is usually pretty boring (because it is difficult) but by including
# a scoring system and the ability to earn points for any number of n-back means that it 
# becomes accessible.
#
# It might also be possible to put it online and gather enough data to write a scientific
# article on it. 
#
# [1] http://en.wikipedia.org/wiki/N-back
# -----------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------
# Code structure:
#   Read an input file that determines the variables of the game
#   Loop present_stimuli times:
#       Randomly generate the stimuli and keep a record of it (up to 10-back?)
#       Present the stimuli
#       Ask for a response 0 (not seen before), 1 (1-back), 2 (2-back), etc...
#       Change the score based upon response and record response
#   If you have enough lives left you can do it again (You lose a life for every mistake you make)
#   Give the final score and a breakdown of the responses
#   
#
# -----------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------
# INPUTS            TYPE        DESCRIPTION
# 
# verbose           int         Use 0 for low verbosity or 1 for high verbosity
#
# present_stimuli   int         The number of stimuli to be presented to the user.
# 
# type_stimulus     str         The type of stimuli to be presented to the user (currently the
#                               only working option is 'letters').
#
# num_stimuli       int         The maximum number of stimuli that will be used.
#
# max_nback         int         The maximum nback to be stored and scored.
#
# 
# -----------------------------------------------------------------------------------------

import json
import os

from nback_game import *


# Read input file
inputfile='game_spec.txt'
with open(inputfile,'r') as f:
    spec = json.load(f)

want_to_play = 0

# level always starts at 1
level=1

while want_to_play==0: 
    # Play game
    os.system("clear")
    want_to_play = nback_game(level,spec)

