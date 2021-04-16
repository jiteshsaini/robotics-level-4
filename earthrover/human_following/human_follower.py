"""
Project: AI Robot - Human Following
Author: Jitesh Saini
Github: https://github.com/jiteshsaini
website: https://helloworld.co.in

- The robot uses PiCamera to capture a frame. 
- Presence of human in the frame is detected using Machine Learning moldel & TensorFlow Lite interpreter.
- Using OpenCV, the frame is overlayed with information such as bounding boxes, center coordinates of the person, deviation of the person from center of the frame etc.
- FLASK is used for streaming the robot's view over LAN (accessed via browser).
- Google Coral USB Accelerator should be used to accelerate the inferencing process.

When Coral USB Accelerator is connected, amend line 14 of util.py as:-
edgetpu = 1 

When Coral USB Accelerator is not connected, amend line 14 of util.py as:-
edgetpu = 0 

The code moves the robot in order to get closer to the person and bring the person towards center of the frame.
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
top_k=5 #first five objects with prediction probability above threshhold (0.2) to be considered
#edgetpu=0

model_dir = '/var/www/html/all_models'
model = 'mobilenet_ssd_v2_coco_quant_postprocess.tflite'
model_edgetpu = 'mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite'
lbl = 'coco_labels.txt'

tolerance=0.1
x_deviation=0
y_max=0
arr_track_data=[0,0,0,0,0,0]

object_to_track='person'

#---------Flask----------------------------------------
from flask import Flask, Response
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    #return "Default Message"
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    #global cap
    return Response(main(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
                    
#-----initialise motor speed-----------------------------------

import RPi.GPIO as GPIO 
GPIO.setmode(GPIO.BCM)  # choose BCM numbering scheme  
      
GPIO.setup(20, GPIO.OUT)# set GPIO 20 as output pin
GPIO.setup(21, GPIO.OUT)# set GPIO 21 as output pin
      
pin20 = GPIO.PWM(20, 100)    # create object pin20 for PWM on port 20 at 100 Hertz  
pin21 = GPIO.PWM(21, 100)    # create object pin21 for PWM on port 21 at 100 Hertz  

val=100
pin20.start(val)              # start pin20 on 0 percent duty cycle (off)  
pin21.start(val)              # start pin21 on 0 percent duty cycle (off)  
    
print("speed set to: ", val)
#------------------------------------------

def track_object(objs,labels):
   
    global x_deviation, y_max, tolerance, arr_track_data
    
    if(len(objs)==0):
        print("no objects to track")
        ut.stop()
        ut.red_light("OFF")
        arr_track_data=[0,0,0,0,0,0]
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
    print("x_diff: ",round(x_diff,5))
    print("y_diff: ",round(y_diff,5))
        
        
    obj_x_center=x_min+(x_diff/2)
    obj_x_center=round(obj_x_center,3)
    
    obj_y_center=y_min+(y_diff/2)
    obj_y_center=round(obj_y_center,3)
    
    #print("[",obj_x_center, obj_y_center,"]")
        
    x_deviation=round(0.5-obj_x_center,3)
    y_max=round(y_max,3)
        
    print("{",x_deviation,y_max,"}")
   
    thread = Thread(target = move_robot)
    thread.start()
    
    arr_track_data[0]=obj_x_center
    arr_track_data[1]=obj_y_center
    arr_track_data[2]=x_deviation
    arr_track_data[3]=y_max
    

def move_robot():
    global x_deviation, y_max, tolerance, arr_track_data
    
    print("moving robot .............!!!!!!!!!!!!!!")
    print(x_deviation, tolerance, arr_track_data)
    
    y=1-y_max #distance from bottom of the frame
    
    if(abs(x_deviation)<tolerance):
        delay1=0
        if(y<0.1):
            cmd="Stop"
            ut.red_light("ON")
            ut.stop()
        else:
            cmd="forward"
            ut.red_light("OFF")
            ut.forward()
    
    else:
        ut.red_light("OFF")
        if(x_deviation>=tolerance):
            cmd="Move Left"
            delay1=get_delay(x_deviation)
                
            ut.left()
            time.sleep(delay1)
            ut.stop()
                
        if(x_deviation<=-1*tolerance):
            cmd="Move Right"
            delay1=get_delay(x_deviation)
                
            ut.right()
            time.sleep(delay1)
            ut.stop()

    arr_track_data[4]=cmd
    arr_track_data[5]=delay1

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
    
    from util import edgetpu
    
    if (edgetpu==1):
        mdl = model_edgetpu
    else:
         mdl = model
        
    interpreter, labels =cm.load_model(model_dir,mdl,lbl,edgetpu)
    
    fps=1
    arr_dur=[0,0,0]
    
    while True:
        start_time=time.time()
        
        #----------------Capture Camera Frame-----------------
        start_t0=time.time()
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2_im = frame
        cv2_im = cv2.flip(cv2_im, 0)
        cv2_im = cv2.flip(cv2_im, 1)

        cv2_im_rgb = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(cv2_im_rgb)
       
        arr_dur[0]=time.time() - start_t0
        #----------------------------------------------------
       
        #-------------------Inference---------------------------------
        start_t1=time.time()
        cm.set_input(interpreter, pil_im)
        interpreter.invoke()
        objs = cm.get_output(interpreter, score_threshold=threshold, top_k=top_k)
        
        arr_dur[1]=time.time() - start_t1
        #----------------------------------------------------
       
       #-----------------other------------------------------------
        start_t2=time.time()
        track_object(objs,labels)#tracking  <<<<<<<
       
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
 
        cv2_im = append_text_img1(cv2_im, objs, labels, arr_dur, arr_track_data)
       # cv2.imshow('Object Tracking - TensorFlow Lite', cv2_im)
        
        ret, jpeg = cv2.imencode('.jpg', cv2_im)
        pic = jpeg.tobytes()
        
        #Flask streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + pic + b'\r\n\r\n')
       
        arr_dur[2]=time.time() - start_t2
        fps = round(1.0 / (time.time() - start_time),1)
        print("*********FPS: ",fps,"************")

    cap.release()
    cv2.destroyAllWindows()

def append_text_img1(cv2_im, objs, labels, arr_dur, arr_track_data):
    height, width, channels = cv2_im.shape
    font=cv2.FONT_HERSHEY_SIMPLEX
    
    global tolerance
    
    #draw black rectangle on top
    cv2_im = cv2.rectangle(cv2_im, (0,0), (width, 24), (0,0,0), -1)
   
    #write processing durations
    cam=round(arr_dur[0]*1000,0)
    inference=round(arr_dur[1]*1000,0)
    other=round(arr_dur[2]*1000,0)
    text_dur = 'Camera: {}ms   Inference: {}ms   other: {}ms'.format(cam,inference,other)
    cv2_im = cv2.putText(cv2_im, text_dur, (int(width/4)-30, 16),font, 0.4, (255, 255, 255), 1)
    
    #write FPS 
    total_duration=cam+inference+other
    fps=round(1000/total_duration,1)
    text1 = 'FPS: {}'.format(fps)
    cv2_im = cv2.putText(cv2_im, text1, (10, 20),font, 0.7, (150, 150, 255), 2)
   
    
    #draw black rectangle at bottom
    cv2_im = cv2.rectangle(cv2_im, (0,height-24), (width, height), (0,0,0), -1)
    
    #write deviations and tolerance
    str_tol='Tol : {}'.format(tolerance)
    cv2_im = cv2.putText(cv2_im, str_tol, (10, height-8),font, 0.55, (150, 150, 255), 2)
  
    x_dev=arr_track_data[2]
    str_x='X: {}'.format(x_dev)
    if(abs(x_dev)<tolerance):
        color_x=(0,255,0)
    else:
        color_x=(0,0,255)
    cv2_im = cv2.putText(cv2_im, str_x, (110, height-8),font, 0.55, color_x, 2)
    
    y_dev=arr_track_data[3]
    str_y='Y: {}'.format(y_dev)
    if(abs(y_dev)>0.9):
        color_y=(0,255,0)
    else:
        color_y=(0,0,255)
    cv2_im = cv2.putText(cv2_im, str_y, (220, height-8),font, 0.55, color_y, 2)
   
    #write command, tracking status and speed
    cmd=arr_track_data[4]
    cv2_im = cv2.putText(cv2_im, str(cmd), (int(width/2) + 10, height-8),font, 0.68, (0, 255, 255), 2)
    
    delay1=arr_track_data[5]
    str_sp='Speed: {}%'.format(round(delay1/(0.1)*100,1))
    cv2_im = cv2.putText(cv2_im, str_sp, (int(width/2) + 185, height-8),font, 0.55, (150, 150, 255), 2)
    
    if(cmd==0):
        str1="No object"
    elif(cmd=='Stop'):
        str1='Acquired'
    else:
        str1='Tracking'
    cv2_im = cv2.putText(cv2_im, str1, (width-140, 18),font, 0.7, (0, 255, 255), 2)
    
    #draw center cross lines
    cv2_im = cv2.rectangle(cv2_im, (0,int(height/2)-1), (width, int(height/2)+1), (255,0,0), -1)
    cv2_im = cv2.rectangle(cv2_im, (int(width/2)-1,0), (int(width/2)+1,height), (255,0,0), -1)
    
    #draw the center red dot on the object
    cv2_im = cv2.circle(cv2_im, (int(arr_track_data[0]*width),int(arr_track_data[1]*height)), 7, (0,0,255), -1)

    #draw the tolerance box
    cv2_im = cv2.rectangle(cv2_im, (int(width/2-tolerance*width),0), (int(width/2+tolerance*width),height), (0,255,0), 2)
    
    for obj in objs:
        x0, y0, x1, y1 = list(obj.bbox)
        x0, y0, x1, y1 = int(x0*width), int(y0*height), int(x1*width), int(y1*height)
        percent = int(100 * obj.score)
        
        box_color, text_color, thickness=(0,150,255), (0,255,0),1
        

        text3 = '{}% {}'.format(percent, labels.get(obj.id, obj.id))
        
        if(labels.get(obj.id, obj.id)=="person"):
            cv2_im = cv2.rectangle(cv2_im, (x0, y0), (x1, y1), box_color, thickness)
            cv2_im = cv2.putText(cv2_im, text3, (x0, y1-5),font, 0.5, text_color, thickness)
            
    return cv2_im

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2204, threaded=True) # Run FLASK
    main()
