"""
Author: Jitesh Saini

This code is based on Google-Coral Object Detection example code available at:
https://github.com/google-coral/examples-camera/tree/master/opencv

The example code has been modified to implements following:-
1. Object Detection with colour coded bounding boxes
2. Added information bar on top of the output window to show FPS, Processing duration and an Object Counter
3. Streaming of output window is achieved through FLASK. Added a a html file named 'index2.html' in directory named 'templates'.
4. The object name is fetched from a txt file for updating the Object Counter. The txt file is updated through Web GUI. 

Run this Python file through terminal and access Web GUI through http://192.168.1.20/earthrover/object_detection/web

Note: IP address '192.168.1.20' should be replaced with your RPi's IP
"""

import common1 as cm
import cv2
import numpy as np
from PIL import Image
import time

cap = cv2.VideoCapture(0)
threshold=0.2
top_k=5 #number of objects to be shown as detected
edgetpu=0

#default_model_dir = '../all_models
model_dir = '/home/pi/Documents/all_models'
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

    
    x = arr.count(selected_obj)
    f1 = open(file_path + "object_found.txt", "w")
    f1.write(str(x))
    f1.close()
    
    diff=x - prev_val
    
    print("diff:",diff)
    if(diff>0):
        counter=counter + diff
    
    prev_val = x
    
    print("counter:",counter)
    

def main():
    
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
