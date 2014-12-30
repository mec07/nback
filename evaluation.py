#!/usr/bin/python
from Verbosity import *
import ipdb

def evaluate_response(verbose,stimulus_store,response):
    # Check to make sure that the response doesn't take you outside bounds
    try:
        if response == 0:
            return True
        last_stimulus=stimulus_store[-1]
        if (response+1)>len(stimulus_store):
            answer=False
        # Check to see if the response is correct
        elif (stimulus_store[-(response+1)]==last_stimulus):
            answer=True
        else:
            answer=False
    except:
        ipdb.set_trace()
    verboseprint(verbose,"Answer is: "+str(answer))
    return answer