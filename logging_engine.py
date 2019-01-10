#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 17:32:42 2019

@author: ivanskya
"""

import time
import redis

log_queue = redis.Redis(host='localhost', port=6379, db=3)

class My_log:
    
    def __init__(self, key_name):
        self.key_name = key_name
        self.last_save_date = time.strftime("%Y%m%d", time.gmtime())
    
    def update(self):
        
        log_val = log_queue.rpop(self.key_name)
        buffer_log = ''
        
        while (not(log_val is None)):
        
            time_stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            
            buffer_log += str(time_stamp) + ', ' + str(log_val.decode("utf-8")) + '\n'
            
            print(log_val)
            
            if (len(buffer_log) > 50000000) | (not(self.curr_date == time.strftime("%Y%m%d", time.gmtime()))):
                with open('log_data/' + self.key_name + '_' + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + ".csv", 'w') as f:
                    f.write( buffer_log )
                    
                buffer_log = ''
            
            self.curr_date = time.strftime("%Y%m%d", time.gmtime())
            log_val = log_queue.rpop(self.key_name)
            
if __name__ == "__main__":
    
    log_list = [My_log('website_log'),My_log('gameplay_log')]
    
    while True:
        for log_item in log_list:
            log_item.update()
    time.sleep(0.5)