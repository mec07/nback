#!/usr/bin/python

def input_integer(Min,Max):
    x = None
    while not x:
        try:
            x=str(raw_input("\n"))
            if x=='': x = 0
            else: x = int(x)
            # make sure that the answer lies within the acceptable limits
            if (x>=Min and x<=Max): break # I need to write this break because there is some strange behaviour when 0 is entered.
            else:
                x = None
                raise Exception
        except:
            print 'Invalid number'
    return x


def input_string(Max):
    x = None
    while not x:
        try:
            x=str(raw_input("\n"))
            # make sure that the answer is short enough
            if (len(x)<=Max): break 
            else:
                x = None
                raise Exception
        except:
            print 'Invalid string'
    return x    