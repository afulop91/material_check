from guizero import App, Box, Text, PushButton, TextBox
import random
import json
import socket
import os
import time
from datetime import date, datetime
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

IRQ_PIN=27

GPIO.setmode(GPIO.BCM)
GPIO.setup(IRQ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

reader = SimpleMFRC522()

def handle_rfid():
    id = reader.read_id_no_block()
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

with open(file_path, 'r') as file:
    for line in file:
        material_list.append(line.strip())

with open(json_path) as json_file:
    users = json.load(json_file)

rFID_list = list(users.keys())

HOST = "172.168.0.10"  # The server's hostname or IP address
PORT = 22002  # The port used by the server

isOnline = 0
theSwitch = 1

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
    choice_box.border = 1 if theSwitch == 1 else 0
    verify_box.border = 1 if theSwitch == 2 else 0

def choose(id):
    global i1
    global filename
    if i1 < len(material_list) - 1:
        i1 += 1
    else:
        i1 = 0
    material_active.value = material_list[i1]
    rFID_active.value = id #random.choice(rFID_list)
    try:
        name_active.value = users[rFID_active.value]
    except Exception as err:
        print("Exception", err)
        name_active.value = "Ismeretlen"

    # Ensure the directory exists
    directory = os.path.join(log_path,str(datetime.now().year))
    os.makedirs(directory, exist_ok=True)  # exist_ok=True prevents an error if the directory already exists
    
    filename = str(date.today())+".log"
    log_final_path = os.path.join(directory, filename)
    msg = str(datetime.now())+" Anyag: "+material_active.value+ " Választó: "+rFID_active.value+" "+name_active.value+"\n"
    with open(log_final_path, 'a') as log:
        log.write(msg)
        

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(0.1)
            s.connect((HOST, PORT))
            s.send(msg.encode("windows-1250"))
            onlineOfflineText.value = "Online"
            onlineOfflineBox.bg = "green"
        except Exception as err:
            print("Exception", err)
            onlineOfflineText.value = "Offline"
            onlineOfflineBox.bg = "red"


def verify(id):
    rFID_active_verify.value = id #random.choice(rFID_list)
    try:
        name_active_verify.value = users[rFID_active_verify.value]
    except Exception as err:
        print("Exception", err)
        name_active_verify.value = "Ismeretlen"
    material_active_verify.value = material_active.value

    msgString_1 = str(datetime.now())+" Kiválasztott anyag: "+material_active.value+" Választó: "+rFID_active.value+" "+name_active.value
    msgString_2 = " Hitelesített anyag: "+material_active_verify.value+" Hitelesítő: "+rFID_active_verify.value+" "+name_active_verify.value+" ""\n"
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
            onlineOfflineText.value = "Online"
            onlineOfflineBox.bg = "green"
        except Exception as err:
            print("Exception", err)
            onlineOfflineText.value = "Offline"
            onlineOfflineBox.bg = "red"


def update():
    if rFID_active_verify.value != "" and rFID_active.value != "":
        if rFID_active_verify.value == rFID_active.value:
            tick_box_1.bg = "#FF4000"
        else:
            tick_box_1.bg = "#40ff00"
    if name_active_verify.value != "" and name_active.value != "":
        if name_active_verify.value == "Ismeretlen" or name_active.value == "Ismeretlen":
            tick_box_2.bg = "#FF4000"
        else:
            tick_box_2.bg = "#40ff00"
    if material_active_verify.value != "" and material_active.value != "":
        if material_active_verify.value == material_active.value:
            tick_box_3.bg = "#40ff00"
        else:
            tick_box_3.bg = "#FF4000"
    handle_rfid()

def goodBye():
    GPIO.cleanup()
    app.destroy()  # Stops the app loop

app = App(title="Anyag hitelesités", bg = "#333333", width=720, height=480, layout="auto")
app.tk.attributes('-fullscreen', True)

top_Box = Box(app, width=686, height=132, align="top", border=1, layout="auto")

Title = Text(top_Box, text="Anyag hitelesítés", color="#00bfff", align="left", size=24)
Title.text_bold = True

exit_Right_Box = Box(top_Box, width=48, height=100, align="right")
exit_Top_Box = Box(exit_Right_Box, width=32, height=32, align="top")
exit_Button = PushButton(exit_Top_Box, width=32, height=32, align="top", text="X", command=goodBye)
exit_Button.bg = "#00bfff"
exit_Button.text_bold = True

middle_Box = Box(app, width=686, height=230, align="top", border=0, layout="auto")

padding_box = Box(middle_Box, width=10, height=280, align="left", border=0, layout="auto")
label_box = Box(middle_Box, width=100, height=280, align="left", border=0, layout="auto")
label_box2 = Box(label_box, align="left", border=0, layout="auto")
choice_box = Box(middle_Box, width=260, height=280, align="left", border=0, layout="auto")
choice_box2 = Box(choice_box, align="left", border=0, layout="auto")
result_box = Box(middle_Box, width=50, height=280, align="left", border=0, layout="auto")
result_box2 = Box(result_box, align="left", border=0, layout="auto")
#label_box_2 = Box(middle_Box, width=55, height=280, align="left", border=0, layout="auto")
verify_box = Box(middle_Box, width=260, height=280, align="left", border=0, layout="auto")
verify_box2 = Box(verify_box, align="left", border=0, layout="auto")

rFID_label = Text(label_box2, text="RFID: ", color="#00bfff", width="fill", align="top", size=20)
name_label = Text(label_box2, "Név: ", color="#00bfff", width="fill",align="top", size=20)
material_label = Text(label_box2, "Anyag: ", color="#00bfff", width="fill",align="top", size=20)

rFID_active = Text(choice_box2, "", color="#00bfff", width="fill", size=20)
name_active = Text(choice_box2, "", color="#00bfff", width="fill", size=20)
material_active = Text(choice_box2, "", color="#00bfff",  width="fill", size=20)

#button_cycle = PushButton(choice_box, text="Cycle", command=cycle, align="left")
#button_cycle.bg = "#00bfff"
#button_cycle.text_bold = True
#cycle_RFID = TextBox(choice_box, align="left")
#cycle_RFID.text_size = 20
#cycle_RFID.text_color = "#00bfff"
#cycle_RFID.text_bold = True

tick_box_1 = Box(result_box2, width=40, height=40, border=1)
tick_box_2 = Box(result_box2, width=40, height=40, border=1)
tick_box_3 = Box(result_box2, width=40, height=40, border=1)

#rFID_label = Text(label_box_2, text="RFID: ", color="#00bfff", width="fill", bold=True)
#name_label = Text(label_box_2, "Név: ", color="#00bfff", width="fill", bold=True)
#material_label = Text(label_box_2, "Anyag: ", color="#00bfff", width="fill", bold=True)

rFID_active_verify = Text(verify_box2, "", color="#00bfff", width="fill", size=20)
name_active_verify = Text(verify_box2, "", color="#00bfff", width="fill", size=20)
material_active_verify = Text(verify_box2, "", color="#00bfff", width="fill", size=20)

#verify_RFID = TextBox(verify_box, align="left")
#verify_RFID.text_size = 20
#verify_RFID.text_color = "#00bfff"
#verify_RFID.text_bold = True

bottom_box = Box(app, width=686, height=150, align="top", border=1, layout="auto")


onlineOfflineBox = Box(bottom_box, height = 50, width="fill", align="bottom")
onlineOfflineBox2 = Box(onlineOfflineBox, height = "fill", align="top")
onlineOfflineText = Text(onlineOfflineBox2, "Offline", bg="#333333", color="#00bfff", align="left", size=22)
if isOnline:        
    onlineOfflineText.value = "Online"
    onlineOfflineBox.bg = "green"
    onlineOfflineText.bg = "#333333"
else:        
    onlineOfflineText.value = "Offline"
    onlineOfflineBox.bg = "red"
    onlineOfflineText.bg = "#333333"

copyright_Box = Box(bottom_box, width="fill", align="bottom")
copyright = Text(copyright_Box, "Syntaks©", color="#00bfff", align="right", size=12)

button_verify = PushButton(bottom_box, text="Switch", command=switch, align="bottom")
button_verify.bg = "#00bfff"
button_verify.text_bold = True

app.repeat(400, update)

app.display()
