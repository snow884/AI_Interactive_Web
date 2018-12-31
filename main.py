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

def my_init():
    
    context = {}
    
    context["time"] = 0
    
    objects = []
    
    return objects, context

def my_update(controls, objects, context):
    
    if (context["time"] ==0) :
        objects.append({})
        
        objects[0]['id'] = "obj0"
        objects[0]['width'] = 50
        objects[0]['height'] = 50 
        objects[0]['position'] = "absolute" 
        objects[0]['top'] = 100+math.cos(context["time"]/1000)*100
        objects[0]['left'] = 100+math.sin(context["time"]/1000)*100
        objects[0]['backgroundColor'] = "red"
        objects[0]['backgroundImage'] = ""
        
        objects.append({})
        
        objects[1]['id'] = "obj1"
        objects[1]['width'] = 50
        objects[1]['height'] = 50 
        objects[1]['position'] = "absolute" 
        objects[1]['top'] = 100+math.cos(context["time"]/1000+3.14/2)*100
        objects[1]['left'] = 100+math.sin(context["time"]/1000+3.14/2)*100
        objects[1]['backgroundColor'] = "red"
        objects[1]['backgroundImage'] = ""
    
    context["time"] = context["time"] + 1
    
    objects[0]['id'] = "obj0"
    objects[0]['width'] = 50
    objects[0]['height'] = 50 
    objects[0]['position'] = "absolute" 
    objects[0]['top'] = 100+math.cos(context["time"]/10)*100
    objects[0]['left'] = 100+math.sin(context["time"]/10)*100
    objects[0]['backgroundColor'] = "red"
    objects[0]['backgroundImage'] = ""
    
    objects[1]['id'] = "obj1"
    objects[1]['width'] = 50
    objects[1]['height'] = 50 
    objects[1]['position'] = "absolute" 
    objects[1]['top'] = 100+math.cos(context["time"]/10+3.14/2)*100
    objects[1]['left'] = 100+math.sin(context["time"]/10+3.14/2)*100
    objects[1]['backgroundColor'] = "red"
    objects[1]['backgroundImage'] = ""
    
    return objects, context
    
class my_map:

    def __init__(self):
        self.objects = []
        self.tiles=[]
        self.size_x=100
        self.size_y=100

class my_environment:

    def __init__(self, update_function, init_function):

        self.objects = []
        self.context = []
        
        self.objects, self.context = init_function()
        
        self.controls_active = []
        
        self.screen_y = 10
        self.screen_y = 10
        
        self.update_function = update_function
        
    def update(self, controls):
        
        objects_old = (self.objects).copy()
        
        objects_new, self.context = self.update_function(controls, self.objects, self.context)
        
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
        
class grp_object:
    
    def __init__(self):

        self.id="";
        self.width = 50; 
        self.height = 50; 
        self.position = "absolute"; 
        self.top = 0; 
        self.left = 0; 
        self.backgroundColor = "red";
        self.backgroundImage = ""; 

global env_list

env_list = []

app = Flask(__name__)
app.debug = True
app.secret_key = "super secret key"

@app.route("/update", methods=['GET', 'POST'])
def update():
    
    if request.method == "POST":
        
        control_data = request.get_json()
        
        print(control_data)
        
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

if __name__ == "__main__":
    app.run()
