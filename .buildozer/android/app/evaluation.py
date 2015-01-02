#!/usr/bin/python
from Verbosity import *

def evaluate_response(verbose,stimulus_store,response):
    # Check to make sure that the response doesn't take you outside bounds
    if response == 0:
        return True
    # Catch the mistake of inserting an empty stimulus_store into this function
    if len(stimulus_store)>0:
        last_stimulus=stimulus_store[-1]
    else:
        return True
    if (response+1)>len(stimulus_store):
        answer=False
    # Check to see if the response is correct
    elif (stimulus_store[-(response+1)]==last_stimulus):
        answer=True
    else:
        answer=False
    verboseprint(verbose,"Answer is: "+str(answer))
    return answer