#!/usr/bin/python
# -*- coding: UTF-8 -*-
from kivy.core.window import Window
from kivy.animation import Animation
import copy
from kivy.uix.widget import Widget
from kivy.properties import (
    ListProperty, NumericProperty, BooleanProperty, ObjectProperty)


class DragNDropWidget(Widget):
    # let kivy take care of kwargs and get signals for free by using
    # properties
    droppable_zone_objects = ListProperty([])
    bound_zone_objects = ListProperty([])
    drag_opacity = NumericProperty(1.0)
    drop_func = ObjectProperty(None)
    drop_args = ListProperty([])
    remove_on_drag = BooleanProperty(True)

    def __init__(self, **kw):
        super(DragNDropWidget, self).__init__(**kw)

        self.register_event_type("on_drag_start")
        self.register_event_type("on_being_dragged")
        self.register_event_type("on_drag_finish")
        self.register_event_type("on_motion_over")
        self.register_event_type("on_motion_out")

        self._dragged = False
        self._dragable = True
        self._fired_already = False

    def set_dragable(self, value):
        self._dragable = value

    def set_remove_on_drag(self, value):
        """
        This function sets the property that determines whether the dragged widget is just copied from its parent or taken from its parent
        @param value: either True or False. If True then the widget will disappear from its parent on drag, else the widget will jsut get copied for dragging
        """
        self.remove_on_drag = value

    def set_bound_axis_positions(self):
        for obj in self.bound_zone_objects:
            try:
                if self.max_y < obj.y+obj.size[1]-self.size[1]:
                    self.max_y = obj.y+obj.size[1]-self.size[1]
            except AttributeError:
                self.max_y = obj.y+obj.size[1]-self.size[1]
            try:
                if self.max_x < obj.x+obj.size[0]-self.size[0]:
                    self.max_x = obj.x + obj.size[0]-self.size[0]
            except AttributeError:
                self.max_x = obj.x+obj.size[0]-self.size[0]
            try:
                if self.min_y > obj.y:
                    self.min_y = obj.y
            except AttributeError:
                self.min_y = obj.y
            try:
                if self.min_x > obj.x:
                    self.min_x = obj.x
            except AttributeError:
                self.min_x = obj.x

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y) and self._dragable:
            # detect if the touch is short - has time and end (if not dispatch drag)
            if abs(touch.time_end - touch.time_start) > 0.2:
                self.dispatch("on_drag_start")


    def on_touch_up(self, touch):
        if self._dragable and self._dragged:
            self.short_touch = True
            self.dispatch("on_drag_finish")
            self.short_touch = False

    def on_touch_move(self, touch):
        if self._dragged and self._dragable:
            x = touch.x
            y = touch.y

            try:
                if touch.x < self.min_x:
                    x = self.min_x
                if touch.x > self.max_x:
                    x = self.max_x
                if touch.y < self.min_y:
                    y = self.min_y
                if touch.y > self.max_y:
                    y = self.max_y
            except AttributeError:
                pass
            self.pos = (x, y)

    def easy_access_dnd(self, function_to_do, function_to_do_out, arguments = [], bind_functions = []):
        """
        This function enables something that can be used instead of drag n drop
        @param function_to_do: function that is to be called when mouse_over event is fired on the widget
        @param bind_functions: what is really to be done - background function for GUI functionality
        """
        Window.bind(mouse_pos=self.on_motion)
        self.easy_access_dnd_function = function_to_do
        self.easy_access_dnd_function_out = function_to_do_out
        self.easy_access_dnd_function_aguments = arguments
        self.easy_access_dnd_function_binds = bind_functions

    def on_motion(self, etype, moutionevent):
        if self.collide_point(Window.mouse_pos[0], Window.mouse_pos[1]):
            if not self._fired_already:
                self.dispatch("on_motion_over")
        else:
            self.dispatch("on_motion_out")

    def on_motion_over(self):
        self.easy_access_dnd_function(
            self.easy_access_dnd_function_aguments,
            self.easy_access_dnd_function_binds)

        self._fired_already = True

    def on_motion_out(self):
        try:
            self.easy_access_dnd_function_out()
        except AttributeError:
            pass
        self._fired_already = False

    def on_drag_start(self):
        print "drag start"
        self.opacity = self.drag_opacity
        self.set_bound_axis_positions()
        self._old_drag_pos = self.pos
        self._old_parent = self.parent
        self._old_index = self.parent.children.index(self)
        self._dragged = True
        if self.remove_on_drag:
            self.reparent(self)
        else:
            #create copy of object to drag
            self.reparent(self)
            # the final child class MUST implement __deepcopy__
            # IF self.remove_on_drag == False !!! In this case this is
            # met in DragableArhellModelImage class
            copy_of_self = copy.deepcopy(self)
            self._old_parent.add_widget(copy_of_self, index=self._old_index)

    def on_drag_finish(self):
        print "drag finish"
        if self._dragged and self._dragable:
            self.opacity = 1.0
            dropped_ok = False
            for obj in self.droppable_zone_objects:
                if obj.collide_point(*self.pos):
                    dropped_ok = True
            if dropped_ok:
                self.drop_func(*self.drop_args)
                anim = Animation(opacity=0, duration=0.7, t="in_quad")
                anim.bind(on_complete=self.deparent)
                anim.start(self)
            else:
                anim = Animation(pos=self._old_drag_pos, duration=0.7, t="in_quad")
                if self.remove_on_drag:
                    anim.bind(on_complete = self.reborn)
                else:
                    anim.bind(on_complete = self.deparent)
                anim.start(self)
            self._dragged = False

    def deparent(self, widget="dumb", anim="dumb2"):
        self.get_root_window().remove_widget(self)

    def on_being_dragged(self):
        print "being dragged"

    def reborn(self, widget, anim):
        self.deparent()
        self._old_parent.add_widget(self, index=self._old_index)

    def reparent(self, widget):
        parent = widget.parent
        orig_size = widget.size
        if parent:
            parent.remove_widget(widget)
            parent.get_root_window().add_widget(widget)
            widget.size_hint = (None, None)
            widget.size = orig_size