#!/bin/bash

echo "*********Checking Raspberry Pi OS*****************************"

RASPBIAN=$(grep VERSION_ID /etc/os-release | sed 's/VERSION_ID="\([0-9]\+\)"/\1/')
echo "Raspbian Version: $RASPBIAN"
if [ "$RASPBIAN" -gt "10" ]; then
    echo "This OS not supported."
    echo "Earthrover's software works with Raspberry Pi OS(Legacy), also known as 'Buster' and earlier versions."
    echo "Prepare a micro sd card with 'Buster' and try again."
    exit 1
fi

echo "***************************************************************"
echo "**********Updating and Upgrading the Raspberry Pi OS***********"
echo "***************************************************************"

sudo apt-get update -y
sudo apt-get upgrade -y


echo "***************************************************************"
echo "*******Installing Apache Webserver and PHP*********************"
echo "***************************************************************"

sudo apt-get install apache2 -y
sudo apt-get install php libapache2-mod-php -y

echo "***************************************************************"
echo "*****Allowing execution of system commands from PHP************"
echo "***************************************************************"

echo "pi ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
echo "www-data ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

echo "***************************************************************"
echo "*******Installing SSL Certificates*****************************"
echo "***************************************************************"

TEMP_DIR="/home/pi/Documents/temp"
FILE_NAME="helloworld_ssl_rpi"

SSL_DIR="/etc/ssl/$FILE_NAME"

if [ -e "$SSL_DIR" ]; then
    timestamp=$(date "+%Y-%m-%d_%H-%M-%S")
    mv $SSL_DIR $SSL_DIR.$timestamp
fi

sudo cp /etc/apache2/sites-available/default-ssl.conf /etc/apache2/sites-available/default-ssl.conf.bak1

mkdir -p ${TEMP_DIR}

curl -O https://helloworld.co.in/deploy/${FILE_NAME}.zip

unzip ${FILE_NAME}.zip -d ${TEMP_DIR}

rm ${FILE_NAME}.zip

mv ${TEMP_DIR}/${FILE_NAME} /etc/ssl/


sudo mv /etc/ssl/${FILE_NAME}/default-ssl.conf /etc/apache2/sites-available/

sudo chmod 600 /etc/ssl/${FILE_NAME}/apache*

rm -R ${TEMP_DIR}


#Enable Apache SSL module
sudo a2ensite default-ssl.conf
sudo a2enmod ssl
sudo a2enmod headers

#restart Apache
sudo systemctl restart apache2

echo "***************************************************************"
echo "******Installing espeak (Text to Speech engine)****************"
echo "***************************************************************"

sudo apt-get install espeak -y

echo "***************************************************************"
echo "******Installing Tensorflow Lite and USB Coral ML accelerator Libraries
echo "***************************************************************"

echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install python3-tflite-runtime -y
sudo apt-get install libedgetpu1-std -y
sudo python3 -m pip install numpy
sudo python3 -m pip install Pillow
sudo python -m pip install urllib3

echo "***************************************************************"
echo "********Installing OpenCV**************************************"
echo "***************************************************************"

sudo apt install python3-opencv -y

echo "***************************************************************"
echo "****** Downloading Robot's Software  **************************"
echo "***************************************************************"

CODE_DIR="/var/www/html/earthrover"
MODEL_DIR="/var/www/html/all_models"

if [ -e "$CODE_DIR" ]; then
    timestamp=$(date "+%Y-%m-%d_%H-%M-%S")
    mv $CODE_DIR $CODE_DIR.$timestamp
    echo "Current time: $timestamp"
fi


if [ -e "$MODEL_DIR" ]; then
    timestamp=$(date "+%Y-%m-%d_%H-%M-%S")
    mv $MODEL_DIR $MODEL_DIR.$timestamp
    echo "Current time: $timestamp"
fi

git clone https://github.com/jiteshsaini/robotics-level-4 /home/pi/Downloads/tmp
sudo mv /home/pi/Downloads/tmp/earthrover/embgpio /var/www/html/
sudo rm -R /home/pi/Downloads/tmp
sudo chmod 777 -R /var/www/html

echo "**************************************************************************************"
echo "***Your Raspberry Pi has been configured to run the software of Embedded Rpi Gpio*****"
echo "**************************************************************************************"

echo "your IP address is: " $(hostname -I)
echo "Now using a browser of Rpi embedded VNC Viewer or Laptop/PC on the same network, type following in your browser:-"
echo $(hostname -I)"/embgpio"
