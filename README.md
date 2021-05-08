<p align="left">
Visit Website: <a href='https://helloworld.co.in/term/robotics4' target='_blank'>
   <img src='https://github.com/jiteshsaini/files/blob/main/img/logo3.gif' height='40px'>
   
</a> Youtube Channel: 
<a href='https://www.youtube.com/channel/UC_2OyRNVCWCH8ipgmAoJ1mA' target='_blank'>
   <img src='https://github.com/jiteshsaini/files/blob/main/img/btn_youtube_2.png' height='40px'>
</a>
</p>

# Robotics Level 4

This repo is an extension of previous [level](https://github.com/jiteshsaini/robotics-level-3). The code of this robot is organised in various folders inside the directory 'earthrover'. The names of these folders briefly indicate the purpose of the code inside them. This repo focusses on the advanced capabilities embedded into the robot via use of Pre-trained Machine Learning models provided by "tensorflow.org" or created via online tool of Google called Teachable Machine. The following projects in this repo demonstrate how we can integrate Tensorflow Lite and such Machine Learning Models on a Raspberry Pi computer. You can further read about them by accessing their individual README.md file.

- Gesture Controls
- Image Classification
- Object Detection
- Object Tracking
- Human Following

## Download the code and configure your Raspberry Pi

I have created a bash script that installs all the packages / libraries required to run this code on your Raspberry Pi. The script also downloads the code of this repo along with ML models on your device automatically. Follow the instructions on the link given below to configure your Raspberry Pi:-

<a href='https://helloworld.co.in/earthrover'>https://helloworld.co.in/earthrover</a>


## <a href='https://github.com/jiteshsaini/robotics-level-4/tree/main/earthrover/object_detection'>Object Detection</a>

The code for this project is placed in a directory named 'object_detection' inside the 'earthrover' directory
The ML model used in this project is placed inside 'all_models' directory. 

The robot can spy on a particular object and provide an alarm on a remote Web Control panel whenever the selected object appears in the frame.

## <a href='https://github.com/jiteshsaini/robotics-level-4/tree/main/earthrover/object_tracking'>Object Tracking</a>
The code for this project is placed in a directory named 'object_tracking' inside the 'earthrover' directory
The ML model used in this project is placed inside 'all_models' directory.  

Robot is made to track a ball and follow it. You can see the robot's camera view on a browser while it is tracking the ball.

## <a href='https://github.com/jiteshsaini/robotics-level-4/tree/main/earthrover/human_following'>Human Following</a>
The code for this project is placed in a directory named 'human_following' inside the 'earthrover' directory
The ML model used in this project is placed inside 'all_models' directory.  

Robot is made to follow a human. It is a good human follower :)

## <a href='https://github.com/jiteshsaini/robotics-level-4/tree/main/earthrover/image_classification'>Image Classification</a>

The code for this project is placed in a directory named 'image_classification' inside the 'earthrover' directory. 
The ML model used in this project is placed inside 'all_models' directory.

The robot's camera view is streamed over LAN with overlays of image classification output. Also, if an object is recognised, the robot speaks out its name.

## <a href='https://github.com/jiteshsaini/robotics-level-4/tree/main/earthrover/tm'>Gesture Control</a>

The code for this project is placed in a folder named 'tm' inside the 'earthrover' directory. 
The model used in this project is trained through Teachable Machine online tool by Google. 
The model files are present in the same directory. Presently the model is trained to recognise hand gestures. You can train your own model using Teachable Machine and replace the model files to customise the project.
