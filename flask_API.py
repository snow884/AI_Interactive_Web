#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 19:49:18 2018

@author: ivanskya
"""

from flask import Flask, request, render_template, flash, redirect, session, url_for

from flask import send_file

import json, os

from captcha.image import ImageCaptcha

import redis

import random

obj_data_queue = redis.Redis(host='localhost', port=6379, db=0)
con_data_queue = redis.Redis(host='localhost', port=6379, db=1)
user_data_queue = redis.Redis(host='localhost', port=6379, db=2)
log_queue = redis.Redis(host='localhost', port=6379, db=3)

app = Flask(__name__)
app.debug = True
app.secret_key = "super secret key"

def generate_capcha():
    
    numbers = ['1','2','3','4','5','6','7','8','9','0']
    alphabet_lowercase = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    random_list = [random.choice(alphabet_lowercase+numbers) for i in range(0,4) ]
    str1 = ''.join(str(e) for e in random_list)
    return(str1)

def get_instr_update(player_id):
    
    data_new_raw = obj_data_queue.get(player_id)
    if not(data_new_raw is None):
            data_new = json.loads( data_new_raw )
    else:
        data_new = []
    
    return(data_new)

@app.route("/update", methods=['GET', 'POST'])
def update():
    if request.method == "POST":
        
        control_data = request.get_json()
        con_data_queue.set(str(session['user_id']), json.dumps( control_data ), px = 1000 )
        
        instruction_list = get_instr_update( session['user_id'] )
        
        return( json.dumps( instruction_list) )
        
    return("ERROR")

@app.route('/init_score_screen', methods=['GET', 'POST'])
def init_score_screen():
    
    return render_template("game_renderer.html")

@app.route('/login', methods=['GET', 'POST'])
def do_login():
    
    if (session['capcha_solution']==request.form['capcha']):
  
        if ((len(request.form['user_id'])<8) & (len(request.form['user_id'])>20)) :
            return login_screen('short_user_id')
        else:
            player_id = request.form['user_id']
            
            objects_new_raw = obj_data_queue.get(player_id)
            if (objects_new_raw is None):
                    
                session['user_id'] = player_id    
                session['objects'] = []
                
                user_data_queue.set('new_user',json.dumps( session['user_id'] ), px = 200)
                
                log_queue.lpush(
                'website_log', 
                json.dumps( 
                        {
                            'ip':request.environ['REMOTE_ADDR'],
                            'func':'do_login',
                            'user_id':player_id
                        } 
                    ) 
                )
        
                return game_renderer()
            else:
                return login_screen('player_exists')
    else:
        return login_screen('incorrect_capcha')
    
@app.route('/get_capcha_img1', methods=['GET', 'POST'])
def get_capcha_img():
    
    image = ImageCaptcha()
    session['capcha_solution'] = generate_capcha()
    data = image.generate(session['capcha_solution'])
    
    log_queue.lpush(
            'website_log', 
            json.dumps( 
                    {
                        'ip':request.environ['REMOTE_ADDR'],
                        'func':'get_capcha_img',
                        'capcha_solution':session['capcha_solution']
                    } 
                ) 
            )
            
    return send_file(data, mimetype='image/png')

@app.route('/get_website_img/<img_name>', methods=['GET', 'POST'])
def get_website_img(img_name):

    log_queue.lpush(
            'website_log', 
            json.dumps( 
                    {
                        'ip':request.environ['REMOTE_ADDR'],
                        'func':'get_website_img',
                        'img_name':img_name
                    } 
                ) 
            )
    return send_file('templates/static/images/' + img_name, mimetype='image/jpeg')

@app.route("/game_renderer", methods=['GET', 'POST'])
def game_renderer():
    log_queue.lpush(
            'website_log', 
            json.dumps( 
                    {
                        'ip':request.environ['REMOTE_ADDR'],
                        'func':'game_renderer'
                    } 
                ) 
            )
    return render_template("game_renderer.html")
        
@app.route("/login_screen/<warning_type>", methods=['GET', 'POST'])
def login_screen(warning_type):
    
    log_queue.lpush(
            'website_log', 
            json.dumps( 
                    {
                        'ip':request.environ['REMOTE_ADDR'],
                        'func':'login_screen',
                        'warning_type':warning_type
                    } 
                ) 
            )
    
    if (warning_type=='initial_ok'):
        return render_template('login.html')
    if (warning_type=='short_user_id'):
        return render_template('login.html',context_info = "Your username must have 8-20 characters!")
    if (warning_type=='incorrect_capcha'):
        return render_template('login.html',context_info = "The capcha you have typed in is incorrect! Are you a robot ?")
    if (warning_type=='game_exit'):
        return render_template('login.html',context_info = "The game exited.")

@app.route("/frame_set", methods=['GET', 'POST'])
def frame_set():
    return render_template('frame_set.html')

@app.route("/", methods=['GET', 'POST'])
def index():
    log_queue.lpush(
            'website_log', 
            json.dumps( 
                    {
                        'request':request.environ['REMOTE_ADDR'],
                        'func':'index'
                    } 
                ) 
            )
            
    return render_template('index.html')

#@app.route("/add_chat_post", methods=['GET', 'POST'])
#def add_chat_post():
#    return render_template('add_chat_post.html')

@app.route("/get_image/<img_file>", methods=['GET', 'POST'])
def get_img(img_file):
    
    return send_file("img/rotations/"+img_file, mimetype='image/png')

@app.route("/get_preload_image_list", methods=['GET', 'POST'])
def get_preload_image_list():
    
    file_list = ['get_image/' + x for x in os.listdir('img/rotations/')]
    
    return( json.dumps( file_list) )
    
if __name__ == "__main__":
    app.run(host='0.0.0.0')
    #app.run()