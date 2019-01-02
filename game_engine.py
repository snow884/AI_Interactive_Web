#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  1 17:33:01 2019

@author: ivanskya
"""

import math
import random

import time

import redis
import json

obj_data_queue = redis.Redis(host='localhost', port=6379, db=0)
con_data_queue = redis.Redis(host='localhost', port=6379, db=1)
user_data_queue = redis.Redis(host='localhost', port=6379, db=2)
log_queue = redis.Redis(host='localhost', port=6379, db=3)

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
    
    angle = 180+10*int(math.atan2(float(controls["mouse_x"])-200, float(controls["mouse_y"])-200)/(2*math.pi)*360/10)
    
    player_control_vx = - math.cos(angle/360*2*math.pi)*5
    player_control_vy = - math.cos(angle/360*2*math.pi)*5
    
    map_in.control_player(player_id, player_control_vx, player_control_vy, angle)
    
    return objects, context

class Map_object:
    
    def __init__(self, object_id, object_type, world_x, world_y, world_vx, world_vy, sz_x, sz_y, rotation, z_index, state, add_object):
        
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
    
    def __str__(self):
        my_str = (
            self.object_id + ' [' + self.object_type + ']'
        )
        return(my_str)
        
    __repr__ = __str__

class Sphere_blue(Map_object):
    
    def __init__(self, object_id, world_x, world_y):
        
        Map_object.__init__(self, object_id, 'sphere_blue', world_x, world_y, 0, 0, 50, 50, 0, 10, 'idle', None)
        
    def get_image(self):
        return('url("get_image/sphere_blue_orig_'+str(int(self.rotation/10)*10)+'.png")')

    def update_state(self,dt):
        pass
    
class Orb(Map_object):
    
    def __init__(self, object_id, world_x, world_y, world_vx, world_vy ):
        
        Map_object.__init__(self, object_id, 'orb', world_x, world_y, world_vx, world_vy, 50, 50, 0, 10, 'fired', None)
        
        self.timer = 0 
        
    def get_image(self):
        return('url("get_image/orb_orig_'+str(int(self.rotation/10)*10)+'.png")')  
    
    def update_state(self,dt):
        self.timer = self.timer + dt
        
        if (self.timer>50):
            self.state = 'deleted'

class Player(Map_object):
    
    def __init__(self, object_id, world_x, world_y, world_vx, world_vy, new_object_func ):
        Map_object.__init__(self, object_id, 'player', world_x, world_y, world_vx, world_vy, 50, 50, 0, 10, 'online', new_object_func)
        self.new_object_func = new_object_func
        self.orb_counter = 0
        self.orb_timer = 0
        self.fire_timer = 0
        
    def get_image(self):
        return('url("get_image/plane_orig_'+str(int(self.rotation/10)*10)+'.png")')
    
    def update_pos(self, dt):
        
        controls_raw = con_data_queue.get(str(self.object_id))
        
        if not(controls_raw is None):
            controls = json.loads( controls_raw )
                
            angle = 180+10*int(math.atan2(float(controls["mouse_x"])-200, float(controls["mouse_y"])-200)/(2*math.pi)*360/10)
            
            self.rotation = angle
            self.world_vx = - math.cos(angle/360*2*math.pi)*1
            self.world_vy = - math.sin(angle/360*2*math.pi)*1
            
            if (controls["mouseDown"]>0):
                self.shoot()
            
        self.world_x = self.world_x + self.world_vx*dt
        self.world_y = self.world_y + self.world_vy*dt
    
    def shoot(self):
        
        if (not(self.fire_timer<20)):
            
            self.new_object_func(
                    Orb(
                            self.object_id + '_fire_' + str(self.orb_counter), 
                            self.world_x, 
                            self.world_y,
                            - math.cos(self.rotation/360*2*math.pi)*10, 
                            - math.sin(self.rotation/360*2*math.pi)*10 
                        )
                    )
            
            self.fire_timer=0
            
    def update_state(self,dt):
        self.orb_timer = self.orb_timer + dt
        
        if (self.orb_timer>10):
            self.orb_timer = 0
            self.new_object_func(Orb(self.object_id + '_orb_' + str(self.orb_counter), self.world_x, self.world_y, 0, 0 ))
        
        self.orb_counter = self.orb_counter+1
        
        if self.orb_counter > 100:
            self.orb_counter = 0

        if (self.fire_timer<20):
            self.fire_timer = self.fire_timer + dt
    
class World_map:

    def __init__(self, sz_x, sz_y):
        
        self.dt = 1
        
        self.sz_x = sz_x
        self.sz_y = sz_y
        
        self.object_list = []
        
        for i in range(0,3000):
            self.object_list.append(
                    Sphere_blue(
                            'sphere' + str(i), 
                            random.randint(1,sz_x), 
                            random.randint(1,sz_y)
                            )
                    )
        
    def iterate():
        pass

    def get_object(self, object_id): 
        
        for my_obj in self.object_list: 
            if (my_obj.object_id==object_id):
                return(my_obj)
        
        return 0

    def add_object(self, my_object): 
        
        self.object_list.append(my_object)
        
        print('adding ' + my_object.object_id)
        
        return 0

    def update(self):
        
        #update objects
        
        for my_obj in self.object_list:
            my_obj.update_pos(self.dt)
            my_obj.update_state(self.dt)
        
        #delete expired objects
        
        self.object_list = [my_obj for my_obj in self.object_list if not(my_obj.get_state()=='deleted')]  
        
        #create new users
        new_player_id_raw = user_data_queue.get('new_user')
        
        if not(new_player_id_raw is None):
            new_player_id = str(json.loads( new_player_id_raw) )
            if (not(new_player_id in [el.object_id for el in self.object_list if (el.object_type=='player')])):
                self.add_object( Player(new_player_id, 2500, 2500, 0, 0, self.add_object ) )
        
        #send players their data
        
        player_obj_list = [el for el in self.object_list if (el.object_type=='player')]
        
        for player_obj in player_obj_list:
            
            objects_out = self.get_objects(player_obj.world_x,player_obj.world_y,400,400)
            
            objects = []
            
            for obj_id, obj_out in enumerate(objects_out):
                objects.append({})
                
                objects[len(objects)-1]['id'] = obj_out.object_id
                objects[len(objects)-1]['width'] = obj_out.sz_x
                objects[len(objects)-1]['height'] = obj_out.sz_y 
                objects[len(objects)-1]['position'] = "absolute" 
                objects[len(objects)-1]['top'] = obj_out.world_x - player_obj.world_x - obj_out.sz_x/2 + 200
                objects[len(objects)-1]['left'] = obj_out.world_y - player_obj.world_y - obj_out.sz_y/2 + 200
                objects[len(objects)-1]['backgroundColor'] = ""
                objects[len(objects)-1]['backgroundImage'] = obj_out.get_image()
                objects[len(objects)-1]['zIndex'] = obj_out.z_index
                
            logging_info = log_queue.get(player_obj.object_id)
            if not(logging_info is None):
                print(player_obj.object_id + ': ' + str(logging_info))
                
            obj_data_queue.set(player_obj.object_id ,json.dumps(objects), px = 200 )
            
    def get_objects(self, x_center, y_center, box_h, box_w):    
        
        obj_out = [el for el in self.object_list if (
                (el.world_x > x_center - box_h / 2)&
                (el.world_x < x_center + box_h / 2)&
                (el.world_y > y_center - box_w / 2)&
                (el.world_y < y_center + box_w / 2)
            )]
        
        return(obj_out)
        

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
        
    def update(self):
        self.map.update()
    
if __name__ == "__main__":
    
    global_environment = my_environment(my_update, my_init)
    
    while True:
        global_environment.update()
        time.sleep(0.05)