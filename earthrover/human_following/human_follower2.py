"""
Project: AI Robot - Human Following
Author: Jitesh Saini
Github: https://github.com/jiteshsaini
website: https://helloworld.co.in

The code in this file is same as 'human_follower.py' file. However, code with respect to FLASK implementation has been removed.
So there is no streaming of camera view. This is bare minimum human following robot.
"""

import common as cm
import cv2
import numpy as np
from PIL import Image
import time
from threading import Thread

import sys
sys.path.insert(0, '/var/www/html/earthrover')
import util as ut
ut.init_gpio()

cap = cv2.VideoCapture(0)
threshold=0.2
top_k=5 #number of objects to be shown as detected
edgetpu=1

model_dir = '/var/www/html/all_models'
model_edgetpu = 'mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite'
lbl = 'coco_labels.txt'

tolerance=0.1
x_deviation=0
y_max=0

object_to_track='person'

#-----initialise motor speed-----------------------------------

import RPi.GPIO as GPIO 
GPIO.setmode(GPIO.BCM)  # choose BCM numbering scheme  
      
GPIO.setup(20, GPIO.OUT)# set GPIO 20 as output pin
GPIO.setup(21, GPIO.OUT)# set GPIO 21 as output pin
      
pin20 = GPIO.PWM(20, 100)    # create object pin20 for PWM on port 20 at 100 Hertz  
pin21 = GPIO.PWM(21, 100)    # create object pin21 for PWM on port 21 at 100 Hertz  

val=100 # maximum speed
pin20.start(val)              # start pin20 on 0 percent duty cycle (off)  
pin21.start(val)              # start pin21 on 0 percent duty cycle (off)  
    
print("speed set to: ", val)
#------------------------------------------

def track_object(objs,labels):
    
    #global delay
    global x_deviation, y_max, tolerance
    
    
    if(len(objs)==0):
        print("no objects to track")
        ut.stop()
        ut.red_light("OFF")
        return

    flag=0
    for obj in objs:
        lbl=labels.get(obj.id, obj.id)
        if (lbl==object_to_track):
            x_min, y_min, x_max, y_max = list(obj.bbox)
            flag=1
            break
        
    #print(x_min, y_min, x_max, y_max)
    if(flag==0):
        print("selected object no present")
        return
        
    x_diff=x_max-x_min
    y_diff=y_max-y_min
         
    obj_x_center=x_min+(x_diff/2)
    obj_x_center=round(obj_x_center,3)
    
    obj_y_center=y_min+(y_diff/2)
    obj_y_center=round(obj_y_center,3)
    
    x_deviation=round(0.5-obj_x_center,3)
    y_max=round(y_max,3)
        
    print("{",x_deviation,y_max,"}")
   
    thread = Thread(target = move_robot)
    thread.start()
    

def move_robot():
    global x_deviation, y_max, tolerance
    
    y=1-y_max #distance from bottom of the frame
    
    if(abs(x_deviation)<tolerance):
        if(y<0.1):
            ut.red_light("ON")
            ut.stop()
            print("reached person...........")
    
        else:
            ut.red_light("OFF")
            ut.forward()
            print("moving robot ...FORWARD....!!!!!!!!!!!!!!")
    
    
    else:
        ut.red_light("OFF")
        if(x_deviation>=tolerance):
            delay1=get_delay(x_deviation)
                
            ut.left()
            time.sleep(delay1)
            ut.stop()
            print("moving robot ...Left....<<<<<<<<<<")
    
                
        if(x_deviation<=-1*tolerance):
            delay1=get_delay(x_deviation)
                
            ut.right()
            time.sleep(delay1)
            ut.stop()
            print("moving robot ...Right....>>>>>>>>")
    

def get_delay(deviation):
    
    deviation=abs(deviation)
    
    if(deviation>=0.4):
        d=0.080
    elif(deviation>=0.35 and deviation<0.40):
        d=0.060
    elif(deviation>=0.20 and deviation<0.35):
        d=0.050
    else:
        d=0.040
    
    return d

def main():
  
    interpreter, labels =cm.load_model(model_dir,model_edgetpu,lbl,edgetpu)
    
    fps=1
   
    while True:
        start_time=time.time()
        
        #----------------Capture Camera Frame-----------------
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2_im = frame
        cv2_im = cv2.flip(cv2_im, 0)
        cv2_im = cv2.flip(cv2_im, 1)

        cv2_im_rgb = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(cv2_im_rgb)
       
        #-------------------Inference---------------------------------
        cm.set_input(interpreter, pil_im)
        interpreter.invoke()
        objs = cm.get_output(interpreter, score_threshold=threshold, top_k=top_k)
        
        #-----------------other------------------------------------
        track_object(objs,labels)#tracking  <<<<<<<
       
        fps = round(1.0 / (time.time() - start_time),1)
        print("*********FPS: ",fps,"************")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

