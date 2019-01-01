#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 19:49:18 2018

@author: ivanskya
"""

from flask import Flask, request, render_template, session
from flask import send_file

import json

import math
import random

from threading import Timer
from time import sleep

import signal
import sys

def my_init():
    
    context = {}
    
    context["time"] = 0
    
    context["x_center"] = 500
    context["y_center"] = 500
    
    objects = []
    
    return objects, context

def my_update(controls, player_id, map_in, context):
    
    player_object = map_in.get_object(player_id)
    
    objects_out = map_in.get_objects(player_object.world_x,player_object.world_y,400,400)
    
    objects = []
    
    for obj_id, obj_out in enumerate(objects_out):
        objects.append({})
        
        objects[len(objects)-1]['id'] = obj_out.object_id
        objects[len(objects)-1]['width'] = obj_out.sz_x
        objects[len(objects)-1]['height'] = obj_out.sz_y 
        objects[len(objects)-1]['position'] = "absolute" 
        objects[len(objects)-1]['top'] = obj_out.world_x - player_object.world_x - obj_out.sz_x/2 + 200
        objects[len(objects)-1]['left'] = obj_out.world_y - player_object.world_y - obj_out.sz_y/2 + 200
        objects[len(objects)-1]['backgroundColor'] = ""
        objects[len(objects)-1]['backgroundImage'] = obj_out.get_image()
        objects[len(objects)-1]['zIndex'] = obj_out.z_index
        
    context["time"] = context["time"] + 1
    
    angle = 180+10*int(math.atan2(float(controls["mouse_x"])-200, float(controls["mouse_y"])-200)/(2*math.pi)*360/10)
    
    player_control_vx = - math.cos(angle/360*2*math.pi)*5
    player_control_vy = - math.cos(angle/360*2*math.pi)*5
    
    map_in.control_player(player_id, player_control_vx, player_control_vy, angle)
    
    return objects, context

class Map_object:
    
    def __init__(self, object_id, object_type, world_x, world_y, world_vx, world_vy, sz_x, sz_y, rotation, z_index, state):
        
        self.object_id = object_id
        self.object_type = object_type
        self.world_x = world_x 
        self.world_y = world_y 
        self.world_vx = world_vx 
        self.world_vy = world_vy
        self.rotation = rotation
        self.sz_x = sz_x 
        self.sz_y = sz_y 
        self.z_index = z_index
        self.state = state      
        
    def get_state(self):
        return(self.state)
    
    def update_pos(self, dt):
        self.world_x = self.world_x + int(self.world_vx)*dt
        self.world_y = self.world_y + int(self.world_vy)*dt
        if (self.object_type=='player') :
            print(self.world_vx*dt,self.world_vy*dt )
    
    def __str__(self):
        my_str = (
            self.object_id + ' [' + self.object_type + ']'
        )
        return(my_str)
        
    __repr__ = __str__

class Sphere_blue(Map_object):
    
    def __init__(self, object_id, world_x, world_y):
        
        Map_object.__init__(self, object_id, 'sphere_blue', world_x, world_y, 0, 0, 50, 50, 0, 10, 'idle')
        
    def get_image(self):
        return('url("get_image/sphere_blue_orig_'+str(int(self.rotation/10)*10)+'.png")')

    def update_state(self,dt):
        pass
    
class Orb(Map_object):
    
    def __init__(self, object_id, world_x, world_y, world_vx, world_vy ):
        
        Map_object.__init__(self, object_id, 'orb', world_x, world_y, world_vx, world_vy, 50, 50, 0, 10, 'fired')
        
        self.timer = 0 
        
    def get_image(self):
        return('url("get_image/orb_orig_'+str(int(self.rotation/10)*10)+'.png")')  
    
    def update_state(self,dt):
        self.timer = self.timer + dt
        
        if (self.timer>10):
            self.state = 'deleted'

class Player(Map_object):
    
    def __init__(self, object_id, world_x, world_y, world_vx, world_vy ):
        Map_object.__init__(self, object_id, 'player', world_x, world_y, world_vx, world_vy, 50, 50, 0, 10, 'online')
        
    def get_image(self):
        return('url("get_image/plane_orig_'+str(int(self.rotation/10)*10)+'.png")')
    
class World_map:

    def __init__(self, sz_x, sz_y):
        
        self.dt = 5
        
        self.sz_x = sz_x
        self.sz_y = sz_y
        
        self.object_list = []
        
        for i in range(0,10):
            self.object_list.append(
                    Sphere_blue(
                            'sphere' + str(i), 
                            random.randint(1,sz_x), 
                            random.randint(1,sz_y)
                            )
                    )
        
        self.thread_timer = Timer(0.1, self.update)
        self.thread_timer.start()
        self.active_timer = 1
        
    def iterate():
        pass
    
    def control_player(self, player_id, world_vx, world_vy, rotation): 
        
        player_obj_id = 0
        
        for obj_id,my_obj in enumerate(self.object_list): 
            if (my_obj.object_id==player_id):
                player_obj_id = obj_id
                
        player_obj = self.object_list[player_obj_id]
        
        player_obj.rotation = rotation
        player_obj.world_vx = world_vx
        player_obj.world_vy = world_vy
        
        self.object_list[player_obj_id] = player_obj
        
        return 0

    def get_object(self, object_id): 
        
        for my_obj in self.object_list: 
            if (my_obj.object_id==object_id):
                return(my_obj)
        
        return 0

    def add_object(self, my_object): 
        
        self.object_list.append(my_object)
        
        print(self.object_list)
        
        return 0

    def update(self):
        
        print(self.object_list)
        
        for my_obj in self.object_list:
            my_obj.update_pos(self.dt)
            my_obj.update_state(self.dt)
        
        self.object_list = [my_obj for my_obj in self.object_list if not(my_obj.get_state()=='deleted')]  
        
        if (self.active_timer):
            self.thread_timer = Timer(0.1, self.update)
            self.thread_timer.start()
            
            
    def get_objects(self, x_center, y_center, box_h, box_w):    
        
        obj_out = [el for el in self.object_list if (
                (el.world_x > x_center - box_h / 2)&
                (el.world_x < x_center + box_h / 2)&
                (el.world_y > y_center - box_w / 2)&
                (el.world_y < y_center + box_w / 2)
            )]
        
        return(obj_out)

    def close(self):
        print('ending the class')
        self.active_timer = 0

    def __del__(self):
        print('ending the class')        
        self.active_timer = 0
        

class my_environment:

    def __init__(self, update_function, init_function):

        print('environment init')
        
        self.objects = []
        self.context = []
        
        self.objects, self.context = init_function()
        
        self.controls_active = []
        
        self.screen_y = 10
        self.screen_y = 10
        
        self.update_function = update_function
        
        self.map = World_map(5000,5000)
        
    def __enter__(self):
        return(self)
    
    def add_player(self, player_id):
        
        self.map.add_object( Player(player_id, 2500, 2500, 0, 0 ) )
        
    def update(self, player_id, controls):
        
        objects_old = (self.objects).copy()
        
        objects_new, self.context = self.update_function(controls, player_id, self.map, self.context)
        
        instruction_list = []
        
        #create
        
        for object_new_curr in objects_new:
            if ( not( object_new_curr['id'] in [object_old['id'] for object_old in objects_old] ) ) :
                instruction = {"instruction": "new_obj","params":object_new_curr}
                
                instruction_list.append(instruction)
                
        #update
        
        for object_new_curr in objects_new:
            if ( object_new_curr['id'] in [object_old['id'] for object_old in objects_old] ) :
                instruction = {"instruction": "mod_obj","params":object_new_curr}
                
                instruction_list.append(instruction)
                
        #delete
        
        for object_old_curr in objects_old:
            if ( not( object_old_curr['id'] in [object_new['id'] for object_new in objects_new] ) ) :
                
                instruction = {"instruction": "del_obj","params":{"id":object_old_curr['id']}}
                
                instruction_list.append(instruction)
        
        self.objects = objects_new
        
        return(instruction_list)
    
    def redraw(self, player_id):
        
        instruction_list = []
        
        for object_new_curr in self.objects:
            instruction = {"instruction": "new_obj", "params":object_new_curr}
            
            instruction_list.append(instruction)
        
        return(instruction_list)

    def __exit__(self ,type, value, traceback):
        
        self.map.close()
        
        return(False)


app = Flask(__name__)
app.debug = True
app.secret_key = "super secret key"

@app.route("/update", methods=['GET', 'POST'])
def update():
    global global_environment
    if request.method == "POST":
        control_data = request.get_json()
        json_out = json.dumps( global_environment.update(session['user_id'], control_data) )
        return( json.dumps( json_out ) )
        
    return("ERROR")
    
@app.route("/redraw", methods=['GET', 'POST'])
def redraw():
    global global_environment
    if request.method == "POST":
        json_out = json.dumps( global_environment.redraw(session['user_id']) )
        return( json.dumps( json_out ) )
    
    return("ERROR")

@app.route('/login', methods=['GET', 'POST'])
def do_login():
    global global_environment
    
    session['stage'] = 2
    
    session['user_id'] = request.form['user_id']
    
    global_environment.add_player(session['user_id'])
    
    return index()

@app.route("/", methods=['GET', 'POST'])
def index():
    if not session.get('stage'):
        return render_template('login.html')
    else:
        if (not(session['stage']==2)):
            return render_template('login.html')
        else:
            session['stage']=1
            return render_template("index.html")

@app.route("/get_image/<img_file>", methods=['GET', 'POST'])
def get_img(img_file):
    
    return send_file("img/rotations/"+img_file, mimetype='image/png')

if __name__ == "__main__":
    
    global global_environment
    
    with my_environment(my_update, my_init) as env1:
        global_environment = env1
        setattr(g, '_messages', messages)
        app.run()