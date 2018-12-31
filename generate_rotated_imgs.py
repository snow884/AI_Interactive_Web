#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 19:44:26 2018

@author: ivanskya
"""

import os
import numpy as np
import cv2

def generate_rotated_images():
    
    file_path_list = ['img/orig/' + x for x in os.listdir('img/orig/')]
    
    print(file_path_list)
    
    for file_path in file_path_list:
    
        if (file_path[-3:]=='png'):
            
            print('processing file: "' + file_path + '"')
            
            for i in range(0,36):
                
                img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
                    
                my_angle = i*10
                
                rows,cols,depth = img.shape
                
                M = cv2.getRotationMatrix2D((cols/2,rows/2),my_angle,1)
                
                dst = cv2.warpAffine(img,M,(cols,rows))
                
                cv2.imwrite(file_path[0:-4].replace('/orig/','/rotations/')+'_'+str(my_angle)+'.png', dst)
        
if __name__ == "__main__":
    generate_rotated_images()