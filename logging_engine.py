#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 17:32:42 2019

@author: ivanskya
"""

import time, datetime
import redis
import json
import copy
import gzip

log_queue = redis.Redis(host='localhost', port=6379, db=3)

class My_log:
    
    def __init__(self, key_name):
        self.key_name = key_name
        self.last_save_date = time.strftime("%Y%m%d", time.gmtime())
        self.buffer_log = ''
        
    def update(self):
        
        log_val = log_queue.rpop(self.key_name)
        
        while (not(log_val is None)):
            
            time_stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            
            self.buffer_log += str(time_stamp) + ', ' + str(log_val.decode("utf-8")) + '\n'
            
            if (len(self.buffer_log) > 50000000) | (not(self.last_save_date == time.strftime("%Y%m%d", time.gmtime()))):
                with open('log_data/' + self.key_name + '_' + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + ".csv", 'w') as f:
                    f.write( self.buffer_log )
                
                self.buffer_log = ''
            
            self.last_save_date = time.strftime("%Y%m%d", time.gmtime())
            log_val = log_queue.rpop(self.key_name)

class Recorder:
        
    def __init__(self):
        self.user_activity = {}
        self.user_start = {}
        self.no_activity_couter = {}
        
    def update(self):
        
        raw_activity = log_queue.lpop('gameplay_log')
        
        while not(raw_activity is None):
        
            act_data = json.loads(raw_activity)
            
            if (act_data['action'] == 'creation'):
                self.add_player(act_data['player_id'])
                
            if (act_data['action'] == 'obj_update'): 
                
                user_id = act_data['player_id']
                
                if (user_id in self.user_activity.keys()):
                
                    self.user_activity[user_id].append( 
                            {
                             "current_time": int((datetime.datetime.now()-self.user_start[user_id]).total_seconds()*1000),
                             "raw_activity": act_data["obj_data"]
                            } 
                        )
                    
                    self.no_activity_couter[user_id] = 0
                else:
                    self.add_player(user_id)
                
                for user_id_other in self.user_activity.keys():
                    if not(user_id_other==user_id):
                        self.no_activity_couter[user_id_other] += 1 
                    
                        if (int((self.no_activity_couter[user_id_other]) / len(self.user_activity.keys()) ) > 1000):
                            self.delete_player(user_id_other)
                
            if (act_data['action'] == 'death'):
                self.delete_player(act_data['player_id'])
            
            raw_activity = log_queue.lpop('gameplay_log')
            
    def add_player(self,user_id):
        self.user_activity[user_id] = []
        self.user_start[user_id] = datetime.datetime.now()
        self.no_activity_couter[user_id] = 0

    def delete_player(self,user_id):
        with gzip.open(
                'log_data/game_recordings/' 
                + time.strftime("%Y%m%d%H%M%S", time.gmtime())  
                + '_' + user_id
                + ".gzip", 
                'wt', 
                encoding="ascii"
                ) as zipfile:
            json.dump(self.user_activity[user_id], zipfile)
        
        self.user_activity.pop(user_id, None)
        self.user_start.pop(user_id, None)
        self.no_activity_couter.pop(user_id, None)
                
if __name__ == "__main__":
    
    log_list = [My_log('website_log'), Recorder()]
    
    while True:
        for log_item in log_list:
            log_item.update()
            
        time.sleep(0.05)