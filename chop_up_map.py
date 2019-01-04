#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 13:40:03 2019

@author: ivanskya
"""

import os
import numpy as np
import cv2

def chop_up_map():
    

    file_path = 'img/orig/maps/Map1.png'

    print('processing file: "' + file_path + '"')
    
    img_large = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    
    rows,cols,depth = img_large.shape
    
    for x_start in range(0,int(rows/50)):
        for y_start in range(0,int(cols/50)):
    
            img_small = img_large[(x_start*50):((x_start*50)+50),(y_start*50):((y_start*50)+50)]
    
            cv2.imwrite('img/rotations/Map1'+'_'+str(x_start)+'_'+str(y_start)+'.png', img_small)
    
if __name__ == "__main__":
    chop_up_map()