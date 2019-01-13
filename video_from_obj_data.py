#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 12 11:16:49 2019

@author: ivanskya
"""

import json
import cv2
import numpy as np
import imageio
import gzip

def my_overlay(canvas,template,x_targ,y_targ):
    
    cx,cy = canvas.shape[0],canvas.shape[1]
    tx,ty = template.shape[0],template.shape[1]
    
    overlay_temp_x_min = (x_targ<=0)*(-x_targ)+(x_targ>0)*0
    overlay_temp_y_min = (y_targ<=0)*(-y_targ)+(y_targ>0)*0
    overlay_temp_x_max = ((x_targ+tx)>=cx)*(tx-(-cx+(x_targ+tx))) + ((x_targ+tx)<cx)*tx
    overlay_temp_y_max = ((y_targ+ty)>=cy)*(ty-(-cy+(y_targ+ty))) + ((y_targ+ty)<cy)*ty
    
    overlay_canv_x_min = max(0,x_targ) 
    overlay_canv_y_min = max(0,y_targ)
    overlay_canv_x_max = min(cx,x_targ + tx)
    overlay_canv_y_max = min(cy,y_targ + ty)

#    print(x_targ)
#    print(y_targ)    
#    print(cx)
#    print(cy)
#    print(tx)
#    print(ty)
#    
#    print(overlay_temp_x_min)
#    print(overlay_temp_y_min)
#    print(overlay_temp_x_max)
#    print(overlay_temp_y_max)
#
#    print(overlay_canv_x_min)
#    print(overlay_canv_y_min)
#    print(overlay_canv_x_max)
#    print(overlay_canv_y_max)
    
    if (template.shape[2]==3):
        canvas[overlay_canv_x_min:overlay_canv_x_max,overlay_canv_y_min:overlay_canv_y_max,0:3] = (
            template[overlay_temp_x_min:overlay_temp_x_max,overlay_temp_y_min:overlay_temp_y_max,0:3]
            )
    
    if (template.shape[2]==4):
            
            canvas[overlay_canv_x_min:overlay_canv_x_max,overlay_canv_y_min:overlay_canv_y_max,0:3] = (
            template[overlay_temp_x_min:overlay_temp_x_max,overlay_temp_y_min:overlay_temp_y_max,0:3]
            *(np.stack((template[overlay_temp_x_min:overlay_temp_x_max,overlay_temp_y_min:overlay_temp_y_max,3],)*3, axis=-1)/ 255.0)
            + canvas[overlay_canv_x_min:overlay_canv_x_max,overlay_canv_y_min:overlay_canv_y_max,0:3]
            *(1.0-np.stack((template[overlay_temp_x_min:overlay_temp_x_max,overlay_temp_y_min:overlay_temp_y_max,3],)*3, axis=-1) / 255.0)
            )
            
    return(canvas)

def write_scoreboard(img, text_in):
    
    text_in = text_in.replace('▓','#')
    
    dy = 8
    x0 = 400-120
    y0 = 10

    for i, line in enumerate(text_in.split('\r\n')):
        
        line = line.replace('\r','')
        line = line.replace('\n','')
        
        y = y0 + i*dy
        cv2.putText(img, line, (x0, y ), cv2.FONT_HERSHEY_SIMPLEX, 0.32, 0.10)
    
    return(img)

def read_json():
    
    writer = imageio.get_writer('log_data/game_recordings/test.mp4', fps=30)
    
    file_name = 'log_data/game_recordings/20190113155605_player_754434.gzip'

    oversample = 3

#    with open(file_name, 'r') as myfile:
#        vid_obj_data = json.loads( myfile.read() )
    
    with gzip.GzipFile( file_name , 'r') as fin:    # 4. gzip
        json_bytes = fin.read()                      # 3. bytes (i.e. UTF-8)
    
    json_str = json_bytes.decode('utf-8')            # 2. string (i.e. JSON)
    vid_obj_data = json.loads(json_str)                      # 1. data
    
    for obj_frame_id in range(0,len(vid_obj_data)-1):
        
        obj_frame = vid_obj_data[obj_frame_id]['raw_activity']
        obj_frame_last = vid_obj_data[obj_frame_id+1]['raw_activity']
        
        blank_image = np.zeros((400,400,3), np.uint8)
        
#        frame_duration = vid_obj_data[obj_frame_id+1]['current_time'] - vid_obj_data[obj_frame_id]['current_time']
#        print(vid_obj_data[obj_frame_id+1]['current_time'])
#        print(vid_obj_data[obj_frame_id]['current_time'])
#        print(frame_duration)
#        
#        oversample = int( (frame_duration/50)+1 )
        
        for oversample_id in range(0,oversample):
            
            try:
                for curr_obj in sorted(obj_frame['instruction_data'], key=lambda curr_obj: curr_obj['zIndex']):
                    
                    x = (curr_obj['top']) 
                    y = (curr_obj['left'])
                    
                    old_ids = [curr_obj_last_o['id'] for curr_obj_last_o in obj_frame_last['instruction_data']]
                    if (curr_obj['id'] in old_ids):
                        old_obj = obj_frame_last['instruction_data'][old_ids.index(curr_obj['id'])]
                        x_old = (old_obj['top']) 
                        y_old = (old_obj['left'])
                        
                        filename = (curr_obj['backgroundImage'][15:-2])
                        img_stamp_filename = 'img/rotations/'+filename
                        
                        if (len(filename)>0):
                            img_stamp = cv2.imread(img_stamp_filename, cv2.IMREAD_UNCHANGED)
                            
                            blank_image = my_overlay(blank_image,img_stamp,int((x_old-x)*oversample_id/oversample+x),int((y_old-y)*oversample_id/oversample+y))
                
                
                
                blank_image = write_scoreboard(blank_image, obj_frame['status_text'])
                
    #            cv2.imwrite('log_data/game_recordings/test_img.png', blank_image)
    #            
                
                blank_image_RGB=np.zeros(blank_image.shape)
                blank_image_RGB[:,:,0]=blank_image[:,:,2]
                blank_image_RGB[:,:,1]=blank_image[:,:,1]
                blank_image_RGB[:,:,2]=blank_image[:,:,0]

            except:
                print('issue parsing the json')
            
            writer.append_data(blank_image_RGB.astype('uint8'))
                    
if __name__ == "__main__":
    read_json()
    