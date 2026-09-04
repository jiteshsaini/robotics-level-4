"""
Project: AI Robot - Object Detection
Author: Jitesh Saini
Github: https://github.com/jiteshsaini
website: https://helloworld.co.in

The code does following:-
- The robot uses PiCamera to capture frames. 
- An object within the frame is detected using Machine Learning moldel & TensorFlow Lite interpreter. 
- Using OpenCV, the frame is overlayed with information such as: color coded bounding boxes, information bar to show FPS, Processing durations and an Object Counter.
- Display the output window (camera view with overlays) locally on Raspberry Pi

"""

import common1 as cm
# highgui removed: this runs against opencv-python-headless, which has no
# window support. waitKey/imshow/destroyAllWindows raise cv2.error there,
# and were no-ops in a windowless server loop anyway.
import cv2
import numpy as np
from PIL import Image
import time

import sys
sys.path.insert(0, '/var/www/html/earthrover')


# cv2.VideoCapture cannot read the CSI camera on Bookworm/Trixie
# (/dev/video0 is unicam, raw Bayer). camera_compat picks a working
# backend: V4L2 for USB webcams, picamera2 for the ribbon camera.
import camera_compat
cap = camera_compat.VideoCapture(0)
threshold=0.2
top_k=10 #number of objects to be shown as detected

model_dir = '/var/www/html/all_models'
model = 'mobilenet_ssd_v2_coco_quant_postprocess.tflite'
model_edgetpu = 'mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite'
lbl = 'coco_labels.txt'

counter=0
prev_val=0

selected_obj="person"

def show_selected_object_counter(objs,labels):
    global counter, prev_val, selected_obj
    arr=[]
    for obj in objs:
        #print(obj.id)
        label = labels.get(obj.id, obj.id)
        #print(label)
        arr.append(label)
            
    print("arr:",arr)
    
    x = arr.count(selected_obj)
    
    diff=x - prev_val
    
    print("diff:",diff)
    if(diff>0):
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
       
            
        cv2_im = cm.append_text_img1(cv2_im, objs, labels, arr_dur, counter,selected_obj)
        # cv2.imshow removed - headless OpenCV has no window support
        
        #time.sleep(0.5)
       
        arr_dur[2]=time.time() - start_t2
        cm.time_elapsed(start_t2,"other")
        cm.time_elapsed(start_time,"overall")
        
        print("arr_dur:",arr_dur)
        fps = round(1.0 / (time.time() - start_time),1)
        print("*********FPS: ",fps,"************")

    cap.release()


if __name__ == '__main__':
    main()
