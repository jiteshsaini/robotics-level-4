# Human Following AI-Robot

<p align="left">
Read the article: <a href='https://helloworld.co.in/article/ai-robot-human-following-robot-using-tensorflow-lite-raspberry-pi' target='_blank'>
   <img src='https://github.com/jiteshsaini/files/blob/main/img/logo3.gif' height='40px'>
</a> Watch the video on Yotube: 
<a href='https://youtu.be/GSYtn8BlGBI' target='_blank'>
   <img src='https://github.com/jiteshsaini/files/blob/main/img/btn_youtube.png' height='40px'>
</a>
</p>


<p align="center">
   <img src="https://github.com/jiteshsaini/files/blob/main/img/human_following.gif">
   
</p>

## Model files
The ML model used in this project is placed in 'all_models' directory inside parent directory.

## Overview of the Project
Robot detects presence of a person in camera frame using a Machine Learning model 'MobileNet SSD v1 (COCO)' and TensorFlow Lite interpreter. 
The code of Human following robot is partially derived from the <a href='https://github.com/jiteshsaini/robotics-level-4/tree/main/earthrover/object_tracking'>Object Tracking code</a>. However, there is a difference in the method which calculates distance from the object to generate forward motion command.

Both the files 'human_follower.py' and 'human_follower2.py' files are identical in logic. One implements FLASK and the other doesn't, as mentioned below.

### 'human_follower.py'
This file performs human following and streams the robot view over LAN using FLASK (Python's micro Web Framework). 

### 'human_follower2.py'
Pure human following logic. The code pertaing to FLASK is removed.

### 'common.py'
This file contains the utility functions which are required for setting up of Tensorflow Lite interpreter.

 
