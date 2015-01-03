import kivy 
#import ipdb
import sys

import time
import os
import json

from kivy.app import App
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color, Ellipse, Line
from kivy.utils import get_color_from_hex
from random import randint
from generate_stimuli import *
from evaluation import *
from Verbosity import *

from DragNDropWidget import *
from kivy.config import Config
#Graphics fix
 #this fixes drawing issues on some phones
Window.clearcolor = (0,0,0,1.) 
# FOR ANDROID DEBUGGING - this is to make it closer to the most common android screen ratio of 16:9, can be changed after we perfect the look on android to something that is nicer for desktops, or if we need more resolution
#Window.size = (1600,900)  
#Config.set('graphics','resizable',0) #don't make the app re-sizeable

# ----------- Global objects -------------

__version__ = '"0"' # for turning into android app

# game spec
spec = {
    "verbose":1,
    "num_high_scores": 10, 
    "highscorefile":"highscores.txt",
    "max_nback": 5, 
    "type_stimulus": "badwords", 
    "present_stimuli": 10,
    "num_stimuli": 5,
    "max_name_length":10,
    "max_score":1000000,
    "num_lives":3,
    "gamename":"NBACK",
    "max_level":5
}

card_size_raw = [150,90]
drop_zone_size = (card_size_raw[0] + (card_size_raw[0] * 0.2),card_size_raw[1]+ (card_size_raw[1] * 0.3))
card_size = (card_size_raw[0],card_size_raw[1])

num2words_dict = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten', 11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen', 15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen', 19: 'Nineteen'}

start_text = '''
Welcome to nBack!

The skill of this game is in recognising and remembering patterns.
'''



# ----------- Functions ------------------



# ----------- Classes --------------------

class WidgetDrawer(Widget):
    #This widget is used to draw all of the objects on the screen
    #it handles the following:
    # widget movement, size, positioning
    #whever a WidgetDrawer object is created, an image string needs to be specified
    #example:    wid - WidgetDrawer('./image.png')
 
    #objects of this class must be initiated with an image string
    #;You can use **kwargs to let your functions take an arbitrary number of keyword arguments
    #kwargs ; keyword arguments

    def __init__(self, imageStr, **kwargs): 
        super(WidgetDrawer, self).__init__(**kwargs) #this is part of the **kwargs notation
        #if you haven't seen with before, here's a link http://effbot.org/zone/python-with-statement.html     
        with self.canvas: 
            #setup a default size for the object
            self.size = (Window.width*.002*25,Window.width*.002*25) 
            #this line creates a rectangle with the image drawn on top
            self.rect_bg=Rectangle(source=imageStr,pos=self.pos,size = self.size) 
            #this line calls the update_graphics_pos function every time the position variable is modified
            self.bind(pos=self.update_graphics_pos) 
            self.x = self.center_x
            self.y = self.center_y
            #center the widget 
            self.pos = (self.x,self.y) 
            #center the rectangle on the widget
            self.rect_bg.pos = self.pos 
 
    def update_graphics_pos(self, instance, value):
    #if the widgets position moves, the rectangle that contains the image is also moved
        self.rect_bg.pos = value  
    #use this function to change widget size        
    def setSize(self,width, height): 
        self.size = (width, height)
    #use this function to change widget position    
    def setPos(xpos,ypos):
        self.x = xpos
        self.y = ypos



class AnswerButton(Button):
    #class used to get uniform button styles
    def __init__(self, **kwargs):
        super(AnswerButton, self).__init__(**kwargs)
 #all we're doing is setting the font size. more can be done later
        self.font_size = Window.width*0.018
        self.size = drop_zone_size
        self.background_normal = "assets/drop_box_b.png"
        for key, value in kwargs.iteritems():      # styles is a regular dictionary
            if key == "num":
                self.num = value
            if key == "_parent":
                self._parent = value

        def press_button(obj):
        #this function will be called whenever the reset button is pushed
            print '%s button pushed' % self.num
            self._parent.end_turn(self.num)

        self.bind(on_release=press_button) 

class Stimulus(DragNDropWidget):
    def __init__(self, **kwargs):
        super(Stimulus, self).__init__(**kwargs)
        self.border_width = 5
        # background
        with self.canvas:
            border_colour = get_color_from_hex("#111111")
            bg_colour = get_color_from_hex("#0b6000")
            self.border_colour = Color(border_colour[0],border_colour[1],border_colour[2],border_colour[3])
            self.border = Rectangle(size=(card_size_raw[0]+(self.border_width*2),card_size_raw[1]+(self.border_width*2)))
            self.colour = Color(bg_colour[0],bg_colour[1],bg_colour[2],bg_colour[3])
            self.bg_rect = Rectangle(source='assets/sign.png',pos=self.pos, size=card_size)
        self.label = Label(text="[color=ff0000]World[/color]", markup=True)
        self.label.font_name="assets/Montserrat-Bold.ttf"
        self.add_widget(self.label)
        self.font_size = Window.width*0.018
        self.x = Window.width/2 - card_size_raw[0]/2
        print Window.width
        self.y = Window.height/2 - card_size_raw[1]/2
        # hardcoding for now because it won't centre properly!
        self.label_centre = (self.x - 10,self.y - 20)
        self.label.pos = self.label_centre
        for key, value in kwargs.iteritems():
           if key == "_parent":
               self._parent = value
        self.remove_on_drag = True
        self.drop_func = self.on_drop
        # what can it be dropped on?
        for i in self._parent.buttons:
            self.droppable_zone_objects.append(i)
        # update it regularly so it repaints when stuck to cursor
        Clock.schedule_interval(self.update, 1.0/60.0)
    def update(self, args):
        # this is just weird. I don't know why I need to add a sixth to it, or any of why this is a problem :(
        self.label_centre = (self.x + (card_size_raw[0] * 0.15),self.y - 20 * 0.15)
        self.label.pos = self.label_centre
        self.bg_rect.pos = self.pos
        self.border.pos = (self.x-self.border_width,self.y-self.border_width)
        # ugly hack to keep size from inheriting from parent
        self.size = card_size
        #debugging:
        # self.label.text = str(self.pos)
    def on_drop(self):
        gui = self._parent
        gui.new_stimulus()
        gui.end_turn(self.dropped_obj.num)
        self.remove_widget(self)

class CentreLabel(Label):
    def __init__(self, **kwargs):
        super(CentreLabel, self).__init__(**kwargs)
        self.x = Window.width/2 - self.width/2
        self.y = Window.height/2 - self.height/2
        self.font_name="assets/Montserrat-Bold.ttf"
        

class GUI(Widget):
    # main UI widget
    # def on_enter(instance,widget):
    #     print "user pressed enter"

    # def enter_name(self):
    #     # Example on how to input text
    #     self.textinput = TextInput(text="Enter name:",multiline=False)
    #     self.textinput.bind(on_text_validate=self.on_enter)
    #     self.parent.add_widget(self.textinput)
    def open_highscore_file(self):
        # Open the highscore file
        if os.path.isfile(spec['highscorefile']): # make sure that it already exists
            with open(spec['highscorefile'],'r') as f:
                self.highscores=json.load(f)
            # If there is nothing in the highscore file, just enter in a zero score
            if self.highscores['scores']==None:
                self.highscores['scores']=[0]
                self.highscores['names']=[":)"]
        # If there is no highscore file then just use a zero value
        else:
            self.highscores = {}
            self.highscores['scores']=[0]
            self.highscores['names']=[":)"]


    def gameStart(self): 
        self.hearts = []
        self.buttons = []
        self.lives = spec["num_lives"]
        # draw elements
        self.started = True
        l = Label(text='NBack', font_name="assets/Montserrat-Bold.ttf") #give the game a title
        l.x = Window.width/2 - l.width/2
        l.y = Window.height*0.8
        if self.start_label:
            self.remove_widget(self.start_label)
            self.start_label = None
        self.add_widget(l)
        # lives
        self.lives = spec["num_lives"]
        # buttons
        self.buttons = []
        for ii in range(spec["max_nback"]):
            tmpbutton = AnswerButton(_parent=self,text=str(num2words_dict[ii+1]), num=ii+1, pos=(Window.width*0.05,Window.height*(0.8-ii*0.19) ) )
            self.buttons.append(tmpbutton)
            self.parent.add_widget(tmpbutton)
        # pass button
        self.pass_button = AnswerButton(_parent=self,text="Pass", num=0, pos=(Window.width*0.7,Window.height/2))
        self.buttons.append(self.pass_button)
        self.parent.add_widget(self.pass_button)
        # hearts
        self.hearts=[]
        self.drawHeart()
        self.open_highscore_file()
        self.highscorelabel=Label(text="Highscore: "+str(self.highscores["scores"][0]))
        self.highscorelabel.pos=Window.width*0.8,Window.height*0.05
        self.add_widget(self.highscorelabel)
        self.new_stimulus()
        # stimulus array
        self.stimulus_store = []
        # score_display
        self.score = 0
        self.score_display = Label(text="0")
        self.score_display.x = Window.width*0.5 - self.score_display.width/2
        self.score_display.y = Window.height*0.9 - ((self.score_display.width/2)*2.5)
        self.add_widget(self.score_display)

    #this is the main widget that contains the game. 
    def __init__(self, **kwargs):
        super(GUI, self).__init__(**kwargs)
        self.started = False
        # stimulus
        self.start_label = CentreLabel(_parent=self, text=start_text, pos=Window.center)
        self.add_widget(self.start_label)

    def new_stimulus(self):
        # create stimulus
        self.stimulus = Stimulus(_parent=self)
        self.parent.add_widget(self.stimulus)

    def game_over(self):
        self.clear_widgets()
        self.parent.remove_widget(self.stimulus)
        for ii in range(spec["max_nback"] + 1): # added one for pass button
            # ipdb.set_trace()
            self.parent.remove_widget(self.buttons[ii])
        # remake stimulus
        self.start_label = CentreLabel(_parent=self, text="Touch to restart")
        self.add_widget(self.start_label)
        self.started = False
        # Is this a new highscore?
        if self.score > self.highscores["scores"][0]:
            print "New Highscore!!"
            self.highscores["scores"][0]=self.score
            # If so then update the highscore file
            with open(spec['highscorefile'],'w') as f:
                json.dump(self.highscores,f)



    def drawHeart(self):
        for ii in range(self.lives):
            tmpheart = WidgetDrawer(imageStr="./assets/heart.png")
            tmpheart.pos=Window.width*(0.8+0.05*ii),Window.height*(0.9)
            self.hearts.append(tmpheart)
            print tmpheart.size
            self.add_widget(tmpheart)


    def num_points(self,response):
        if response==0:
            return 0
        else:
            return 10**(response-1)

    def end_turn(self,response):
        # Evaluate the user's response
        answer = evaluate_response(spec['verbose'],self.stimulus_store,response)
        if not answer:
            self.lives-=1 
            self.remove_widget(self.hearts[0])
            self.hearts.pop(0)

        # update score based upon evaluation
        if answer:
            self.score+=self.num_points(response)
        # Update displayed score
        self.score_display.text = str(self.score)
        # Game over
        if self.lives <=0:
            self.game_over()
        else:
            # Generate a new stimulus and store it
            new_stim = generate_stimulus(spec["type_stimulus"],spec["num_stimuli"])
            if len(self.stimulus_store) > spec["max_nback"]:
                self.stimulus_store.pop(0)
            self.stimulus_store.append(new_stim)
            verboseprint(spec["verbose"], self.stimulus_store, len(self.stimulus_store))
            self.stimulus.label.text = new_stim
            return new_stim

    #Every time the screen is touched, the on_touch_down function is called
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self.oneButton)

        if not self.started:
            self.gameStart()
            self.end_turn(0)

    def update(self,dt):
        #This update function is the main update function for the game
        #All of the game logic has its origin here 
        #events are setup here as well
        # everything here is executed every 60th of a second.
        pass

class ClientApp(App):
    def build(self):
        #this is where the root widget goes
        #should be a canvas
        parent = Widget() #this is an empty holder for buttons, etc
 
        app = GUI()
        #Start the game clock (runs update function once every (1/60) seconds
        Clock.schedule_interval(app.update, 1.0/60.0) 
        parent.add_widget(app) #use this hierarchy to make it easy to deal w/buttons
        return parent





if __name__ == '__main__' :
    ClientApp().run()