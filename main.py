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

def my_init():
    
    context = {}
    
    context["time"] = 0
    
    context.x_center = 500
    context.y_center = 500
    
    objects = []
    
    return objects, context

def my_update(controls, map_in, context):
    
    objects_out = map_in.get_objects(context.x_center,context.y_center,400,400)
    
    objects = []
    
    objects_out
    
    if (context["time"] ==0) :
        objects.append({})
        
        objects[0]['id'] = "obj0"
        objects[0]['width'] = 50
        objects[0]['height'] = 50 
        objects[0]['position'] = "absolute" 
        objects[0]['top'] = 100+math.cos(context["time"]/1000)*100
        objects[0]['left'] = 100+math.sin(context["time"]/1000)*100
        objects[0]['backgroundColor'] = ""
        objects[0]['backgroundImage'] = 'url("get_image/plane_orig_'+str(0)+'.png")'
        objects[0]['zIndex'] = 10

        objects.append({})
        
        objects[1]['id'] = "obj1"
        objects[1]['width'] = 50
        objects[1]['height'] = 50 
        objects[1]['position'] = "absolute" 
        objects[1]['top'] = 100+math.cos(context["time"]/50)*100
        objects[1]['left'] = 100+math.sin(context["time"]/50)*100
        objects[1]['backgroundColor'] = ""
        objects[1]['backgroundImage'] = 'url("get_image/plane2_orig_'+str(0)+'.png")'
        objects[1]['zIndex'] = 10

    context["time"] = context["time"] + 1
    
    angle = 180+10*int(math.atan2(float(controls["mouse_x"])-200, float(controls["mouse_y"])-200)/(2*math.pi)*360/10)
    
    objects[0]['id'] = "obj0"
    objects[0]['width'] = 50 
    objects[0]['height'] = 50 
    objects[0]['position'] = "absolute" 
    objects[0]['top'] = 175
    objects[0]['left'] = 175
    objects[0]['backgroundColor'] = ""
    objects[0]['backgroundImage'] = 'url("get_image/plane_orig_'+str(angle)+'.png")'
    objects[0]['zIndex'] = 10
    
    objects[1]['id'] = "obj1"
    objects[1]['width'] = 50
    objects[1]['height'] = 50 
    objects[1]['position'] = "absolute" 
    objects[1]['top'] = 200+math.cos(context["time"]/50)*100
    objects[1]['left'] = 200+math.sin(context["time"]/50)*100
    objects[1]['backgroundColor'] = ""
    objects[1]['backgroundImage'] = 'url("get_image/plane2_orig_'+str(angle)+'.png")'
    objects[1]['zIndex'] = 10
    
    return objects, context

class Map_object:
    
    def __init__(self, object_id, object_type, world_x, world_y, rotation, z_index):
        
        self.object_id = object_id
        self.object_type = object_type
        self.world_x = world_x 
        self.world_y = world_y 
        self.z_index = z_index
        
        self.state = 'idle'
    
    def collide(self,other_object):
        pass
    
    def update(self):
        pass
    
class World_map:

    def __init__(self, sz_x, sz_y):
        
        self.object_list = []
        
        for i in range(0,5000):
            self.object_list.append(Map_object('sphere' + str(i), 'sphere', random.randint(1,sz_x), random.randint(1,sz_y), random.randint(1,360), 10))
        
    def iterate():
        pass
    
    def get_objects(self,x_center,y_center,box_h,box_w):    
        
        obj_out = filter(lambda el: 
            (
                (el.world_x > x_center - box_h / 2)&
                (el.world_x < x_center + box_h / 2)&
                (el.world_y > y_center - box_w / 2)&
                (el.world_y < y_center + box_w / 2)
            ), 
            self.object_list
            )
        
        return(obj_out)
        
class my_environment:

    def __init__(self, update_function, init_function):

        self.objects = []
        self.context = []
        
        self.objects, self.context = init_function()
        
        self.controls_active = []
        
        self.screen_y = 10
        self.screen_y = 10
        
        self.update_function = update_function
        
        self.map = World_map(5000,5000)
        
    def update(self, controls):
        
        objects_old = (self.objects).copy()
        
        objects_new, self.context = self.update_function(controls, self.map, self.context)
        
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
    
    def redraw(self):
        
        instruction_list = []
        
        for object_new_curr in self.objects:
            instruction = {"instruction": "new_obj","params":object_new_curr}
            
            instruction_list.append(instruction)
        
        return(instruction_list)
        
global env_list

env_list = []

app = Flask(__name__)
app.debug = True
app.secret_key = "super secret key"

@app.route("/update", methods=['GET', 'POST'])
def update():
    
    if request.method == "POST":
        control_data = request.get_json()
        json_out = json.dumps( env_list[0].update(control_data) )
        return( json.dumps( json_out ) )
        
    return("ERROR")
    
@app.route("/redraw", methods=['GET', 'POST'])
def redraw():
    
    if request.method == "POST":
        json_out = json.dumps( env_list[0].redraw() )
        return( json.dumps( json_out ) )
    
    return("ERROR")

@app.route("/", methods=['GET', 'POST'])
def index():
    session["user_id"] = len(env_list)
    env_list.append( my_environment(my_update, my_init) )
    
    return render_template("index.html")

@app.route("/get_image/<img_file>", methods=['GET', 'POST'])
def get_img(img_file):
    
    return send_file("img/rotations/"+img_file, mimetype='image/png')

if __name__ == "__main__":
    app.run()
