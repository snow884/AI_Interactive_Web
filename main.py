#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 19:49:18 2018

@author: ivanskya
"""

from flask import Flask, request, render_template, session
from flask import send_file

import json

import redis
obj_data_queue = redis.Redis(host='localhost', port=6379, db=0)
con_data_queue = redis.Redis(host='localhost', port=6379, db=1)
user_data_queue = redis.Redis(host='localhost', port=6379, db=2)
log_queue = redis.Redis(host='localhost', port=6379, db=3)

app = Flask(__name__)
app.debug = True
app.secret_key = "super secret key"

def get_instr_update(objects_old, player_id):
    
    objects_new_raw = obj_data_queue.get(player_id)
    if not(objects_new_raw is None):
            objects_new = json.loads( objects_new_raw )
    else:
        objects_new = []
    
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
    
    return(instruction_list, objects_new)

def get_instr_redraw(player_id):
    
    objects_new_raw = obj_data_queue.get(player_id)
    if not(objects_new_raw is None):
            objects_new = json.loads( objects_new_raw )
    else:
        objects_new = []
        
    instruction_list = []
    
    for object_new_curr in objects_new:
        instruction = {"instruction": "new_obj", "params":object_new_curr}
        
        instruction_list.append(instruction)
        
    return(instruction_list, objects_new)

@app.route("/update", methods=['GET', 'POST'])
def update():
    if request.method == "POST":
        
        control_data = request.get_json()
        con_data_queue.set(str(session['user_id']), json.dumps( control_data ), px = 200 )
        
        instruction_list, session['objects'] = get_instr_update( session['objects'],session['user_id'] )
        
        return( json.dumps( instruction_list) )
        
    return("ERROR")
    
@app.route("/redraw", methods=['GET', 'POST'])
def redraw():
    
    instruction_list, session['objects'] = get_instr_redraw(session['user_id'])
    
    if request.method == "POST":
        log_queue.set(session['user_id'],instruction_list, px = 200)
        return( json.dumps( instruction_list ) )
    
    return("ERROR")

@app.route('/login', methods=['GET', 'POST'])
def do_login():
    
    session['stage'] = 2
    session['user_id'] = request.form['user_id']
    session['objects'] = []
    
    user_data_queue.set('new_user',json.dumps( session['user_id'] ), px = 200)
    
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
    app.run(host='0.0.0.0')
    #app.run()