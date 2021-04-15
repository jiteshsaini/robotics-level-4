# AI Robot: Object Detection with TensorFlow Lite on Raspberry Pi & Live-Stream results on browser 

<p align="left">
Read the article: <a href='https://helloworld.co.in/article/ai-robot-object-detection-tensorflow-lite-raspberry-pi-live-stream-results-browser' target='_blank'>
   <img src='https://github.com/jiteshsaini/files/blob/main/img/logo3.gif' height='40px'>
</a> Watch the video on Yotube: 
<a href='https://youtu.be/1pnUkhIL7QA' target='_blank'>
   <img src='https://github.com/jiteshsaini/files/blob/main/img/btn_youtube.png' height='40px'>
</a>
</p>
                    
<p align="center">
   <img src="https://github.com/jiteshsaini/files/blob/main/img/obj_det.gif">
</p>

## Code Files
The ML model used in this project is placed in 'all_models' directory inside parent directory.


## Overview
The code in this project is based on Google-Coral Object Detection example available at:-<br>
https://github.com/google-coral/examples-camera/tree/master/opencv

A brief description of the files used in this project is mentioned below.

1. **object_detection.py**

 The file implements basic object detection using TensorFlow Lite API. Camera operation and generation of output window with text and figure overlays is carried out using OPENCV.
 Other customisations implemented are as follows:-
 - Object Detection with colour coded bounding boxes
 - Added information bar on top of the output window to show FPS, Processing duration and an Object Counter
 - Counter gets updated upon finding 'Person' in the frame

2. **object_detection_web1.py**

 This file covers all the features mentioned above. In addition, following features have been implemented:-
 - Integrated FLASK with the object detection code to stream the output window over LAN.
 - Created a directory named 'templates' and placed a html file named 'index1.html' in it. This html file is responsible for displaying the output streamed through FLASK. It can be viewd by typing the IP address of Raspberry Pi follwed by the port as mentioned in the code.

3. **object_detection_web2.py**

This file covers all the features mentioned above. In addition, following features have been implemented:-

 - The object name to be monitored is supplied through Web GUI for updating the Object Counter during run time. 
 - The code for Web GUI is present in 'web' directory.

4. **common1.py**

This is a utility file which is imported in all the above three files. It contains functions to load a model, making interpreter, generating overlays on output window etc

