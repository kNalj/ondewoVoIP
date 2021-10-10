# ondewoVoIP
VoIP bot that plays back files based on speech input

There are many ways to make this work, i chose the one that was simplest for me and my environment. This included the following steps:

 1) Download and install [Oracle VirtualBox](https://www.virtualbox.org/)
 2) Download [Ubuntu](https://ubuntu.com/download/desktop) image (I downloaded 20.04.3 LTS version)
 3) Setup Ubuntu virtual machine using previously downloaded VirtualBox and Ubuntu image

    <details>
      <summary>Expand for details</summary>
   
    - Click on "NEW" to create a new VM

    ![01-VM](https://user-images.githubusercontent.com/13066652/136285382-db3561b6-3b5e-40e4-b276-661ad82dd48a.png)
 
    - Select desired memory size (I choose 4GB)
    - Select the "Create a virtual disk now" option
 
    ![02-virtualdisk](https://user-images.githubusercontent.com/13066652/136285663-3e6bce36-35ac-4e9b-971d-d3ada8d9c0f1.png)
 
    - Select "VDI" option
 
    ![03-VDI](https://user-images.githubusercontent.com/13066652/136285897-ae57e5ab-be79-439f-a34b-a7f362432e73.png)
 
    - Select "Fixed size" option, and choose the appropriate disk size (I went with 50GB)
 
    ![04-fixed](https://user-images.githubusercontent.com/13066652/136285994-923f7baa-92f4-4c2e-9dfc-47b26e790fa4.png)
 
    - Click on the underlined "Storage" which opens a new window
 
    ![05-storage](https://user-images.githubusercontent.com/13066652/136286115-88f634b5-be6c-4468-ae8d-847b48fa2c1d.png)
 
    - In the storage section, click the underlined "Empty", and select the Ubuntu image you downloaded earlier by clicking 
    the underlined disk and selecting "Choose a disk file" option.
 
    ![06-img](https://user-images.githubusercontent.com/13066652/136286289-d82bf448-dc62-4337-aef1-b4212ae87204.png)
 
    - In to "System" section of the menu, go to the "Processor" tab and select appropriate number of CPUs to use 
    (I went with 4)
 
    ![07-proc](https://user-images.githubusercontent.com/13066652/136286623-b5474738-63a3-4f08-945b-ba6ec6f8249a.png)
    </details>

 4) Boot the Ubuntu VM and install the operating system
     <details>
      <summary>Expand for details</summary>
     
     - Select default options for everything
     - Optionally create custom partitioning table
       - Swap memory: same as the amount of RAM
       - Mount point "/" : 20 GB
       - Mount point "/home" : Reamining disk size

     </details>
 5) Install Asterisk
    <details>
      <summary>Expand for details</summary>
  
    ## Prerequisites
 
    Before continuing with this tutorial, make sure you are logged in as a user with sudo privileges .

    Update your Ubuntu system and install the following packages which are necessary to download and build Asterisk:
 
    ```
    sudo apt update && sudo apt upgrade
    sudo apt install wget build-essential subversion
    ```
  
    ## Downloading Asterisk
 
    We are going to download Asterisk source in the /usr/src directory which is the common location to place source files, 
    change to the directory with:
 
    ```
    cd /usr/src/
    ```
  
    Download the latest version of Asterisk 18 using the following wget command :
  
    ```
    sudo wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-18-current.tar.gz
    ``` 
 
    Once the download is completed extract the tarball with:

    ```
    sudo tar zxf asterisk-18-current.tar.gz
    ``` 
 
    Before continuing with the next steps, make sure you change to the Asterisk source directory by typing:

    ```
    cd asterisk-18.*/
    ```
 
    ## Installing Asterisk Dependencies
 
    The following script will download the MP3 sources which are required to build the MP3 module and use MP3 
    files on Asterisk:

    ```
    sudo contrib/scripts/get_mp3_source.sh
    ```
 
    Use the install_prereq script to resolve all of the dependencies on your Ubuntu system:

    ```
    sudo contrib/scripts/install_prereq install
    ``` 
 
    The script will install all necessary packages and upon successful completion, it will print the following message:
 
    ```
    #############################################
    ## install completed successfully
    #############################################
     ```
 
    ## Installing Asterisk
 
    The configure script will perform a number of checks to make sure all of the dependencies on your system are present, 
    start the script by typing:
 
    ```
    sudo ./configure
    ```
 
    Upon successful completion, you will see the following output:
    ![configure-asterisk_hu0c7894854a446e25c3397f87a60e7179_74411_768x0_resize_q75_lanczos](https://user-images.githubusercontent.com/13066652/136288634-a5dd9943-aa5b-4c0b-bcfd-04ed0fc8303f.png)
 
    The next step is to select the modules you want to compile and install. Access the Menuselect system, by typing:
 
    ```
    sudo make menuselect
    ```
 
    We have already downloaded the MP3 source files and now we need to tell Asterisk to build the MP3 module by selecting 
    format_mp3:
 
    ![asterisk-mp3_hua61dbfefa68829b965e4e9d64ed48119_149382_768x0_resize_q75_lanczos](https://user-images.githubusercontent.com/13066652/136288779-610c7ed3-2d60-49e5-8e31-81cb034f6f7b.png)
    
    Once you are finished, press F12 to save and exit, or switch to the Save and Exit button and press Enter.

    Now we can start the compilation process using the make command:
 
    ```
    sudo make -j2
    ```
  
    The compilation may take some time, depending on your system. You can modify the -j flag according to the number of 
    cores in your processor.
 
    Once the build process is completed, you will be presented with the following message:
 
    ![03](https://user-images.githubusercontent.com/13066652/136288857-8ae4089a-9c0d-40b9-a3c5-0b6452703a5a.png)

    As the message above says, the next step is to install Asterisk and its modules by typing:

    ```
    sudo make install
    ```
  
    Once the installation is finished the script will display the following message:
 
    ![04](https://user-images.githubusercontent.com/13066652/136288951-c2d8e550-f76b-4a30-96f3-2694767a7691.png)
 
    Now that we have Asterisk installed we need to install the sample configuration files.
 
    Install either the generic configuration files with reference documentation by typing:

    ```
    sudo make samples
    ```
  
    Or install the basic PBX configuration files:

    ```
    sudo make basic-pbx
    ```
  
    The last step is to install the Asterisk init script by typing:

    ```
    sudo make config
    ```
  
    It is also a good idea to run ldconfig to update the shared libraries cache:
 
    ```
    sudo ldconfig
    ```
  
    ## Creating Asterisk User
 
    By default Asterisk runs as a root user. For security reasons we will create a new system user and configure 
    Asterisk to run as the newly created user.

    To create a new system user named asterisk run the following command:

    ```
    sudo adduser --system --group --home /var/lib/asterisk --no-create-home --gecos "Asterisk PBX" asterisk
    ```
  
    To configure Asterisk to run as asterisk user, open the /etc/default/asterisk file and uncomment the following 
    two lines:

    ```
    /etc/default/asterisk
    AST_USER="asterisk"
    AST_GROUP="asterisk"
    ```
  
    Add the asterisk user to the dialout and audio groups:

    ```
    sudo usermod -a -G dialout,audio asterisk
    ```
  
    We also need to change the ownership and permissions of all asterisk files and directories so the user asterisk 
    can access those files:
  
    ```
    sudo chown -R asterisk: /var/{lib,log,run,spool}/asterisk /usr/lib/asterisk /etc/asterisk
    sudo chmod -R 750 /var/{lib,log,run,spool}/asterisk /usr/lib/asterisk /etc/asterisk
    ```
  
    ## Starting Asterisk
 
    Now that we are all set up, we can start the Asterisk service with the following command:

    ```
    sudo systemctl start asterisk
    ```

    To verify that Asterisk is running, connect to the Asterisk command line interface (CLI) by typing:

    ```
    sudo asterisk -vvvr
    ```
 
    You’ll see the default Asterisk CLI prompt:
 
    ![05](https://user-images.githubusercontent.com/13066652/136289169-88daab77-48b3-464f-9219-a54e68f3afa8.png)
 
    The last step is to enable Asterisk service to start on boot with:

    ```
    sudo systemctl enable asterisk
    ```
 
    ## Configuring Firewall
 
    The firewall will secure your server against unwanted traffic.

    If you don’t have a firewall configured on your server, you can check our guide about how to setup a firewall with ufw on ubuntu

    By default, SIP uses the UDP port 5060, to open the port run:
 
    ```
    sudo ufw allow 5060/udp
    ```
 
    If you enabled the Real Time Protocol (RTP) then you also need to open the following port range:

    ```
    sudo ufw allow 10000:20000/udp
    ```
 
    Feel free to adjust the firewall according to your need.
  
    </details>
 6) Install sipsimple for python3
    <details>
      <summary>Expand for details</summary>
      
    ## SIP SIMPLE SDK installation on Ubuntu

    Home page: http://sipsimpleclient.org

    This document describes the installation procedure on Ubuntu operating
    systems from the official public repository maintained by AG Projects.

    Configure Repository

    Install the AG Projects debian software signing key: 

    ```
    wget http://download.ag-projects.com/agp-debian-gpg.key
    sudo apt-key add agp-debian-gpg.key
    ```

    Add the repository to /etc/apt/sources.list (run commands as root):
 
    ```
    echo "deb       http://ag-projects.com/ubuntu `lsb_release -c -s` main" >> /etc/apt/sources.list
    echo "deb-src   http://ag-projects.com/ubuntu `lsb_release -c -s` main" >> /etc/apt/sources.list
    ```

    Update the list of available packages:

    ```
    sudo apt-get update
    ```

    Install SIP SIMPLE client SDK:

    ```
    sudo apt-get install python3-sipsimple
    ```

    Install the Command Line Clients:

    ```
    sudo apt-get install sipclients3
    ```
    </details>
 7) Clone this repository
    
    <details>
      <summary>Expand for details</summary>
 
    - Install git if you dont have it already
 
    ```
    sudo apt update
    sudo apt install git
    git --version
    ```
    
    - Clone the repo
    ```
    git clone https://github.com/kNalj/ondewoVoIP.git
    ```
 
    </details>

 8) Enable microphone loopback
    <details>
      <summary>Expand for details</summary>
 
     - Install Audio Recorder
 
    ```
    sudo apt-add-repository ppa:audio-recorder/ppa
    sudo apt-get update
    sudo apt-get install audio-recorder
    ```
 
     - Install PulseAudio Volume Control
 
    ```
    sudo apt update
    sudo apt install pavucontrol
    ```
 
     - Clone sipsimple3 examples repo
 
    ```
    git clone https://github.com/kNalj/sipsimple3-examples.git
    ```
     - Run VoIPBot.py
 
    ```
    python3 VoIPBot.py
    ```
 
     - Run ConfigCall.py from examples repository in another terminal
 
    ```
    python3 ConfigCall.py
    ```
 
     - Open PulseAudio Volume control
 
     ```
     pavucontrol
     ```
 
     - In the PulseAudio Volume Control, go to "Recording" tab, and change the displayed dropdown to be: "Monitor of Built-In Audio Analog Stereo". If it is not showing up, change the bottom dropdown to display "All Streams"
 
     ![Loopback1](https://user-images.githubusercontent.com/13066652/136464543-a483ffab-9883-4c3f-b029-3a3fa17f198c.png)

     - Make sure that the same option is now displayed in the "Input Devices" tab
 
     ![Loopback2](https://user-images.githubusercontent.com/13066652/136464563-ee246056-19fa-4ff5-adbc-8afe163efb74.png)

 
     - Close all terminals, and the VoIPBot is ready to work.
 
    </details>

 9) Run the bot and use any SIP client to make a call to the bot.
    - Issue a command of your choice
    - Wait for bots response


## SOURCES: 
  - https://brb.nci.nih.gov/seqtools/installUbuntu.html
  - https://linuxize.com/post/how-to-install-asterisk-on-ubuntu-18-04/
  - https://github.com/AGProjects/python3-sipsimple/blob/master/docs/Install.ubuntu
  - https://itsfoss.com/record-streaming-audio/
  - https://wiki.ubuntu.com/record_system_sound
