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

class Helper(object):
    def get_rotated_img_string(img_name,rotation):
        
        rotation = rotation - int(rotation/360)*360
        
        str_out = 'url("get_image/' + img_name + '_'+str(int(rotation/10)*10)+'.png")'

        return(str_out)

    def get_unique_id(Map_object):
        
        global last_object_id
        
        if 'last_object_id' in globals():
            last_object_id = last_object_id + 1
        else:
            last_object_id = 0
            
        return(Map_object.object_class + '_' + Map_object.object_type + '_' + str(last_object_id))
    
class Map_object:
    
    def __init__(self, object_type, object_class, world_x, world_y, world_vx, world_vy, sz_x, sz_y, rotation, z_index, state, new_object_func, col_sz):
        
        self.object_type = object_type
        self.object_class = object_class
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
        self.backgroundColor = ''  
        self.textContent = ''
        
        self.object_id = Helper.get_unique_id(self)
        
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

class Map_object_decor(Map_object):

    def __init__(self, object_type, world_x, world_y, world_vx, world_vy, sz_x, sz_y, rotation, z_index, state, new_object_func, col_sz):
        Map_object.__init__(
                self,
                object_type = object_type, 
                object_class = 'decorative', 
                world_x = world_x, 
                world_y = world_y, 
                world_vx = world_vx, 
                world_vy = world_vy, 
                sz_x = sz_x, 
                sz_y = sz_y, 
                rotation = rotation, 
                z_index = z_index, 
                state = state, 
                new_object_func = new_object_func, 
                col_sz = col_sz
                )

class Map_object_enemy(Map_object):

    def __init__(self, object_type, world_x, world_y, world_vx, world_vy, sz_x, sz_y, rotation, z_index, state, new_object_func,get_objects_func, col_sz):
        Map_object.__init__(
                self,
                object_type = object_type, 
                object_class = 'enemy', 
                world_x = world_x, 
                world_y = world_y, 
                world_vx = world_vx, 
                world_vy = world_vy, 
                sz_x = sz_x, 
                sz_y = sz_y, 
                rotation = rotation, 
                z_index = z_index, 
                state = state, 
                new_object_func = new_object_func, 
                col_sz = col_sz
                )
        self.get_objects_func = get_objects_func

class Map_object_explosive(Map_object):

    def __init__(self, object_type, world_x, world_y, world_vx, world_vy, sz_x, sz_y, rotation, z_index, state, new_object_func, col_sz):
        Map_object.__init__(
                self,
                object_type = object_type, 
                object_class = 'explosive', 
                world_x = world_x, 
                world_y = world_y, 
                world_vx = world_vx, 
                world_vy = world_vy, 
                sz_x = sz_x, 
                sz_y = sz_y, 
                rotation = rotation, 
                z_index = z_index, 
                state = state, 
                new_object_func = new_object_func, 
                col_sz = col_sz
                )

class Map_object_item(Map_object):

    def __init__(self, object_type, world_x, world_y, sz_x, sz_y, rotation, z_index, state, new_object_func, col_sz):
        Map_object.__init__(
                self,
                object_type = object_type, 
                object_class = 'item', 
                world_x = world_x, 
                world_y = world_y, 
                world_vx = 0, 
                world_vy = 0, 
                sz_x = sz_x, 
                sz_y = sz_y, 
                rotation = rotation, 
                z_index = z_index, 
                state = state, 
                new_object_func = new_object_func, 
                col_sz = col_sz
                )

class Map_object_player(Map_object):
    
    def __init__(self, object_type, world_x, world_y, world_vx, world_vy, sz_x, sz_y, rotation, z_index, state, new_object_func, col_sz):
        Map_object.__init__(
                self,
                object_type = object_type, 
                object_class = 'player', 
                world_x = world_x, 
                world_y = world_y, 
                world_vx = world_vx, 
                world_vy = world_vy, 
                sz_x = sz_x, 
                sz_y = sz_y, 
                rotation = rotation, 
                z_index = z_index, 
                state = state, 
                new_object_func = new_object_func, 
                col_sz = col_sz
                )

class Sphere_blue(Map_object_item):
    
    def __init__(self, world_x, world_y, new_object_func):
        
        Map_object_item.__init__( 
            self,
            object_type = 'Sphere_blue', 
            world_x = world_x, 
            world_y = world_y, 
            sz_x = 50, 
            sz_y= 50, 
            rotation = 0, 
            z_index = 10, 
            state = 'idle', 
            new_object_func = new_object_func, 
            col_sz = 25
         )
        
    def get_image(self):
        #return('url("get_image/sphere_blue_orig_'+str(int(self.rotation/10)*10)+'.png")')
        return(Helper.get_rotated_img_string('sphere_blue_orig', self.rotation))
        
    def update_state(self,dt):
        pass
    
    def collide(self, other_obj):
        if not(other_obj.object_class in 'decorative'):
            self.state = 'deleted'
            self.new_object_func(Health_drop1( 
                    self.world_x,
                    self.world_y,
                    self.new_object_func
                    )
                    )
            
class Health_drop1(Map_object_item):
    
    def __init__(self, world_x, world_y, new_object_func):
        
        Map_object_item.__init__( 
            self,
            object_type = 'Health_drop1', 
            world_x = world_x, 
            world_y = world_y, 
            sz_x = 50, 
            sz_y= 50, 
            rotation = 0, 
            z_index = 10, 
            state = 'idle', 
            new_object_func = new_object_func, 
            col_sz = 25
         )
        
#        self.wiggle_timer = 0
        
    def get_image(self):
        #return('url("get_image/health_drop1_orig_'+str(int(self.rotation/10)*10)+'.png")')
        return(Helper.get_rotated_img_string('health_drop1_orig', self.rotation))
#    def update_state(self,dt):
#        self.wiggle_timer = self.wiggle_timer + dt
#        
#        self.rotation = 20*math.sin(self.wiggle_timer/20*2*math.pi) + 360
#        self.rotation = self.rotation - int(self.rotation/360)*360
#        
#        if (self.wiggle_timer > 20):
#            self.wiggle_timer = 0
#            self.rotation = 0
            
    def collide(self, other_obj):
        if (other_obj.object_class=='player'):
            self.state = 'deleted'
            self.new_object_func(Health_collected_floater(
                    self.world_x,
                    self.world_y,
                    self.new_object_func
                    )
                    )

class Health_drop2(Health_drop1):
    def __init__(self, world_x, world_y, new_object_func ):
        Health_drop1.__init__(self, world_x, world_y, new_object_func )
        self.object_type = 'Health_drop2'
        
    def get_image(self):
        #return('url("get_image/health_drop2_orig_'+str(int(self.rotation/10)*10)+'.png")')
        return(Helper.get_rotated_img_string('health_drop2_orig', self.rotation))

class Health_drop3(Health_drop1):
    def __init__(self, world_x, world_y, new_object_func ):
        Health_drop1.__init__(self, world_x, world_y, new_object_func )
        self.object_type = 'Health_drop3'
        
    def get_image(self):
        #return('url("get_image/health_drop3_orig_'+str(int(self.rotation/10)*10)+'.png")')
        return(Helper.get_rotated_img_string('health_drop3_orig', self.rotation))

class Health_collected_floater(Map_object_decor):
    
    def __init__(self, world_x, world_y, new_object_func):
        
        Map_object_decor.__init__( 
            self,
            object_type = 'Health_collected_floater', 
            world_x = world_x, 
            world_y = world_y, 
            world_vx = -3, 
            world_vy = 0, 
            sz_x = 50, 
            sz_y= 50, 
            rotation = 0, 
            z_index = 11, 
            state = 'idle', 
            new_object_func = new_object_func, 
            col_sz = 25
         )
        
        self.timer = 0 
        
    def get_image(self):
        #return('url("get_image/health_collected_orig_'+str(int(self.rotation/10)*10)+'.png")')
        return(Helper.get_rotated_img_string('health_collected_orig', self.rotation))
        
    def update_state(self,dt):
        self.timer = self.timer + dt
        
        if (self.timer>5):
            self.state = 'deleted'
    
    def collide(self, other_obj):
        pass
    
class Orb(Map_object_explosive):
    
    def __init__(self, world_x, world_y, world_vx, world_vy, new_object_func ):
        
        Map_object_explosive.__init__(
            self, 
            object_type = 'Orb', 
            world_x = world_x, 
            world_y = world_y, 
            world_vx = world_vx, 
            world_vy = world_vy, 
            sz_x = 50, 
            sz_y = 50, 
            rotation = 0, 
            z_index = 12, 
            state = 'fired', 
            new_object_func = new_object_func , 
            col_sz = 5
         )
        
        self.timer = 0 
        
    def get_image(self):
        #return('url("get_image/orb_orig_'+str(int(self.rotation/10)*10)+'.png")')  
        return(Helper.get_rotated_img_string('orb_orig', self.rotation))
        
    def update_state(self,dt):
        self.timer = self.timer + dt
        
        if (self.timer>40):
            self.state = 'deleted'
            
    def collide(self, other_obj):
        if (( not(other_obj.object_class in ['decorative'])) & (not(other_obj.object_class in ['explosive']))):
            self.state = 'deleted'
            self.new_object_func(Cloud_black2(
                    self.world_x, 
                    self.world_y, 
                    -3, 
                    0
                    )
                    )
            

class Cloud_white1(Map_object_decor):
    
    def __init__(self, world_x, world_y, world_vx, world_vy ):
        
        Map_object_decor.__init__( 
            self,
            object_type = 'Cloud_white1', 
            world_x = world_x, 
            world_y = world_y, 
            world_vx = world_vx, 
            world_vy = world_vy, 
            sz_x = 50, 
            sz_y= 50, 
            rotation = int(random.randint(0,35)*10), 
            z_index = 11, 
            state = 'idle', 
            new_object_func = None, 
            col_sz = 25
         )
        
        self.timer = 0 
        
    def get_image(self):
        #return('url("get_image/white_cloud1_orig_'+str(int(self.rotation/10)*10)+'.png")')  
        return(Helper.get_rotated_img_string('white_cloud1_orig', self.rotation))
    def update_state(self,dt):
        self.timer = self.timer + dt
        
        if (self.timer>50):
            self.state = 'deleted'
            
    def collide(self, other_obj):
        pass
    
class Cloud_white2(Cloud_white1):
    def __init__(self, world_x, world_y, world_vx, world_vy ):
        Cloud_white1.__init__(self, world_x, world_y, world_vx, world_vy )
        self.object_type = 'Cloud_white2'
        
    def get_image(self):
        #return('url("get_image/white_cloud2_orig_'+str(int(self.rotation/10)*10)+'.png")')
        return(Helper.get_rotated_img_string('white_cloud2_orig', self.rotation))
class Cloud_white3(Cloud_white1):
    def __init__(self, world_x, world_y, world_vx, world_vy ):
        Cloud_white1.__init__(self, world_x, world_y, world_vx, world_vy )
        self.object_type = 'Cloud_white3'
        
    def get_image(self):
        #return('url("get_image/white_cloud3_orig_'+str(int(self.rotation/10)*10)+'.png")')
        return(Helper.get_rotated_img_string('white_cloud3_orig', self.rotation))
        
class Cloud_black1(Cloud_white1):
    def __init__(self, world_x, world_y, world_vx, world_vy ):
        Cloud_white1.__init__(self, world_x, world_y, world_vx, world_vy )
        self.object_type = 'Cloud_black1'
        
    def get_image(self):
        return('url("get_image/black_cloud1_orig_'+str(int(self.rotation/10)*10)+'.png")')

class Cloud_black2(Cloud_white1):
    def __init__(self, world_x, world_y, world_vx, world_vy ):
        Cloud_white1.__init__(self, world_x, world_y, world_vx, world_vy )
        self.object_type = 'Cloud_black2'
        
    def get_image(self):
        #return('url("get_image/black_cloud2_orig_'+str(int(self.rotation/10)*10)+'.png")')
        return(Helper.get_rotated_img_string('black_cloud2_orig', self.rotation))
        
class Cloud_black3(Cloud_white1):
    def __init__(self, world_x, world_y, world_vx, world_vy ):
        Cloud_white1.__init__(self, world_x, world_y, world_vx, world_vy )
        self.object_type = 'Cloud_black3'
        
    def get_image(self):
        #return('url("get_image/black_cloud3_orig_'+str(int(self.rotation/10)*10)+'.png")')
        return(Helper.get_rotated_img_string('black_cloud3_orig', self.rotation))
        
class Explosion1(Cloud_white1):
    def __init__(self, world_x, world_y, world_vx, world_vy ):
        Cloud_white1.__init__(self, world_x, world_y, world_vx, world_vy )
        self.object_type = 'Explosion1'
        
    def get_image(self):
        #return('url("get_image/explosion1_orig_'+str(int(self.rotation/10)*10)+'.png")')
        return(Helper.get_rotated_img_string('explosion1_orig', self.rotation))
        
class Explosion2(Cloud_white1):
    def __init__(self, world_x, world_y, world_vx, world_vy ):
        Cloud_white1.__init__(self, world_x, world_y, world_vx, world_vy )
        self.object_type = 'Explosion2'
        
    def get_image(self):
        #return('url("get_image/explosion2_orig_'+str(int(self.rotation/10)*10)+'.png")')
        return(Helper.get_rotated_img_string('explosion2_orig', self.rotation))
        
class Explosion3(Cloud_white1):
    def __init__(self, world_x, world_y, world_vx, world_vy ):
        Cloud_white1.__init__(self, world_x, world_y, world_vx, world_vy )
        self.object_type = 'Explosion3'
        
    def get_image(self):
        #return('url("get_image/explosion3_orig_'+str(int(self.rotation/10)*10)+'.png")')
        return(Helper.get_rotated_img_string('explosion3_orig', self.rotation))
        
class Map_tile(Map_object_decor):
    
    def __init__(self, world_x, world_y, tile_coord_x, tile_coord_y, map_name ):
        
        Map_object_decor.__init__( 
            self, 
            object_type = 'Map_tile', 
            world_x = world_x, 
            world_y = world_y, 
            world_vx = 0, 
            world_vy = 0, 
            sz_x = 50, 
            sz_y= 50, 
            rotation = 0, 
            z_index = 1, 
            state = 'idle', 
            new_object_func = None, 
            col_sz = 25
        )
        
        self.tile_coord_x = tile_coord_x
        self.tile_coord_y = tile_coord_y
        self.map_name = map_name

    def get_image(self):
        return('url("get_image/'+self.map_name+'_'+str(self.tile_coord_x)+'_'+str(self.tile_coord_y)+'.png")')  
        
    def update_state(self,dt):
        pass
            
    def collide(self, other_obj):
        pass

class Crater1(Map_object_decor):
    
    def __init__(self, world_x, world_y ):
        
        Map_object_decor.__init__( 
            self,
            object_type = 'Crater1', 
            world_x = world_x, 
            world_y = world_y, 
            world_vx = 0, 
            world_vy = 0, 
            sz_x = 50, 
            sz_y= 50, 
            rotation = int(random.randint(0,35)*10), 
            z_index = 4, 
            state = 'idle', 
            new_object_func = None, 
            col_sz = 25
        )
        
        self.timer = 0 
        
    def get_image(self):
        #return('url("get_image/crater1_orig_'+str(int(self.rotation/10)*10)+'.png")')  
        return(Helper.get_rotated_img_string('crater1_orig', self.rotation))
        
    def update_state(self,dt):
        self.timer = self.timer + dt
        
        if (self.timer>500):
            self.state = 'deleted'
            
    def collide(self, other_obj):
        pass
    
class Crater2(Crater1):
    def __init__(self, world_x, world_y):
        Crater1.__init__(self, world_x, world_y )
        self.object_type = 'Crater2'
        
    def get_image(self):
        #return('url("get_image/crater2_orig_'+str(int(self.rotation/10)*10)+'.png")')
        return(Helper.get_rotated_img_string('crater2_orig', self.rotation))
    
class Crater3(Crater1):
    def __init__(self, world_x, world_y):
        Crater1.__init__(self, world_x, world_y )
        self.object_type = 'Crater3'
        
    def get_image(self):
        #return('url("get_image/crater3_orig_'+str(int(self.rotation/10)*10)+'.png")')
        return(Helper.get_rotated_img_string('crater3_orig', self.rotation))
        
class Enemy_tower_1(Map_object_enemy):
    
    def __init__(self, world_x, world_y, new_object_func, get_objects_func ):
        
        Map_object_enemy.__init__(
            self, 
            object_type = 'Enemy_tower_1', 
            world_x = world_x, 
            world_y = world_y, 
            world_vx = 0, 
            world_vy = 0, 
            sz_x = 50, 
            sz_y = 50, 
            rotation = 0, 
            z_index = 20, 
            state = 'idle', 
            new_object_func = new_object_func, 
            get_objects_func = get_objects_func,
            col_sz = 25
            )
        
        self.search_timer = 0
        self.fire_timer = 0
        self.fire_interval = 20
        
        self.selected_target = None
        
    def get_image(self):
        #return('url("get_image/tower1_orig_'+str(int(self.rotation/10)*10)+'.png")')  
        return(Helper.get_rotated_img_string('tower1_orig', self.rotation))
        
    def update_pos(self,dt):
        self.search_timer = self.search_timer + dt
        
        if (self.search_timer > 20):
            self.search_timer = 0
            
            objects_ids, objects_nearby_list = self.get_objects_func(self.world_x, self.world_y, 400, 400)
            
            payers_nearby_list = np.array( [el for el in objects_nearby_list if (
                    (el.object_class=='player')
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
                            self.world_x - math.cos(self.rotation/360*2*math.pi)*40, 
                            self.world_y - math.sin(self.rotation/360*2*math.pi)*40,
                            - math.cos(self.rotation/360*2*math.pi)*10, 
                            - math.sin(self.rotation/360*2*math.pi)*10,
                            self.new_object_func
                        )
                    )
            self.new_object_func(
                Cloud_black1(
                    self.world_x - math.cos(self.rotation/360*2*math.pi)*40, 
                    self.world_y - math.sin(self.rotation/360*2*math.pi)*40,
                    -3, 
                    0
                    )
                )
                    
            self.fire_timer=0
            
    def update_state(self,dt):
        if (self.fire_timer<20):
            self.fire_timer = self.fire_timer + dt
        
    def collide(self, other_obj):
        if not(other_obj.object_class in ['decorative']):
            self.state = 'deleted'
            
            self.new_object_func(
                    Crater1(
                            self.world_x, 
                            self.world_y 
                        )
                    )
            
            self.new_object_func(Cloud_black2(
                    self.world_x, 
                    self.world_y, 
                    -3, 
                    0
                    )
                    )
            if (other_obj.object_class in ['explosive']):
                self.new_object_func(Explosion2(
                        self.world_x, 
                        self.world_y, 
                        -2, 
                        0
                        )
                        )
    
                self.new_object_func(Health_drop1(
                        self.world_x + int(random.randint(0,50)-25), 
                        self.world_y + int(random.randint(0,50)-25), 
                        self.new_object_func
                        )
                        )

class Enemy_tower_2(Enemy_tower_1):
    
    def __init__(self, world_x, world_y, new_object_func, get_objects_func ):
        Enemy_tower_1.__init__(self, world_x, world_y, new_object_func, get_objects_func )
        self.object_type = 'Enemy_tower_2'
        self.fire_interval = 10
        
    def get_image(self):
        #return('url("get_image/tower2_orig_'+str(int(self.rotation/10)*10)+'.png")') 
        return(Helper.get_rotated_img_string('tower2_orig', self.rotation))
        
    def collide(self, other_obj):
        if not(other_obj.object_class in ['decorative']):
            self.state = 'deleted'
            
            self.new_object_func(
                    Crater2(
                            self.world_x, 
                            self.world_y 
                        )
                    )
            self.new_object_func(Cloud_black2(
                    self.world_x, 
                    self.world_y, 
                    -3, 
                    0
                    )
                    )
            if (other_obj.object_class in ['explosive']):
                self.new_object_func(Explosion2(
                        self.world_x, 
                        self.world_y, 
                        -2, 
                        0
                        )
                        )
    
                self.new_object_func(Health_drop2( 
                        self.world_x + int(random.randint(0,50)-25), 
                        self.world_y + int(random.randint(0,50)-25), 
                        self.new_object_func
                        )
                        )

class Enemy_tower_3(Enemy_tower_1):
    def __init__(self, world_x, world_y, new_object_func, get_objects_func ):
        Enemy_tower_1.__init__(self, world_x, world_y, new_object_func, get_objects_func )
        self.object_type = 'Enemy_tower_3'
        self.fire_interval = 5
        
    def get_image(self):
        #return('url("get_image/tower3_orig_'+str(int(self.rotation/10)*10)+'.png")') 
        return(Helper.get_rotated_img_string('tower3_orig', self.rotation))
        
    def collide(self, other_obj):
        if not(other_obj.object_class in ['decorative']):
            self.state = 'deleted'
            
            self.new_object_func(
                    Crater3(
                            self.world_x, 
                            self.world_y 
                        )
                    )
            self.new_object_func(Cloud_black3(
                    self.world_x, 
                    self.world_y, 
                    -3, 
                    0
                    )
                    )

            self.new_object_func(Explosion3(
                    self.world_x, 
                    self.world_y, 
                    -2, 
                    0
                    )
                    )
                    
            if (other_obj.object_class in ['explosive']):
                self.new_object_func(Health_drop1(
                        self.world_x + int(random.randint(0,50)-25), 
                        self.world_y + int(random.randint(0,50)-25), 
                        self.new_object_func
                        )
                        )
    
                self.new_object_func(Health_drop2(
                        self.world_x + int(random.randint(0,50)-25), 
                        self.world_y + int(random.randint(0,50)-25), 
                        self.new_object_func
                        )
                        )
                        
class Airship_1(Map_object_enemy):

    def __init__(self, world_x, world_y, new_object_func, get_objects_func ):
        
        Map_object_enemy.__init__(
            self, 
            object_type = 'Airship_1', 
            world_x = world_x, 
            world_y = world_y, 
            world_vx = 0, 
            world_vy = 0, 
            sz_x = 50, 
            sz_y = 50, 
            rotation = 0, 
            z_index = 20, 
            state = 'idle', 
            new_object_func = new_object_func, 
            get_objects_func = get_objects_func,
            col_sz = 25
            )
        
        self.search_timer = 0
        
        self.selected_target = None
        
        self.speed = 1
        
    def update_pos(self,dt):
        self.search_timer = self.search_timer + dt
        
        if (self.search_timer > 20):
            self.search_timer = 0
            
            objects_ids, objects_nearby_list = self.get_objects_func(self.world_x, self.world_y, 400, 400)
            
            payers_nearby_list = np.array( [el for el in objects_nearby_list if (
                    (el.object_class=='player')
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
        #return('url("get_image/airship1_orig_'+str(int(self.rotation/10)*10)+'.png")') 
        return(Helper.get_rotated_img_string('airship1_orig', self.rotation))
        
    def collide(self, other_obj):
        if not(other_obj.object_class in 'decorative'):
            self.state = 'deleted'
            
            self.new_object_func(Cloud_black3(
                    self.world_x, 
                    self.world_y, 
                    -3, 
                    0
                    )
                    )

            self.new_object_func(Explosion3(
                    self.world_x, 
                    self.world_y, 
                    -2, 
                    0
                    )
                    )
            
class Airship_2(Airship_1):
    def __init__(self, world_x, world_y, new_object_func, get_objects_func ):
        Airship_1.__init__(self, world_x, world_y, new_object_func, get_objects_func )
        self.object_type = 'Airship_2'
        self.speed = 2
        
    def get_image(self):
        #return('url("get_image/airship2_orig_'+str(int(self.rotation/10)*10)+'.png")') 
        return(Helper.get_rotated_img_string('airship2_orig', self.rotation))
        
class Airship_3(Airship_1):
    def __init__(self, world_x, world_y, new_object_func, get_objects_func ):
        Airship_1.__init__(self, world_x, world_y, new_object_func, get_objects_func )
        self.object_type = 'Airship_3'
        self.speed = 3.5

    def get_image(self):
        #return('url("get_image/airship3_orig_'+str(int(self.rotation/10)*10)+'.png")')   
        return(Helper.get_rotated_img_string('airship3_orig', self.rotation))

class Text_label(Map_object_decor):
    
    def __init__(self, obj_follow, text_in ):
        Map_object_decor.__init__(
                self, 
                object_type = 'Text_label', 
                world_x = obj_follow.world_x, 
                world_y = obj_follow.world_y, 
                world_vx = 0, 
                world_vy = 0, 
                sz_x = 50, 
                sz_y = 20, 
                rotation = 0, 
                z_index = 11, 
                state = 'active', 
                new_object_func = None, 
                col_sz = 25)
        
        self.obj_follow = obj_follow
        self.textContent = text_in
        self.backgroundColor = ''
        
    def update_pos(self, dt):
            
        if not(self.obj_follow.state == 'deleted'):
            
            self.world_x = self.obj_follow.world_x + 30
            self.world_y = self.obj_follow.world_y
        else:
            self.state = 'deleted'
    
    def get_image(self):
        return('')
    
class Player(Map_object_player):
    
    def __init__(self, object_id, world_x, world_y, world_vx, world_vy, new_object_func ):
        Map_object_player.__init__(
                self, 
                object_type = 'Player', 
                world_x = world_x, 
                world_y = world_y, 
                world_vx = world_vx, 
                world_vy = world_vy, 
                sz_x = 50, 
                sz_y = 50, 
                rotation = 0, 
                z_index = 11, 
                state = 'online', 
                new_object_func = new_object_func, 
                col_sz = 25)
        
        self.object_id = object_id
        self.no_input_count = 0
        self.orb_counter = 0
        self.orb_timer = 0
        self.fire_timer = 0
        self.health = 8
        
        self.new_object_func(Text_label(self, self.object_id))
        
        log_queue.lpush(
            'gameplay_log', 
            json.dumps( 
                    {
                        'action':'login',
                        'player_id':object_id
                    } 
                ) 
            )
        
    def get_image(self):
        #return('url("get_image/plane_orig_'+str(int(self.rotation/10)*10)+'.png")')
        return(Helper.get_rotated_img_string('plane_orig', self.rotation))
        
    def update_pos(self, dt):
        
        controls_raw = con_data_queue.get(str(self.object_id))
        
        if not(controls_raw is None):
            
            self.no_input_count = 0
            
            controls = json.loads( controls_raw )
            
            angle = 180+10*int(math.atan2(float(controls["mouse_x"])-200, float(controls["mouse_y"])-200)/(2*math.pi)*360/10)
            
            self.rotation = angle
            
            self.world_vx = - math.cos(angle/360*2*math.pi)*3
            self.world_vy = - math.sin(angle/360*2*math.pi)*3
            
            if ((self.world_x > (5000-200)) & (self.world_vx>0)):
                self.world_vx = 0

            if ((self.world_x < (0+200)) & (self.world_vx<0)):
                self.world_vx = 0

            if ((self.world_y > (5000-200)) & (self.world_vy>0)):
                self.world_vy = 0

            if ((self.world_y < (0+200)) & (self.world_vy<0)):
                self.world_vy = 0
            
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
        
        if (self.orb_timer>5):
            self.orb_timer = 0
            self.new_object_func(
                    Cloud_white2(
                        self.world_x+math.cos(self.rotation/360*2*math.pi)*30, 
                        self.world_y+math.sin(self.rotation/360*2*math.pi)*30, 
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

        log_queue.lpush(
            'gameplay_log', 
            json.dumps( 
                    {
                        'action':'logout',
                        'player_id': self.object_id,
                        'message':message
                    } 
                ) 
            )
            
    def sustain_damage(self, damage):
        self.health = self.health - damage

        self.new_object_func(Cloud_black3(
                self.world_x, 
                self.world_y, 
                -3, 
                0
                )
                )

        self.new_object_func(Explosion3(
                self.world_x, 
                self.world_y, 
                -2, 
                0
                )
                )
    
        if (self.health<=0):
            self.death("😵🔫 You've been killed")

    def heal(self, heanth_added):
        self.health = self.health + heanth_added
        if (self.health>8):
            self.health = 8
    
    def collide(self, other_obj):
        if ( 
            (not(other_obj.object_class in 'decorative')) 
            & (not(other_obj.object_type in ['Health_drop1','Health_drop2','Health_drop3']) )
            ):
            self.sustain_damage(1)
            
        if (other_obj.object_type == 'Health_drop1'):
            self.heal(1)

        if (other_obj.object_type == 'Health_drop2'):
            self.heal(2)

        if (other_obj.object_type == 'Health_drop3'):
            self.heal(3)
         
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
        
        self.population_counts = {
                "Sphere_blue":200,
                "Enemy_tower_1":300,
                "Enemy_tower_2":100,
                "Enemy_tower_3":50,
                "Airship_1":300,
                "Airship_2":80,
                "Airship_3":20,
                }
        
        for x_id in range(0,100):
            for y_id in range(0,100):
                self.object_list.append(
                        Map_tile(
                            x_id*50, 
                            y_id*50, 
                            x_id, 
                            y_id, 
                            'Map1' 
                            )
                        )
                        
        self.balance_population()
                        
    def place_object(self, object_type):
        
        if (object_type=='Sphere_blue'):
            self.object_list.append(
                    Sphere_blue(
                            random.randint(1,self.sz_x), 
                            random.randint(1,self.sz_y),
                            self.add_object
                            )
                    )

        if (object_type=='Enemy_tower_1'):
            self.object_list.append(
                    Enemy_tower_1(
                            random.randint(1,self.sz_x), 
                            random.randint(1,self.sz_y),
                            self.add_object,
                            self.get_objects
                            )
                    )
        
        if (object_type=='Enemy_tower_2'):
            self.object_list.append(
                    Enemy_tower_2(
                            random.randint(1,self.sz_x), 
                            random.randint(1,self.sz_y),
                            self.add_object,
                            self.get_objects
                            )
                    )
                    
        if (object_type=='Enemy_tower_3'):
            self.object_list.append(
                    Enemy_tower_3(
                            random.randint(1,self.sz_x), 
                            random.randint(1,self.sz_y),
                            self.add_object,
                            self.get_objects
                            )
                    )   
        if (object_type=='Airship_1'):
            self.object_list.append(
                    Airship_1(
                            random.randint(1,self.sz_x), 
                            random.randint(1,self.sz_y),
                            self.add_object,
                            self.get_objects
                            )
                    )   
        if (object_type=='Airship_2'):
            self.object_list.append(
                    Airship_2( 
                            random.randint(1,self.sz_x), 
                            random.randint(1,self.sz_y),
                            self.add_object,
                            self.get_objects
                            )
                    )   
        if (object_type=='Airship_3'):
            self.object_list.append(
                    Airship_3(
                            random.randint(1,self.sz_x), 
                            random.randint(1,self.sz_y),
                            self.add_object,
                            self.get_objects
                            )
                    )   
    
    def balance_population(self):
        
        object_type_list = [el.object_type for el in self.object_list if not(el.object_class in ['decorative','player','explosive'])]
        
        occurrences = dict(zip( 
                        [el for el in set(object_type_list)],[object_type_list.count(el) for el in set(object_type_list)] 
                    ))
        
        for obj_type in list(self.population_counts):
            if obj_type in occurrences.keys():
                if (occurrences[obj_type] < self.population_counts[obj_type]):
                    for i in range(0, self.population_counts[obj_type] - occurrences[obj_type]):
                        self.place_object(obj_type)
            else:
                self.place_object(obj_type)
        
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
            if (not(new_player_id in [el.object_id for el in self.object_list if (el.object_class=='player')])):
                self.add_object( Player(new_player_id, 2500, 2500, 0, 0, self.add_object ) )
                
        #send players their data
        
        player_obj_list = [el for el in self.object_list if (el.object_class=='player')]
        
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
                objects[len(objects)-1]['top'] = obj_out.world_x - player_obj.world_x - obj_out.sz_y/2 + 200
                objects[len(objects)-1]['left'] = obj_out.world_y - player_obj.world_y - obj_out.sz_x/2 + 200
                objects[len(objects)-1]['backgroundColor'] = obj_out.backgroundColor
                objects[len(objects)-1]['backgroundImage'] = obj_out.get_image()
                objects[len(objects)-1]['zIndex'] = obj_out.z_index
                objects[len(objects)-1]['textContent'] = obj_out.textContent
                
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
            self.object_list[obj_id].update_pos(self.dt)
        
        for obj_id in range(0,len(self.object_list) ):
            self.object_list[obj_id].update_state(self.dt)
        
        #replace deleted / destroyed objects
        self.balance_population()
        
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
    
    obj_data_queue.flushall()
    con_data_queue.flushall()
    user_data_queue.flushall()
        
    global_environment = my_environment()
    
    while True:
        global_environment.update()
        time.sleep(0.05)