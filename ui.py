import kivy 
import ipdb

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.graphics import Rectangle

from kivy.config import Config
Config.set('graphics','resizable',0) #don't make the app re-sizeable
#Graphics fix
 #this fixes drawing issues on some phones
Window.clearcolor = (0,0,0,1.) 

# Global objects
stimulus = Label(text='TIGER')

def display_simulus(input):
    if input == 2:
        stimulus.text = "HORSE"

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
        for key, value in kwargs.iteritems():      # styles is a regular dictionary
            if key == "num":
                self.num = value

        def press_button(obj):
        #this function will be called whenever the reset button is pushed
            print '%s button pushed' % self.num
            display_simulus(self.num)

        self.bind(on_release=press_button) 

class GUI(Widget):
    #this is the main widget that contains the game. 
    def __init__(self, **kwargs):
        super(GUI, self).__init__(**kwargs)
        l = Label(text='NBack') #give the game a title
        l.x = Window.width/2 - l.width/2
        l.y = Window.height*0.8
        self.add_widget(l) #add the label to the screen
        self.add_widget(stimulus)

    #handle input events
    #kivy has a great event handler. the on_touch_down function is already recognized 
    #and doesn't need t obe setup. Every time the screen is touched, the on_touch_down function is called
 
    def gameStart(self): #this function is called when the game ends
        #add a restart button
        oneButton = MyButton(text='One', num=1)
        twoButton = MyButton(text='Two', num=2)

        oneButton.size = (Window.width*.3,Window.width*.1)
        twoButton.size = (Window.width*.3,Window.width*.1)
        oneButton.pos = Window.width*0.5-oneButton.width, Window.height*0.5
        twoButton.pos = Window.width*0.5+twoButton.width, Window.height*0.5   
 
        #*** It's important that the parent get the button so you can click on it
        #otherwise you can't click through the main game's canvas
        self.parent.add_widget(oneButton)
        self.parent.add_widget(twoButton)

    def on_touch_down(self, touch):
        self.gameStart()
 
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