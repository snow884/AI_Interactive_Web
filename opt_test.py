#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 22:20:21 2019

@author: ivanskya
"""

import numpy as np
import math
import matplotlib.pyplot as plt

sz = 100

lin_arr = np.linspace(-3, 3, num=sz, endpoint=False, retstep=False, dtype=None)

x = np.tile(lin_arr,(sz,1))
y = np.transpose(x)

player_coords = [0,0]

root_list_x = [-1,1,-1,1]
root_list_y = [-1,-1,1,1]

my_path_x = []
my_path_y = []

x_curr = -1.2
y_curr = -2

def my_func(x_curr,y_curr,root_list_x,root_list_y):
    
    dx_opt_func =  0
    dy_opt_func =  0
    
    opt_func = 0
    
    dx_opt_func += -1 * - 2*(x_curr) / ( (x_curr)**2 + (y_curr)**2 )**2
    dy_opt_func += -1 * - 2*(y_curr) / ( (x_curr)**2 + (y_curr)**2 )**2
    
    opt_func += -1 / ( (x_curr)**2 + (y_curr)**2 )
    
    for i in range(0,len(root_list_x)):
        dx_opt_func += - 2*(x_curr-root_list_x[i]) / ( (x_curr-root_list_x[i])**2 + (y_curr-root_list_y[i])**2 )**2
        dy_opt_func += - 2*(y_curr-root_list_y[i]) / ( (x_curr-root_list_x[i])**2 + (y_curr-root_list_y[i])**2 )**2
        
        opt_func += 1 / ( (x_curr-root_list_x[i])**2 + (y_curr-root_list_y[i])**2 )
        
        dx_opt_func += -1 * - 2*(x_curr) / ( (x_curr)**2 + (y_curr)**2 )**2
        dy_opt_func += -1 * - 2*(y_curr) / ( (x_curr)**2 + (y_curr)**2 )**2
        
        opt_func += -1 / ( (x_curr)**2 + (y_curr)**2 )
        
    if (opt_func>1000):
        opt_func = 0
        
    return(opt_func,dx_opt_func,dy_opt_func)

z=np.zeros((sz,sz))

for x_id,x_coord in enumerate(lin_arr):
    for y_id,y_coord in enumerate(lin_arr):
        z_val,dx_opt_func,dy_opt_func = my_func(x_coord,y_coord,root_list_x,root_list_y)
        z[x_id,y_id] = z_val
        
plt.pcolormesh(x, y, z)
plt.show()        

for my_iter in range(0,2000):
    
    z,dx_opt_func,dy_opt_func = my_func(x_curr,y_curr,root_list_x,root_list_y)
        
    angle = math.atan2(dx_opt_func, dy_opt_func)
    
    x_curr = x_curr - math.sin(angle)*0.05
    y_curr = y_curr - math.cos(angle)*0.05
    
    my_path_x.append(x_curr)
    my_path_y.append(y_curr)
    
plt.plot(my_path_x, my_path_y)
plt.scatter(root_list_x, root_list_y)
plt.scatter(player_coords[0], player_coords[1])
plt.show()

