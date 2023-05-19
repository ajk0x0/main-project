import subprocess
import shlex, os
from tkinter import Tk, messagebox, Button, Label
import socket,cv2, pickle,struct
import RPi.GPIO as GPIO
import threading as thread

from streaming import *
from ocr import getNumber

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Up button
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Down button
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Enter button


def handle_key(event):
	print('key pressed',event.char)
def set_focus(event, buttons):
    global flag
    flag = False
    current_focus = top.focus_get()
    try:
        index = buttons.index(current_focus)
    except ValueError:
        index = -1
 
    if event.keysym == "Up":
        index -= 1
    elif event.keysym == "Down":
        index += 1
 
    if index >= len(buttons):
        index = 0
    elif index < 0:
        index = len(buttons) - 1
 
    buttons[index].focus()
 
def button_pressed(event):
    current_focus = top.focus_get()
    current_focus.invoke()
def highlight(number):
    global ssid_button
    if number in ssid_button: ssid_button[number].focus()
    else: print('no network found', number)
def license_plate_process():
    global flag
    while flag:
        img = cv2.imread('/home/pi/Desktop/ocr/testimg/bus/image.webp')
        highlight(getNumber(img))
cv2.imshow("Webcam", getFrame())
top = Tk()
top.geometry("640x480")
#style = Style(top)
#style.theme_use('clam')

x = 300
y = 240
Label(top, text='current network is : ' + current_wifi).pack()


def helloCallBack(ssid):
   def showDialogue():
    connect_wifi(ssid,pass_lookup[ssid])
    start_stream(host_ip, port)
    # os.system(f"nc {host_ip} {port} | mplayer -benchmark -")

   return showDialogue 
buttons=[]
ssid_button = {}
flag = True
for ssid in networks:
    B = Button(top, text = ssid, command = helloCallBack(ssid), width=50, height=2)
    B.pack(pady= 3)
    buttons.append(B)
    ssid_button[ssid] = B
for i,button in enumerate(buttons):
	top.bind(str(i+1),lambda event,button=button:set_focus(button))
print('hello')
top.bind('<Up>', lambda event: set_focus(event, buttons))
top.bind('<Down>', lambda event: set_focus(event, buttons))
 
# Bind Enter key to select the focused button
top.bind('<Return>', button_pressed)
top.bind('<Key>',handle_key)
# highlight(getNumber(), ssid_button)
# Set up callbacks for GPIO buttons
def up_pressed(channel):
    channel.widget.config(bg="light blue")
    top.event_generate('<Up>', when='tail')
    print('up')
def down_pressed(channel):
    channel.widget.config(bg="light blue")
    top.event_generate('<Down>', when='tail')
    print('down')
def enter_pressed(channel):
    top.event_generate('<Return>', when='tail')
    print('enter')
GPIO.add_event_detect(11, GPIO.FALLING, callback=up_pressed, bouncetime=200)
GPIO.add_event_detect(13, GPIO.FALLING, callback=down_pressed, bouncetime=200)
GPIO.add_event_detect(15, GPIO.FALLING, callback=enter_pressed, bouncetime=200)
image_process = thread.Thread(target=license_plate_process)
image_process.start()
top.mainloop()
flag = False
