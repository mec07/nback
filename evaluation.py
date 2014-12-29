#!/usr/bin/python
from Verbosity import *

def evaluate_response(verbose,stimulus_store,response):
    last_stimulus=stimulus_store[-1]
    # Check to make sure that the response doesn't take you outside bounds
    if (response+1)>len(stimulus_store): answer=False
    # Check to see if the response is correct
    elif (stimulus_store[-(response+1)]==last_stimulus):
        answer=True
    else:
        answer=False
    verboseprint(verbose,"Answer is: "+str(answer))
    return answer