#!/usr/bin/python
import json
mydict ={}
mydict['present_stimuli']=10
mydict['type_stimulus']='letters'
mydict['max_nback']=5
mydict['num_stimuli']=5
mydict['num_high_scores']=10
filename='game_spec.txt'
with open(filename,'w') as f:
    json.dump(mydict,f)
    
