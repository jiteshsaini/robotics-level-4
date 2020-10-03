"""
This file has utility functions which are used in the following three files:-
1. object_detection.py
2. object_detection_web1.py
3. object_detection_web2.py

This file is imported in all the above three files.

This code is based on Google-Coral Object Detection example code available at:
https://github.com/google-coral/examples-camera/tree/master/opencv

"""
import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite
import platform


EDGETPU_SHARED_LIB = {
  'Linux': 'libedgetpu.so.1',
  'Darwin': 'libedgetpu.1.dylib',
  'Windows': 'edgetpu.dll'
}[platform.system()]

def make_interpreter_0(model_file):
    model_file, *device = model_file.split('@')
    return tflite.Interpreter(model_path=model_file)

def make_interpreter_1(model_file):
    model_file, *device = model_file.split('@')
    return tflite.Interpreter(
      model_path=model_file,
      experimental_delegates=[
          tflite.load_delegate(EDGETPU_SHARED_LIB,
                               {'device': device[0]} if device else {})
      ])

def set_input(interpreter, image, resample=Image.NEAREST):
    """Copies data to input tensor."""
    image = image.resize((input_image_size(interpreter)[0:2]), resample)
    input_tensor(interpreter)[:, :] = image

def input_image_size(interpreter):
    """Returns input image size as (width, height, channels) tuple."""
    _, height, width, channels = interpreter.get_input_details()[0]['shape']
    return width, height, channels

def input_tensor(interpreter):
    """Returns input tensor view as numpy array of shape (height, width, 3)."""
    tensor_index = interpreter.get_input_details()[0]['index']
    return interpreter.tensor(tensor_index)()[0]

def output_tensor(interpreter, i):
    """Returns dequantized output tensor if quantized before."""
    output_details = interpreter.get_output_details()[i]
    output_data = np.squeeze(interpreter.tensor(output_details['index'])())
    if 'quantization' not in output_details:
        return output_data
    scale, zero_point = output_details['quantization']
    if scale == 0:
        return output_data - zero_point
    return scale * (output_data - zero_point)

import time
def time_elapsed(start_time,event):
        time_now=time.time()
        duration = (time_now - start_time)*1000
        duration=round(duration,2)
        print (">>> ", duration, " ms (" ,event, ")")

import os
def load_model(model_dir,model, lbl, edgetpu):
    
    print('Loading from directory: {} '.format(model_dir))
    print('Loading Model: {} '.format(model))
    print('Loading Labels: {} '.format(lbl))
    
    model_path=os.path.join(model_dir,model)
    labels_path=os.path.join(model_dir,lbl)
    
    if(edgetpu==0):
        interpreter = make_interpreter_0(model_path)
    else:
        interpreter = make_interpreter_1(model_path)
    
    interpreter.allocate_tensors()
    
    labels = load_labels(labels_path)
    
    return interpreter, labels
    
import re
def load_labels(path):
    p = re.compile(r'\s*(\d+)(.+)')
    with open(path, 'r', encoding='utf-8') as f:
       lines = (p.match(line).groups() for line in f.readlines())
       return {int(num): text.strip() for num, text in lines}
       
#----------------------------------------------------------------------
import collections
Object = collections.namedtuple('Object', ['id', 'score', 'bbox'])

class BBox(collections.namedtuple('BBox', ['xmin', 'ymin', 'xmax', 'ymax'])):
    """Bounding box.
    Represents a rectangle which sides are either vertical or horizontal, parallel
    to the x or y axis.
    """
    __slots__ = ()

def get_output(interpreter, score_threshold, top_k, image_scale=1.0):
    """Returns list of detected objects."""
    boxes = output_tensor(interpreter, 0)
    class_ids = output_tensor(interpreter, 1)
    scores = output_tensor(interpreter, 2)
    count = int(output_tensor(interpreter, 3))

    def make(i):
        ymin, xmin, ymax, xmax = boxes[i]
        return Object(
            id=int(class_ids[i]),
            score=scores[i],
            bbox=BBox(xmin=np.maximum(0.0, xmin),
                      ymin=np.maximum(0.0, ymin),
                      xmax=np.minimum(1.0, xmax),
                      ymax=np.minimum(1.0, ymax)))

    return [make(i) for i in range(top_k) if scores[i] >= score_threshold]
#--------------------------------------------------------------------

import cv2

def append_text_img1(cv2_im, objs, labels, arr_dur, counter, selected_obj):
    height, width, channels = cv2_im.shape
    font=cv2.FONT_HERSHEY_SIMPLEX
    
    cam=round(arr_dur[0]*1000,0)
    inference=round(arr_dur[1]*1000,0)
    other=round(arr_dur[2]*1000,0)
    
    #total_duration=arr_dur[0] + arr_dur[1] + arr_dur[2]
    total_duration=cam+inference+other
    
    fps=round(1000/total_duration,1)
    
    cv2_im = cv2.rectangle(cv2_im, (0,0), (width, 24), (0,0,0), -1)

    text1 = 'FPS: {}'.format(fps)
    cv2_im = cv2.putText(cv2_im, text1, (10, 20),font, 0.7, (0, 0, 255), 2)
    
    #text_dur = 'Camera: {}ms, Inference {}ms, other {}ms'.format(arr_dur[0]*1000,arr_dur[1]*1000,arr_dur[2]*1000)
    text_dur = 'Camera: {}ms   Inference: {}ms   other: {}ms'.format(cam,inference,other)
    
    cv2_im = cv2.putText(cv2_im, text_dur, (int(width/4)-30, 16),font, 0.4, (255, 255, 255), 1)
    
    
    #object_name="person"
    text2 = selected_obj + ': {}'.format(counter)
    cv2_im = cv2.putText(cv2_im, text2, (width-140, 20),font, 0.6, (0, 255, 0), 2)
                             
    for obj in objs:
        x0, y0, x1, y1 = list(obj.bbox)
        x0, y0, x1, y1 = int(x0*width), int(y0*height), int(x1*width), int(y1*height)
        percent = int(100 * obj.score)
        
        if (percent>=60):
            box_color, text_color, thickness=(0,255,0), (0,255,0),2
        elif (percent<60 and percent>40):
            box_color, text_color, thickness=(0,0,255), (0,0,255),2
        else:
            box_color, text_color, thickness=(255,0,0), (255,0,0),1
            
       
        text3 = '{}% {}'.format(percent, labels.get(obj.id, obj.id))
        
        cv2_im = cv2.rectangle(cv2_im, (x0, y0), (x1, y1), box_color, thickness)
        cv2_im = cv2.putText(cv2_im, text3, (x0, y1-5),font, 0.5, text_color, thickness)
        
    return cv2_im
