from guizero import App, Box, Text, PushButton, TextBox
import random
import json
import socket
import os
import time
from datetime import date, datetime
import subprocess

FULLSCREEN = False
GRAY = "#333333"
BLUE = "#00bfff"

print(os.name) 
if os.name == "posix":
    from mfrc522 import SimpleMFRC522

if os.name == "posix":
    reader = SimpleMFRC522()

def handle_rfid():

    if os.name == "posix":
        id = reader.read_id_no_block()
    else:
        id = None
    if id != None:
        if theSwitch == 1:
            choose(id)
        else:
            verify(id)

script_folder = os.path.dirname(os.path.abspath(__file__))
print(script_folder)

file_path = os.path.join(script_folder,'materials.dat')
json_path = os.path.join(script_folder,'RFIDs.json')
log_path = script_folder

material_list = []

with open(file_path, 'r', encoding="utf-8") as file:
    for line in file:
        material_list.append(line.strip())

with open(json_path, encoding="utf-8") as json_file:
    users = json.load(json_file)

rFID_list = list(users.keys())

def get_wifi_ssid():
    if os.name == "nt":
        result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if "SSID" in line:
                return line.split(":")[1].strip()
        return None
    if os.name == "posix":
        try:
            ssid = subprocess.check_output(["iwgetid", "-r"]).decode().strip()
            return ssid if ssid else "Not connected"
        except subprocess.CalledProcessError:
            return "Error: Not connected or no Wi-Fi interface"

if get_wifi_ssid() == "Telekom-519850":
    HOST = "192.168.1.56"  # The server's hostname or IP address
elif get_wifi_ssid() == "Vulcan-519850":
    HOST = "172.168.0.10"  # The server's hostname or IP address
else:
    HOST = "192.168.0.1"  # The server's hostname or IP addrress

PORT = 22002  # The port used by the server
print(HOST)

def checkTheSwitch(mSwitch):
    name_label1.bg = "#333333" if mSwitch == 2 else "#00bfff"
    name_label1.text_color = "#00bfff" if mSwitch == 2 else "#333333"
    name_label2.bg = "#333333" if mSwitch == 1 else "#00bfff"
    name_label2.text_color = "#00bfff" if mSwitch == 1 else "#333333" 

isOnline = 0
rFID_chooser = ""

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.settimeout(0.1)
        s.connect((HOST, PORT))
        isOnline = 1

    except Exception as err:
        print("Exception", err)
        isOnline = 0

i1 = 0
filename = "date.log"

def switch():
    global theSwitch
    theSwitch = 2 if theSwitch == 1 else 1
    checkTheSwitch(theSwitch)

def choose(id):
    global i1
    global filename
    global rFID_chooser
    global isOnline
    global name_name2
    
    middle_Box.bg = "red"
    material_active.text_color = "#333333"
    name_name2.value = ""

    if i1 < len(material_list) - 1:
        i1 += 1
    else:
        i1 = 0
    material_active.value = material_list[i1]
    rFID_chooser = str(id) #random.choice(rFID_list)
    try:
        name_name1.value = users[rFID_chooser]
        name_name1.text_color = BLUE
        name_name1.bg = GRAY    
    except Exception as err:
        print("Exception", err)
        name_name1.value = "Ismeretlen"
        name_name1.text_color = GRAY
        name_name1.bg = "red"

    # Ensure the directory exists
    directory = os.path.join(log_path,str(datetime.now().year))
    os.makedirs(directory, exist_ok=True)  # exist_ok=True prevents an error if the directory already exists
    
    filename = str(date.today())+".log"
    log_final_path = os.path.join(directory, filename)
    msg = str(datetime.now())+" Anyag: "+material_active.value+ " Választó: "+rFID_chooser+" "+name_name1.value+"\n"
    with open(log_final_path, 'a') as log:
        log.write(msg)
        

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(0.1)
            s.connect((HOST, PORT))
            s.send(msg.encode("windows-1250"))
            isOnline = 1
        except Exception as err:
            print("Exception", err)
            isOnline = 0

def verify(id):
    global isOnline

    rFID_verifyer = str(id) #random.choice(rFID_list)
    if rFID_chooser != rFID_verifyer:
        middle_Box.bg = "green"
        material_active.text_color = BLUE
    else:
        middle_Box.bg = "yellow"
        material_active.text_color = GRAY
    

    try:
        name_name2.value = users[rFID_verifyer]
        name_name2.text_color = BLUE
        name_name2.bg = GRAY  
    except Exception as err:
        print("Exception", err)
        name_name2.value = "Ismeretlen"
        name_name2.text_color = GRAY
        name_name2.bg = "red"

    msgString_1 = str(datetime.now())+" Kiválasztott anyag: "+material_active.value+" Választó: "+rFID_chooser+" "+name_name1.value
    msgString_2 = " Hitelesítő: "+rFID_verifyer+" "+name_name2.value+"\n"
    msg = msgString_1 + msgString_2

    # Ensure the directory exists
    directory = os.path.join(log_path,str(datetime.now().year))
    os.makedirs(directory, exist_ok=True)  # exist_ok=True prevents an error if the directory already exists
    
    filename = str(date.today())+".log"
    log_final_path = os.path.join(directory, filename)
    with open(log_final_path, 'a') as log:
        log.write(msg)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(0.1)
            s.connect((HOST, PORT))
            s.send(msg.encode("windows-1250"))
            isOnline = 1
        except Exception as err:
            print("Exception", err)
            isOnline = 0

def handle_network():
    if isOnline == 1:
        onlineOfflineText.value = "Online"
        onlineOfflineBox.bg = "green"
    else:
        onlineOfflineText.value = "Offline"
        onlineOfflineBox.bg = "red"
    onlineOfflineText.bg = "#333333"

def update():
    handle_network()
    handle_rfid()

def goodBye():
    app.destroy()  # Stops the app loop

app = App(title="Anyag hitelesités", bg = "#333333", width=720, height=480, layout="auto")
app.tk.attributes('-fullscreen', FULLSCREEN)

top_Box = Box(app, width=800, height=70, border=0, layout="auto")

#copyright_Box = Box(top_Box, width="fill", align="bottom")
copyright = Text(top_Box, "Syntaks©", color="#00bfff", size=8, align="left")

Title = Text(top_Box, text="Anyag hitelesítés", color="#00bfff", align="left", size=20)
Title.text_bold = True

exit_Right_Box = Box(top_Box, height="fill", align="right")
exit_Top_Box = Box(exit_Right_Box, width=32, height=32, align="top", border=0)
exit_Button = PushButton(exit_Top_Box, width=32, height=32, align="right", text="X", command=goodBye)
exit_Button.bg = "#00bfff"
exit_Button.text_bold = True

middle_Box = Box(app, width=800, height=340, align="top", border=0, layout="auto")
material_Box = Box(middle_Box, height="fill", align="top", border=0, layout="auto")
material_active = Text(material_Box, "", color="#00bfff", width="fill", align="left", size=120)

bottom_box = Box(app, width=800, height=70, align="top", border=0, layout="auto")


onlineOfflineBox = Box(bottom_box, height = 32, width="fill", align="bottom")
onlineOfflineBox2 = Box(onlineOfflineBox, height = "fill", align="top")
onlineOfflineText = Text(onlineOfflineBox2, "Offline", bg="#333333", color="#00bfff", align="left", size=16)
if isOnline:        
    onlineOfflineText.value = "Online"
    onlineOfflineBox.bg = "green"
    onlineOfflineText.bg = "#333333"
else:        
    onlineOfflineText.value = "Offline"
    onlineOfflineBox.bg = "red"
    onlineOfflineText.bg = "#333333"

names_box = Box(bottom_box, width="fill", align="bottom", border=0)
name_label1 = Text(names_box, "Választó: ", color="#00bfff", align="left", size=16)
name_name1 = Text(names_box, "", color="#00bfff", align="left", size=16)
name_name2 = Text(names_box, "", color="#00bfff", align="right", size=16)
name_label2 = Text(names_box, "Hitelesítő: ", color="#00bfff", align="right", size=16)

if os.name == "nt":
    button_choose = PushButton(names_box, text="Choose", command=choose, args=["1234567"], align="left")
    button_choose.text_color = "#00bfff"
    button_verify = PushButton(names_box, text="Verify", command=verify, args=["3456789"], align="right")
    button_verify.text_color = "#00bfff"
if os.name == "posix":
    button_switch = PushButton(names_box, text="Switch", command=switch, align="bottom")
    button_switch.bg = "#00bfff"
    button_switch.text_bold = True

theSwitch = 1
checkTheSwitch(theSwitch)

app.repeat(400, update)

app.display()
