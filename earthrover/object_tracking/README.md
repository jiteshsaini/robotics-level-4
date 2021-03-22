# Object Tracking AI-Robot

<p align="left">
Read the article: <a href='https://helloworld.co.in/article/ai-robot-object-tracking-object-following-robot-using-tensorflow-lite' target='_blank'>
   <img src='https://github.com/jiteshsaini/files/blob/main/img/logo3.gif' height='40px'>
</a> Watch the video on Yotube: 
<a href='https://youtu.be/gqirgvxcXVQ' target='_blank'>
   <img src='https://github.com/jiteshsaini/files/blob/main/img/btn_youtube.png' height='40px'>
</a>
</p>

<p align="center">
   <img src="https://github.com/jiteshsaini/files/blob/main/img/track3.gif">
</p>

## Model files
The ML model used in this project is placed in 'all_models' directory inside parent directory.

## Overview of the Project
Robot detects an object using a Machine Learning model 'MobileNet SSD v1 (COCO)' and TensorFlow Lite interpreter. The Robot follows the object and manoeuvres itself to get the object in the center of frame. While the robot is tracking / following the object, working of tracking algorithm and Robot's view can be accessed on a browser. Robot's view with information overlay is generated using OpenCV. The various overlays on a frame are shown in the picture below

<p align="center">
   <img src="https://github.com/jiteshsaini/files/blob/main/img/frame.jpeg" >
</p>


When the object is present in the frame, information such as bounding boxes, center of the object, deviation of the object from center of the frame, robot direction and speed are updated as shown in picture below. In the below example, X and Y values denote the deviation of center of the object (the red dot) from center of the frame. Since the horizontal deviation i.e. value of 'X' is above the tolerance value, the code generated 'Move Left' command.  

<p align="center">
   <img src="https://github.com/jiteshsaini/files/blob/main/img/robo_view.gif">
</p>


Python's micro Web Framework called "FLASK" is used for streaming the camera frame (or Robot's view) over LAN. 
