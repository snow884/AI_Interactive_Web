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

import numpy as np

obj_data_queue = redis.Redis(host='localhost', port=6379, db=0)
con_data_queue = redis.Redis(host='localhost', port=6379, db=1)
user_data_queue = redis.Redis(host='localhost', port=6379, db=2)
log_queue = redis.Redis(host='localhost', port=6379, db=3)

class Map_object:
    
    def __init__(self, object_id, object_type, world_x, world_y, world_vx, world_vy, sz_x, sz_y, rotation, z_index, state, new_object_func, col_sz):
        
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
        self.col_sz = col_sz  
        self.new_object_func = new_object_func
        
    def get_state(self):
        return(self.state)
    
    def update_pos(self, dt):
        self.world_x = self.world_x + (self.world_vx)*dt
        self.world_y = self.world_y + (self.world_vy)*dt
    
    def update_state(self,dt):
        pass
    
    def collide(self, other_obj):
        pass
    
    def __str__(self):
        my_str = (
            self.object_id + ' [' + self.object_type + ']'
        )
        return(my_str)
        
    __repr__ = __str__

class Sphere_blue(Map_object):
    
    def __init__(self, object_id, world_x, world_y, new_object_func):
        
        Map_object.__init__(self, object_id, 'sphere_blue', world_x, world_y, 0, 0, 50, 50, 0, 10, 'idle', new_object_func, 25)
        
    def get_image(self):
        return('url("get_image/sphere_blue_orig_'+str(int(self.rotation/10)*10)+'.png")')

    def update_state(self,dt):
        pass
    
    def collide(self, other_obj):
        if (other_obj.object_type=='orb'):
            self.state = 'deleted'
            self.new_object_func(Health_drop1(
                    self.object_id + '_health_drop1', 
                    self.world_x,
                    self.world_y,
                    self.new_object_func
                    )
                    )
            
class Health_drop1(Map_object):
    
    def __init__(self, object_id, world_x, world_y, new_object_func):
        
        Map_object.__init__(self, object_id, 'health_drop1', world_x, world_y, 0, 0, 50, 50, 0, 10, 'idle', new_object_func, 25)
        
        self.wiggle_timer = 0
        
    def get_image(self):
        return('url("get_image/health_drop1_orig_'+str(int(self.rotation/10)*10)+'.png")')
        
    def update_state(self,dt):
        self.wiggle_timer = self.wiggle_timer + dt
        
        self.rotation = self.rotation + 20*math.cos(self.wiggle_timer/5*2*math.pi)
        
        if (self.wiggle_timer > 5):
            self.wiggle_timer = 0
            self.rotation = 0
            
    def collide(self, other_obj):
        if (other_obj.object_type=='player'):
            self.state = 'deleted'
            self.new_object_func(Health_collected_floater(
                    self.object_id + '_health_collected_floater', 
                    self.world_x,
                    self.world_y,
                    self.new_object_func
                    )
                    )

class Health_drop2(Health_drop1):
    def __init__(self, object_id, world_x, world_y, new_object_func ):
        Health_drop1.__init__(self, object_id, world_x, world_y, new_object_func )
        self.object_type = 'health_drop2'
        
    def get_image(self):
        return('url("get_image/health_drop2_orig_'+str(int(self.rotation/10)*10)+'.png")')

class Health_drop3(Health_drop1):
    def __init__(self, object_id, world_x, world_y, new_object_func ):
        Health_drop1.__init__(self, object_id, world_x, world_y, new_object_func )
        self.object_type = 'health_drop3'
        
    def get_image(self):
        return('url("get_image/health_drop3_orig_'+str(int(self.rotation/10)*10)+'.png")')

class Health_collected_floater(Map_object):
    
    def __init__(self, object_id, world_x, world_y, new_object_func):
        
        Map_object.__init__(self, object_id, 'health_collected_floater', world_x, world_y, -3, 0, 50, 50, 0, 10, 'idle', new_object_func, 25)
        
        self.timer = 0 
        
    def get_image(self):
        return('url("get_image/health_collected_orig_'+str(int(self.rotation/10)*10)+'.png")')

    def update_state(self,dt):
        self.timer = self.timer + dt
        
        if (self.timer>5):
            self.state = 'deleted'
    
    def collide(self, other_obj):
        pass
    
class Orb(Map_object):
    
    def __init__(self, object_id, world_x, world_y, world_vx, world_vy, new_object_func ):
        
        Map_object.__init__(self, object_id, 'orb', world_x, world_y, world_vx, world_vy, 50, 50, 0, 10, 'fired', new_object_func, 10)
        
        self.timer = 0 
        
    def get_image(self):
        return('url("get_image/orb_orig_'+str(int(self.rotation/10)*10)+'.png")')  
    
    def update_state(self,dt):
        self.timer = self.timer + dt
        
        if (self.timer>50):
            self.state = 'deleted'
            
    def collide(self, other_obj):
        if (not(other_obj.object_type in ['map_tile', 'cloud', 'orb'])):
            self.state = 'deleted'
            self.new_object_func(Cloud_black1(
                    self.object_id + '_cloud_black1', 
                    self.world_x, 
                    self.world_y, 
                    -3, 
                    0
                    )
                    )
            

class Cloud_white1(Map_object):
    
    def __init__(self, object_id, world_x, world_y, world_vx, world_vy ):
        
        Map_object.__init__(self, object_id, 'cloud_white1', world_x, world_y, world_vx, world_vy, 50, 50, int(random.randint(0,35)*10), 10, 'generated', None, 25)
        
        self.timer = 0 
        
    def get_image(self):
        return('url("get_image/white_cloud1_orig_'+str(int(self.rotation/10)*10)+'.png")')  
    
    def update_state(self,dt):
        self.timer = self.timer + dt
        
        if (self.timer>50):
            self.state = 'deleted'
            
    def collide(self, other_obj):
        pass
    
class Cloud_white2(Cloud_white1):
    def __init__(self, object_id, world_x, world_y, world_vx, world_vy ):
        Cloud_white1.__init__(self, object_id, world_x, world_y, world_vx, world_vy )
        self.object_type = 'cloud_white2'
        
    def get_image(self):
        return('url("get_image/white_cloud2_orig_'+str(int(self.rotation/10)*10)+'.png")')
  
class Cloud_white3(Cloud_white1):
    def __init__(self, object_id, world_x, world_y, world_vx, world_vy ):
        Cloud_white1.__init__(self, object_id, world_x, world_y, world_vx, world_vy )
        self.object_type = 'cloud_white3'
        
    def get_image(self):
        return('url("get_image/white_cloud3_orig_'+str(int(self.rotation/10)*10)+'.png")')

class Cloud_black1(Cloud_white1):
    def __init__(self, object_id, world_x, world_y, world_vx, world_vy ):
        Cloud_white1.__init__(self, object_id, world_x, world_y, world_vx, world_vy )
        self.object_type = 'cloud_black1'
        
    def get_image(self):
        return('url("get_image/black_cloud1_orig_'+str(int(self.rotation/10)*10)+'.png")')

class Cloud_black2(Cloud_white1):
    def __init__(self, object_id, world_x, world_y, world_vx, world_vy ):
        Cloud_white1.__init__(self, object_id, world_x, world_y, world_vx, world_vy )
        self.object_type = 'cloud_black2'
        
    def get_image(self):
        return('url("get_image/black_cloud2_orig_'+str(int(self.rotation/10)*10)+'.png")')

class Cloud_black3(Cloud_white1):
    def __init__(self, object_id, world_x, world_y, world_vx, world_vy ):
        Cloud_white1.__init__(self, object_id, world_x, world_y, world_vx, world_vy )
        self.object_type = 'cloud_black3'
        
    def get_image(self):
        return('url("get_image/black_cloud3_orig_'+str(int(self.rotation/10)*10)+'.png")')
        
class Map_tile(Map_object):
    
    def __init__(self, object_id, world_x, world_y, tile_coord_x, tile_coord_y, map_name ):
        
        Map_object.__init__(self, object_id, 'map_tile', world_x, world_y, 0, 0, 50, 50, 0, 1, 'generated', None, 0)
        
        self.tile_coord_x = tile_coord_x
        self.tile_coord_y = tile_coord_y
        self.map_name = map_name
        
    def get_image(self):
        return('url("get_image/'+self.map_name+'_'+str(self.tile_coord_x)+'_'+str(self.tile_coord_y)+'.png")')  
    
    def update_state(self,dt):
        pass
            
    def collide(self, other_obj):
        pass

class Crater1(Map_object):
    
    def __init__(self, object_id, world_x, world_y ):
        
        Map_object.__init__(self, object_id, 'crater1', world_x, world_y, 0, 0, 50, 50, int(random.randint(0,35)*10), 4, 'generated', None, 0)
        
        self.timer = 0 
        
    def get_image(self):
        return('url("get_image/crater1_orig_'+str(int(self.rotation/10)*10)+'.png")')  
    
    def update_state(self,dt):
        self.timer = self.timer + dt
        
        if (self.timer>400):
            self.state = 'deleted'
            
    def collide(self, other_obj):
        pass
    
class Crater2(Cloud_white1):
    def __init__(self, object_id, world_x, world_y):
        Crater1.__init__(self, object_id, world_x, world_y )
        self.object_type = 'crater2'
        
    def get_image(self):
        return('url("get_image/crater2_orig_'+str(int(self.rotation/10)*10)+'.png")')
    
class Crater3(Cloud_white1):
    def __init__(self, object_id, world_x, world_y):
        Crater1.__init__(self, object_id, world_x, world_y )
        self.object_type = 'crater3'
        
    def get_image(self):
        return('url("get_image/crater3_orig_'+str(int(self.rotation/10)*10)+'.png")')
        
        
class Enemy_tower_1(Map_object):
    
    def __init__(self, object_id, world_x, world_y, new_object_func, get_objects_func ):
        
        Map_object.__init__(self, object_id, 'enemy_tower1', world_x, world_y, 0, 0, 50, 50, 0, 10, 'idle', new_object_func, 25)
        
        self.search_timer = 0
        self.fire_timer = 0
        self.fire_interval = 20
        
        self.orb_counter = 0
        
        self.selected_target = None
        
        self.get_objects_func = get_objects_func
        
    def get_image(self):
        return('url("get_image/tower1_orig_'+str(int(self.rotation/10)*10)+'.png")')  
    
    def update_pos(self,dt):
        self.search_timer = self.search_timer + dt
        
        if (self.search_timer > 20):
            self.search_timer = 0
            
            objects_ids, objects_nearby_list = self.get_objects_func(self.world_x, self.world_y, 400, 400)
            
            payers_nearby_list = np.array( [el for el in objects_nearby_list if (
                    (el.object_type=='player')
                )] )
            
            if (len(payers_nearby_list)>0):
                self.selected_target = payers_nearby_list[0]
            else:
                self.selected_target = None
                
        else:
            if ( not(self.selected_target is None) ):
                
                dist = pow(( self.world_x - self.selected_target.world_x )**2+( self.world_y - self.selected_target.world_y )**2,0.5)
                
                target_x = self.selected_target.world_x + dist/10*self.selected_target.world_vx
                target_y = self.selected_target.world_y + dist/10*self.selected_target.world_vy
                
                my_angle = math.atan2( 
                
                        ( self.world_y - target_y ),
                        ( self.world_x - target_x )
                        )/math.pi*180+360
                
                rotation_increment = ( ((my_angle) - int( (my_angle) / 360 )*360) - (self.rotation) )
                
                if (abs(rotation_increment)<10):
                    self.shoot()
                else:
                    self.rotation = self.rotation + (rotation_increment>0)*5*dt - (rotation_increment<0)*5*dt
                
    def shoot(self):
        
        if (not(self.fire_timer<self.fire_interval)):
            
            self.new_object_func(
                    Orb(
                            self.object_id + '_fire_' + str(self.orb_counter), 
                            self.world_x - math.cos(self.rotation/360*2*math.pi)*40, 
                            self.world_y - math.sin(self.rotation/360*2*math.pi)*40,
                            - math.cos(self.rotation/360*2*math.pi)*10, 
                            - math.sin(self.rotation/360*2*math.pi)*10,
                            self.new_object_func
                        )
                    )
            
            self.fire_timer=0
            
            self.orb_counter = self.orb_counter+1
            
            if self.orb_counter > 100:
                self.orb_counter = 0
            
    def update_state(self,dt):
        if (self.fire_timer<20):
            self.fire_timer = self.fire_timer + dt
        
    def collide(self, other_obj):
        if (other_obj.object_type=='orb'):
            self.state = 'deleted'

class Enemy_tower_2(Enemy_tower_1):
    
    def __init__(self, object_id, world_x, world_y, new_object_func, get_objects_func ):
        Enemy_tower_1.__init__(self, object_id, world_x, world_y, new_object_func, get_objects_func )
        self.object_type = 'enemy_tower2'
        self.fire_interval = 10
        
    def get_image(self):
        return('url("get_image/tower2_orig_'+str(int(self.rotation/10)*10)+'.png")') 
    
class Enemy_tower_3(Enemy_tower_1):
    def __init__(self, object_id, world_x, world_y, new_object_func, get_objects_func ):
        Enemy_tower_1.__init__(self, object_id, world_x, world_y, new_object_func, get_objects_func )
        self.object_type = 'enemy_tower3'
        self.fire_interval = 5
        
    def get_image(self):
        return('url("get_image/tower3_orig_'+str(int(self.rotation/10)*10)+'.png")') 
        
class Airship_1(Map_object):

    def __init__(self, object_id, world_x, world_y, new_object_func, get_objects_func ):
        
        Map_object.__init__(self, object_id, 'airship1', world_x, world_y, 0, 0, 50, 50, 0, 10, 'idle', new_object_func, 25)
        
        self.search_timer = 0
        
        self.selected_target = None
        
        self.get_objects_func = get_objects_func
        
        self.speed = 1
        
    def update_pos(self,dt):
        self.search_timer = self.search_timer + dt
        
        if (self.search_timer > 20):
            self.search_timer = 0
            
            objects_ids, objects_nearby_list = self.get_objects_func(self.world_x, self.world_y, 400, 400)
            
            payers_nearby_list = np.array( [el for el in objects_nearby_list if (
                    (el.object_type=='player')
                )] )
            
            if (len(payers_nearby_list)>0):
                self.selected_target = payers_nearby_list[0]
            else:
                self.selected_target = None
                
        else:
            if ( not(self.selected_target is None) ):
                
                dist = pow(( self.world_x - self.selected_target.world_x )**2+( self.world_y - self.selected_target.world_y )**2,0.5)
                
                target_x = self.selected_target.world_x + dist/10*self.selected_target.world_vx
                target_y = self.selected_target.world_y + dist/10*self.selected_target.world_vy
                
                my_angle = math.atan2( 
                
                        ( self.world_y - target_y ),
                        ( self.world_x - target_x )
                        )/math.pi*180+360
                
                rotation_increment = ( ((my_angle) - int( (my_angle) / 360 )*360) - (self.rotation) )
                
                if (abs(rotation_increment)>10):
                    self.rotation = self.rotation + (rotation_increment>0)*5*dt - (rotation_increment<0)*5*dt
                
            self.world_vx = - math.cos(self.rotation/360*2*math.pi)*self.speed
            self.world_vy = - math.sin(self.rotation/360*2*math.pi)*self.speed
            
            self.world_x = self.world_x + self.world_vx*dt
            self.world_y = self.world_y + self.world_vy*dt
            
    def get_image(self):
        return('url("get_image/airship1_orig_'+str(int(self.rotation/10)*10)+'.png")') 
    
    def collide(self, other_obj):
        if (other_obj.object_type in ['orb','player']):
            self.state = 'deleted'
            
class Airship_2(Airship_1):
    def __init__(self, object_id, world_x, world_y, new_object_func, get_objects_func ):
        Airship_1.__init__(self, object_id, world_x, world_y, new_object_func, get_objects_func )
        self.object_type = 'airship2'
        self.speed = 2
        
    def get_image(self):
        return('url("get_image/airship2_orig_'+str(int(self.rotation/10)*10)+'.png")') 

class Airship_3(Airship_1):
    def __init__(self, object_id, world_x, world_y, new_object_func, get_objects_func ):
        Airship_1.__init__(self, object_id, world_x, world_y, new_object_func, get_objects_func )
        self.object_type = 'airship3'
        self.speed = 3.5

    def get_image(self):
        return('url("get_image/airship3_orig_'+str(int(self.rotation/10)*10)+'.png")')   

class Player(Map_object):
    
    def __init__(self, object_id, world_x, world_y, world_vx, world_vy, new_object_func ):
        Map_object.__init__(self, object_id, 'player', world_x, world_y, world_vx, world_vy, 50, 50, 0, 10, 'online', new_object_func, 25)
        self.no_input_count = 0
        self.orb_counter = 0
        self.orb_timer = 0
        self.fire_timer = 0
        self.health = 8
        
    def get_image(self):
        return('url("get_image/plane_orig_'+str(int(self.rotation/10)*10)+'.png")')
    
    def update_pos(self, dt):
        
        controls_raw = con_data_queue.get(str(self.object_id))
        
        if not(controls_raw is None):
            
            self.no_input_count = 0
            
            controls = json.loads( controls_raw )
            
            angle = 180+10*int(math.atan2(float(controls["mouse_x"])-200, float(controls["mouse_y"])-200)/(2*math.pi)*360/10)
            
            self.rotation = angle
            self.world_vx = - math.cos(angle/360*2*math.pi)*3
            self.world_vy = - math.sin(angle/360*2*math.pi)*3
            
            if (controls["mouseDown"]>0):
                self.shoot()
            
        else:
            self.no_input_count = self.no_input_count + 1
            
        self.world_x = self.world_x + self.world_vx*dt
        self.world_y = self.world_y + self.world_vy*dt
    
    def shoot(self):
        
        if (not(self.fire_timer<20)):
            
            self.new_object_func(
                    Orb(
                            self.object_id + '_fire_' + str(self.orb_counter), 
                            self.world_x - math.cos(self.rotation/360*2*math.pi)*50, 
                            self.world_y - math.sin(self.rotation/360*2*math.pi)*50,
                            - math.cos(self.rotation/360*2*math.pi)*10, 
                            - math.sin(self.rotation/360*2*math.pi)*10,
                            self.new_object_func
                        )
                    )
            
            self.fire_timer=0
            
    def update_state(self,dt):
        self.orb_timer = self.orb_timer + dt
        
        if (self.orb_timer>10):
            self.orb_timer = 0
            self.new_object_func(
                    Cloud_white2(
                        self.object_id + '_cloud_white2_' + str(self.orb_counter), 
                        self.world_x+math.cos(self.rotation/360*2*math.pi)*10, 
                        self.world_y+math.sin(self.rotation/360*2*math.pi)*10, 
                        math.cos(self.rotation/360*2*math.pi)*1, 
                        math.sin(self.rotation/360*2*math.pi)*1 
                    )
                )
        
        self.orb_counter = self.orb_counter+1
        
        if self.orb_counter > 100:
            self.orb_counter = 0
            
        if (self.fire_timer<20):
            self.fire_timer = self.fire_timer + dt
        
        if (self.no_input_count*dt > 10):
            self.death('💤 U were logged off due to inactivity!')
        
    def death(self, message):
        
        self.state = 'deleted'
        
        data={}
        data["instruction_data"] = [1]
        data["status_text"] = '_'
        data["infobanner_text"] = '\r\n \r\n \r\n' + message
        
        obj_data_queue.set(self.object_id ,json.dumps(data), px = 200 )
        
    def sustain_damage(self, damage):
        self.health = self.health - damage
        
        if (self.health<=0):
            self.death('😵🔫 You were killed')

    def heal(self, heanth_added):
        self.health = self.health + heanth_added
        if (self.health>8):
            self.health = 8
    
    def collide(self, other_obj):
        if (other_obj.object_type in ['orb','player','airship1','airship2','airship3']):
            self.sustain_damage(1)
            
        if (other_obj.object_type in ['health_box']):
            self.heal(1)
            
    def get_status_text(self):
       
        str_out='\r\n'
        health_bar_string = ''.join(['▓'*(i<self.health)+' '*(i>=self.health) for i in range(0,8)])
        str_out += 'HEALTH ' + health_bar_string + ' \r\n'
        level_bar_string = ''.join(['▓'*(i<(self.fire_timer/20)*8)+' '*(i>=(self.fire_timer/20)*8) for i in range(0,8)])
        str_out += 'CHARGE ' + level_bar_string + ' \r\n'    
        
        return(str_out)
        
class World_map:

    def __init__(self, sz_x, sz_y):
        
        self.dt = 1
        
        self.sz_x = sz_x
        self.sz_y = sz_y
        
        self.object_list = []
        
        for i in range(0,100):
            self.object_list.append(
                    Sphere_blue(
                            'sphere' + str(i), 
                            random.randint(1,sz_x), 
                            random.randint(1,sz_y),
                            self.add_object
                            )
                    )

        for i in range(0,50):
            self.object_list.append(
                    Enemy_tower_1(
                            'enemy_tower1' + str(i), 
                            random.randint(1,sz_x), 
                            random.randint(1,sz_y),
                            self.add_object,
                            self.get_objects
                            )
                    )
        
        for i in range(0,50):
            self.object_list.append(
                    Enemy_tower_2(
                            'enemy_tower2' + str(i), 
                            random.randint(1,sz_x), 
                            random.randint(1,sz_y),
                            self.add_object,
                            self.get_objects
                            )
                    )
                    
        for i in range(0,50):
            self.object_list.append(
                    Enemy_tower_3(
                            'enemy_tower3' + str(i), 
                            random.randint(1,sz_x), 
                            random.randint(1,sz_y),
                            self.add_object,
                            self.get_objects
                            )
                    )   
        for i in range(0,50):
            self.object_list.append(
                    Airship_1(
                            'airship1' + str(i), 
                            random.randint(1,sz_x), 
                            random.randint(1,sz_y),
                            self.add_object,
                            self.get_objects
                            )
                    )   
        for i in range(0,50):
            self.object_list.append(
                    Airship_2(
                            'airship2' + str(i), 
                            random.randint(1,sz_x), 
                            random.randint(1,sz_y),
                            self.add_object,
                            self.get_objects
                            )
                    )   
        for i in range(0,50):
            self.object_list.append(
                    Airship_3(
                            'airship3' + str(i), 
                            random.randint(1,sz_x), 
                            random.randint(1,sz_y),
                            self.add_object,
                            self.get_objects
                            )
                    )   
        for x_id in range(0,100):
            for y_id in range(0,100):
                self.object_list.append(
                        Map_tile('maptile_'+str(x_id)+'_'+str(y_id), x_id*50, y_id*50, x_id, y_id, 'Map1' )
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
        
        #print('adding ' + my_object.object_id)
        
        return 0
        
    def update(self):
        
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
        
        all_visible_object_ids = []
        
        for player_obj in player_obj_list:
            
            object_ids, objects_out = self.get_objects(player_obj.world_x,player_obj.world_y,400,400)
            
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
            
            all_visible_object_ids+=object_ids
            
            #logging_info = log_queue.get(player_obj.object_id)
            #if not(logging_info is None):
            #    print(player_obj.object_id + ': ' + str(logging_info))
            data={}
            data["instruction_data"] = objects
            data["status_text"] = player_obj.get_status_text()
            data["infobanner_text"] = 'None'
            
            obj_data_queue.set(player_obj.object_id ,json.dumps(data), px = 200 )
            
        #handle colidions
        
        self.handle_coliditions( list(dict.fromkeys(all_visible_object_ids)) )
        
        #update objects
        
        visible_ids_deduped = list(dict.fromkeys(all_visible_object_ids))
        
        for obj_id in visible_ids_deduped:
        #for obj_id in range(0,len(self.object_list) ):
            self.object_list[obj_id].update_pos(self.dt)
            self.object_list[obj_id].update_state(self.dt)
        
    def get_objects(self, x_center, y_center, box_h, box_w):    
        
        np_obj_out = np.array( [[el_id, el] for el_id, el in enumerate(self.object_list) if (
                (el.world_x + el.sz_x/2 > x_center - box_h / 2)&
                (el.world_x - el.sz_x/2 < x_center + box_h / 2)&
                (el.world_y + el.sz_y/2 > y_center - box_w / 2)&
                (el.world_y - el.sz_y/2 < y_center + box_w / 2)
            )] )
        
        return(list(np_obj_out[:,0]),list(np_obj_out[:,1]))
        
    def handle_coliditions(self, all_visible_object_ids):
        
        x_coords = np.array( [self.object_list[i_id].world_x for i_id in all_visible_object_ids])
        y_coords = np.array( [self.object_list[i_id].world_y for i_id in all_visible_object_ids])
        col_sz = np.array( [self.object_list[i_id].col_sz for i_id in all_visible_object_ids])
        
        x_coords_2D = np.tile( x_coords,(x_coords.shape[0],1) )
        y_coords_2D = np.tile( y_coords,(y_coords.shape[0],1) )
        col_sz_2 = np.tile( col_sz,(col_sz.shape[0],1) )
        
        dist_mat2 = ( ( x_coords_2D - np.transpose(x_coords_2D) )**2 + ( y_coords_2D - np.transpose(y_coords_2D) )**2 )
        
        coliding_object_ids = np.argwhere( dist_mat2 < (col_sz_2 + np.transpose(col_sz_2))**2 )
        
        for colidion_id in range(0,coliding_object_ids.shape[0]):
            if (not(coliding_object_ids[colidion_id,0] == coliding_object_ids[colidion_id,1])):
                self.object_list[all_visible_object_ids[coliding_object_ids[colidion_id,0]]].collide(self.object_list[all_visible_object_ids[coliding_object_ids[colidion_id,1]]])
        
class my_environment:

    def __init__(self):
        
        self.map = World_map(5000,5000)
        
    def update(self):
        self.map.update()
    
if __name__ == "__main__":
    
    global_environment = my_environment()
    
    while True:
        global_environment.update()
        time.sleep(0.05)