# python3
#
# Copyright 2019 The TensorFlow Authors. All Rights Reserved.


# Modified by: Jitesh Saini
# Project: Earth Rover (Real Time Image classifiation)

from tflite_runtime.interpreter import Interpreter
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

import picamera
from picamera import PiCamera, Color
from time import sleep

def scale_image(frame, new_size=(224, 224)):
  # Get the dimensions
  height, width, _ = frame.shape # Image shape
  new_width, new_height = new_size # Target shape 

  # Calculate the target image coordinates
  left = (width - new_width) // 2
  top = (height - new_height) // 2
  right = (width + new_width) // 2
  bottom = (height + new_height) // 2
  
  #print("left:", left)
  #print("right:", right)
  #print("top:", top)
  #print("bottom:", bottom)
  
  image = frame[left: right, top: bottom, :]
  return image

def move_back():
        ut.back()
        sleep(3)
        ut.stop()

def move_forward():
        ut.forward()
        sleep(3)
        ut.stop()

def action(pred,lbl):
        #print("max_prediction: ", pred)
        #print("max_Label: ", lbl)
        
        if (pred < threshold):
                camera.annotate_text = "___"
                ut.camera_light("OFF")
                
        if (pred >= threshold):
                percent=round(pred*100)
                txt= "Saw a " + lbl + ", i am " + str(percent) + "% sure"
                camera.annotate_text = txt
                
                ut.speak_tts(lbl,"f")
                sleep(0.3)
                
        if (pred >= threshold and lbl=="mouse"):
                print(lbl)
                ut.camera_light("ON")
                move_back()
                
        if (pred >= threshold and lbl=="tennis ball"):
                print(lbl)
                ut.camera_light("ON")
                move_forward()


#----initialise GPIO----------------------------
import sys
sys.path.insert(0, '/var/www/html/earthrover')
import util as ut
ut.init_gpio()
#-----------------------------------------------

#-----initialise the Model and Load into interpreter-------------------------

#specify the path of Model and Label file
model_path = "/var/www/html/all_models/mobilenet_v1_1.0_224_quant.tflite" 
label_path = "/var/www/html/all_models/labels_mobilenet_quant_v1_224.txt"
top_k_results = 3

with open(label_path, 'r') as f:
    labels = list(map(str.strip, f.readlines()))

# Load TFLite model and allocate tensors
interpreter = Interpreter(model_path=model_path)
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

## Get input size
input_shape = input_details[0]['shape']
#print(input_shape)
size = input_shape[:2] if len(input_shape) == 3 else input_shape[1:3]
#print(size)

#prediction threshold for triggering actions
threshold=0.5
#-----------------------------------------------------------

#-------Window to display camera view---------------------
plt.ion()
plt.tight_layout()
	
fig = plt.gcf()
fig.canvas.set_window_title('TensorFlow Lite')
fig.suptitle('Earth Rover: Image Classification')
ax = plt.gca()
ax.set_axis_off()
tmp = np.zeros([480,640] + [3], np.uint8)
preview = ax.imshow(tmp)
#---------------------------------------------------------

with picamera.PiCamera() as camera:
    camera.framerate = 30
    camera.resolution = (640, 480)
    camera.annotate_foreground = Color('black')
    
    #loop continuously (press control + 'c' to exit program)
    while True:
        stream = np.empty((480, 640, 3), dtype=np.uint8)
        camera.capture(stream, 'rgb')
        
        img = scale_image(stream)
        
        # Add a batch dimension
        input_data = np.expand_dims(img, axis=0)
        #print(input_data)
        
        # feed data to input tensor and run the interpreter
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        # Obtain results and map them to the classes
        predictions = interpreter.get_tensor(output_details[0]['index'])[0]
        
        # Get indices of the top k results
        top_k_indices = np.argsort(predictions)[::-1][:top_k_results]

        
        for i in range(top_k_results):
            pred=predictions[top_k_indices[i]]/255.0
            pred=round(pred,2)
            lbl=labels[top_k_indices[i]]
            print(lbl, "=", pred)
            
        print("-----------------------------------")
        
        pred_max=predictions[top_k_indices[0]]/255.0
        lbl_max=labels[top_k_indices[0]]
        
        #take action based on maximum prediction value
        action(pred_max,lbl_max)
        
        #update the window of camera view 
        preview.set_data(stream)
        fig.canvas.get_tk_widget().update()
        
camera.close()
