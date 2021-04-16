"""
Project: AI Robot - Object Detection
Author: Jitesh Saini
Github: https://github.com/jiteshsaini
website: https://helloworld.co.in

- The robot uses PiCamera to capture frames. 
- An object within the frame is detected using Machine Learning moldel & TensorFlow Lite interpreter. 
- Using OpenCV, the frame is overlayed with information such as: color coded bounding boxes, information bar to show FPS, Processing durations and an Object Counter.
- The frame with overlays is streamed over LAN using FLASK. The Flask stream is embedded into a Web GUI which can be accessed at "http://192.168.1.20/earthrover/object_detection/web". IP '192.168.1.20' should be replaced with your RPi's IP
- You can select an object through Web GUI to generate alarm on a specific object.
- Google Coral USB Accelerator can be used to accelerate the inferencing process.

When Coral USB Accelerator is connected, amend line 14 of util.py as:-
edgetpu = 1 

When Coral USB Accelerator is not connected, amend line 14 of util.py as:-
edgetpu = 0 

"""

import common1 as cm
import cv2
import numpy as np
from PIL import Image
import time

import sys
sys.path.insert(0, '/var/www/html/earthrover')
import util as ut
ut.init_gpio()

cap = cv2.VideoCapture(0)
threshold=0.2
top_k=5 #number of objects to be shown as detected

model_dir = '/var/www/html/all_models'
model = 'mobilenet_ssd_v2_coco_quant_postprocess.tflite'
model_edgetpu = 'mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite'
lbl = 'coco_labels.txt'

counter=0
prev_val=0

file_path="/var/www/html/earthrover/object_detection/web/"
selected_obj=""
prev_val_obj=""

#---------Flask----------------------------------------
from flask import Flask, Response
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    #return "Default Message"
    return render_template("index2.html")

@app.route('/video_feed')
def video_feed():
    #global cap
    return Response(main(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
                    
#-------------------------------------------------------------

    
def show_selected_object_counter(objs,labels):
    global counter, prev_val
    global file_path,selected_obj,prev_val_obj
    
    arr=[]
    for obj in objs:
        #print(obj.id)
        label = labels.get(obj.id, obj.id)
        #print(label)
        arr.append(label)
            
    print("arr:",arr)
    
    
    f0 = open(file_path + "object_cmd.txt", "r+")
    selected_obj = f0.read(20);
    f0.close()
    
    if(selected_obj!=prev_val_obj):
        counter=0
    
    prev_val_obj=selected_obj
    
    
    print("selected_obj: ",selected_obj)

    
    x = arr.count(selected_obj) #no of occurances of selected object in array of objects detected by the model
    f1 = open(file_path + "object_found.txt", "w")
    f1.write(str(x))
    f1.close()
    
    if(x>0):#selected object present in frame. Make GPIO pin high
        ut.camera_light("ON") 
    else:#selected object absent in frame. Make GPIO pin Low
        ut.camera_light("OFF")
        
    diff=x - prev_val #detect change in the no of occurances of selected object w.r.t previous frame
    
    print("diff:",diff)
    if(diff>0): #if there is an change then update counter
        counter=counter + diff
        
    prev_val = x
    
    print("counter:",counter)
    

def main():
    from util import edgetpu
    
    if (edgetpu==1):
        mdl = model_edgetpu
    else:
         mdl = model
        
    interpreter, labels =cm.load_model(model_dir,mdl,lbl,edgetpu)
    
    fps=1
    arr_dur=[0,0,0]
    #while cap.isOpened():
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
        cm.time_elapsed(start_t0,"camera capture")
        #----------------------------------------------------
       
        #-------------------Inference---------------------------------
        start_t1=time.time()
        cm.set_input(interpreter, pil_im)
        interpreter.invoke()
        objs = cm.get_output(interpreter, score_threshold=threshold, top_k=top_k)
        
        arr_dur[1]=time.time() - start_t1
        cm.time_elapsed(start_t1,"inference")
        #----------------------------------------------------
       
       #-----------------other------------------------------------
        start_t2=time.time()
        show_selected_object_counter(objs,labels)#counter  <<<<<<<
       
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        
        cv2_im = cm.append_text_img1(cv2_im, objs, labels, arr_dur, counter,selected_obj)
        #cv2.imshow('Object Detection - TensorFlow Lite', cv2_im)
        
        ret, jpeg = cv2.imencode('.jpg', cv2_im)
        pic = jpeg.tobytes()
        
        #Flask streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + pic + b'\r\n\r\n')
       
        arr_dur[2]=time.time() - start_t2
        cm.time_elapsed(start_t2,"other")
        cm.time_elapsed(start_time,"overall")
        
        print("arr_dur:",arr_dur)
        fps = round(1.0 / (time.time() - start_time),1)
        print("*********FPS: ",fps,"************")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2204, threaded=True) # Run FLASK
    main()
