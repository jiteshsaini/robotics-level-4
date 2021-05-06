# Example code provided by TensorFlow Authors have been useful in creating this project.
# Author: Jitesh Saini
# Project: Earth Rover (Real Time Image classifiation)

from tflite_runtime.interpreter import Interpreter
import numpy as np
from PIL import Image
from time import sleep
import cv2
import os

cap = cv2.VideoCapture(0)

font=cv2.FONT_HERSHEY_SIMPLEX
text_overlay=""

       
#---------Flask----------------------------------------
from flask import Flask, Response
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    #return "Default Message"
    return render_template("index1.html")

@app.route('/video_feed')
def video_feed():
    #global cap
    return Response(main(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
                    
#-------------------------------------------------------------

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

threshold=0.35
#-----------------------------------------------------------

#----initialise GPIO----------------------------
import sys
sys.path.insert(0, '/var/www/html/earthrover')
import util as ut
ut.init_gpio()
#-----------------------------------------------

def action(pred,lbl):
        global text_overlay
        
        if (pred < threshold):
                text_overlay = "__"
                ut.camera_light("OFF")
                
        if (pred >= threshold):
                percent=round(pred*100)
                text_overlay= "Saw a " + lbl + ", i am " + str(percent) + "% sure"
                #ut.speak_tts(lbl,"f")
                #sleep(1)
                #text_to_speech(lbl,"f")
                ut.camera_light("ON")
                
def input_image_size(interpreter):
    """Returns input image size as (width, height, channels) tuple."""
    _, height, width, channels = interpreter.get_input_details()[0]['shape']
    return width, height, channels

def main():
        while True:
        
                ret, frame = cap.read()
                if not ret:
                    break
                
                cv2_im = frame
                cv2_im = cv2.flip(cv2_im, 0)
                cv2_im = cv2.flip(cv2_im, 1)

                cv2_im_rgb = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
                pil_im = Image.fromarray(cv2_im_rgb)
                
                image = pil_im.resize((input_image_size(interpreter)[0:2]), Image.NEAREST)
                
                # Add a batch dimension
                input_data = np.expand_dims(image, axis=0)
                
                
                #print(input_data)
                
                # feed data to input tensor and run the interpreter
                interpreter.set_tensor(input_details[0]['index'], input_data)
                interpreter.invoke()

                # Obtain results and map them to the classes
                predictions = interpreter.get_tensor(output_details[0]['index'])[0]
                
                # Get indices of the top k results
                top_k_indices = np.argsort(predictions)[::-1][:top_k_results]

                j=0
                for i in range(top_k_results):
                    pred=predictions[top_k_indices[i]]/255.0
                    pred=round(pred,2)
                    lbl=labels[top_k_indices[i]]
                    print(lbl, "=", pred)
                    
                    txt1=lbl + "(" + str(pred) + ")"
                    cv2_im = cv2.rectangle(cv2_im, (25,45 + j*35), (160, 65 + j*35), (0,0,0), -1)
                    cv2_im = cv2.putText(cv2_im, txt1, (30, 60 + j*35),font, 0.5, (255, 255, 255), 1)
                    j=j+1
                    
                pred_max=predictions[top_k_indices[0]]/255.0
                lbl_max=labels[top_k_indices[0]]
                
                #print(lbl_max, "=", pred_max)
                
                #take action based on maximum prediction value
                action(pred_max,lbl_max)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                #cv2.imshow('Real-time Image Classification', cv2_im)
                cv2_im = cv2.putText(cv2_im, text_overlay, (60, 30),font, 0.8, (0, 0, 255), 2)
                
                ret, jpeg = cv2.imencode('.jpg', cv2_im)
                pic = jpeg.tobytes()
        
                #Flask streaming
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + pic + b'\r\n\r\n')
               
                print("-----------------------------------")
                
                #sleep(0.5)
                
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
        app.run(host='0.0.0.0', port=2204, threaded=True) # Run FLASK
        main()
