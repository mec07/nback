import kivy 
import ipdb
import sys
import time

from kivy.app import App
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color, Ellipse
from random import randint
from generate_stimuli import *
from evaluation import *
from Verbosity import *

from DragNDropWidget import *

from kivy.config import Config
Config.set('graphics','resizable',0) #don't make the app re-sizeable
#Graphics fix
 #this fixes drawing issues on some phones
Window.clearcolor = (0,0,0,1.) 

# ----------- Global objects -------------

__version__ = '"0"' # for turning into android app

# game spec
spec = {
    "verbose":1,
    "num_high_scores": 10, 
    "highscorefile":"highscores.txt",
    "max_nback": 3, 
    "type_stimulus": "animals", 
    "present_stimuli": 10,
    "num_stimuli": 5,
    "max_name_length":10,
    "max_score":1000000,
    "num_lives":3,
    "gamename":"NBACK",
    "max_level":5
}



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



class MyButton(Button):
    #class used to get uniform button styles
    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
 #all we're doing is setting the font size. more can be done later
        self.font_size = Window.width*0.018
        self.size = Window.width*.3,Window.width*.1
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
        self.label = Label(text="[color=ff0000]World[/color]", markup=True)
        self.label.font_name="assets/Montserrat-Bold.ttf"
        self.add_widget(self.label)
        self.font_size = Window.width*0.018
        self.x = Window.width/2 - self.width/2
        self.y = Window.height/2 - self.height/2
        self.label.pos = self.pos
        self.size = Window.width*.3,Window.width*.1
        for key, value in kwargs.iteritems():
           if key == "_parent":
               self._parent = value

class CentreLabel(Label):
    def __init__(self, **kwargs):
        super(CentreLabel, self).__init__(**kwargs)
        self.x = Window.width/2 - self.width/2
        self.y = Window.height/2 - self.height/2
        self.font_name="assets/Montserrat-Bold.ttf"
        

class GUI(Widget):
    # main UI widget
    def gameStart(self): 
        self.started = True
        l = Label(text='NBack', font_name="assets/Montserrat-Bold.ttf") #give the game a title
        l.x = Window.width/2 - l.width/2
        l.y = Window.height*0.8
        if self.start_label:
            self.remove_widget(self.start_label)
            self.start_label = None
        self.add_widget(l) #add the label to the screen
        self.stimulus = Stimulus(_parent=self)
        self.parent.add_widget(self.stimulus)
        # stimulus array
        self.stimulus_store = []
        # score_display
        self.score = 0
        self.score_display = Label(text="0")
        self.score_display.x = Window.width*0.5 - self.score_display.width/2
        self.score_display.y = Window.height*0.9 - ((self.score_display.width/2)*2)
        self.add_widget(self.score_display)
        # lives
        self.lives = spec["num_lives"]
        self.oneButton = MyButton(_parent=self,text='One', num=1, pos=(Window.left*0.1,Window.height*0.8))
        self.twoButton = MyButton(_parent=self,text='Two', num=2, pos=(Window.left*0.1,Window.height*0.6))
        self.threeButton = MyButton(_parent=self,text='Three', num=3, pos=(Window.left*0.1,Window.height*0.4))
        #*** It's important that the parent gets the button so you can click on it
        #otherwise you can't click through the main game's canvas
        self.parent.add_widget(self.oneButton)
        self.parent.add_widget(self.twoButton)
        self.parent.add_widget(self.threeButton)
        self.hearts=[]
        self.drawHeart()

    #this is the main widget that contains the game. 
    def __init__(self, **kwargs):
        super(GUI, self).__init__(**kwargs)
        self.started = False
        # stimulus
        self.start_label = CentreLabel(_parent=self, text="Touch to start", pos=Window.center)
        self.add_widget(self.start_label)

    def game_over(self):
        self.clear_widgets()
        self.parent.remove_widget(self.stimulus)
        self.parent.remove_widget(self.oneButton)
        self.parent.remove_widget(self.twoButton)
        self.parent.remove_widget(self.threeButton)
        # remake stimulus
        self.start_label = CentreLabel(_parent=self, text="Touch to restart")
        self.add_widget(self.start_label)
        self.started = False

    def drawHeart(self):
        print "trying to draw heart"
        for ii in range(self.lives):
            tmpheart = WidgetDrawer(imageStr="./assets/heart.png")
            tmpheart.pos=Window.width*(0.8+0.05*ii),Window.height*(0.9)
            self.hearts.append(tmpheart)
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
            if len(self.stimulus_store) >= spec["max_nback"]:
                self.stimulus_store.pop(0)
            self.stimulus_store.append(new_stim)
            verboseprint(spec["verbose"], self.stimulus_store, len(self.stimulus_store))
            self.stimulus.label.text = new_stim
            return new_stim

    #Every time the screen is touched, the on_touch_down function is called
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self.oneButton)
            print "yum"

        if not self.started:
            self.gameStart()
            self.end_turn(0)
        else:
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