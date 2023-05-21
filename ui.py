import cv2
import RPi.GPIO as GPIO
import threading as thread
from tkinter import Tk, Button, Label
from ocr import LicensePlateDetector
from networking import Network
from streaming import VideoClient

class UserInterface:
    def __init__(self) -> None:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Up button
        GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Down button
        GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Enter button

        GPIO.add_event_detect(11, GPIO.FALLING, callback=self.on_up, bouncetime=200)
        GPIO.add_event_detect(13, GPIO.FALLING, callback=self.on_down, bouncetime=200)
        GPIO.add_event_detect(15, GPIO.FALLING, callback=self.on_select, bouncetime=200)

        self.should_ocr_run = True
        self.detector = LicensePlateDetector()
        self.network = Network()
        self.client = VideoClient()
    
    def generate_layout(self) -> None:
        self.root = Tk()
        self.root.geometry("640x480")
        self.buttons = {}
        self.root.bind('<Up>', lambda event: self.set_focus(event))
        self.root.bind('<Down>', lambda event: self.set_focus(event))
        self.root.bind('<Return>', self.on_button_pressed)
        Label(self.root, text='current network is : ' + self.network.current_wifi).pack()
        for ssid in self.network.available_networks:
            button = Button(self.root, text = ssid, command = self.connect(ssid), width=50, height=2)
            button.pack(pady= 3)
            self.buttons[ssid] = button
        for i,button in enumerate(self.buttons.values()):
            self.root.bind(str(i+1),lambda event,button=button:self.set_focus(button))

    def set_focus(self,event) -> None:
        self.should_ocr_run = False
        current_focus = self.root.focus_get()
        buttons = list(self.buttons.values())
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
    
    def highlight(self, number) -> None:
        if number in self.buttons: self.buttons[number].focus()
        else: print('no network found', number)
    
    # On key-press actions
    def on_up(self, _) -> None:
        self.root.event_generate('<Up>', when='tail')
        print('up')
    
    def on_down(self, _) -> None:
        self.root.event_generate('<Down>', when='tail')
        print('down')
    
    def on_select(self, _) -> None:
        self.root.event_generate('<Return>', when='tail')
        print('enter')

    def on_button_pressed(self, _) -> None:
        current_focus = self.root.focus_get()
        current_focus.invoke()

    def license_plate_process(self) -> None:
        while self.should_ocr_run:
            img = self.client.getFrame()
            number = self.detector.getNumber(img)
            print("new frames, detected: ", number)
            self.highlight(number)
    
    def connect(self, ssid):
        def showDialogue():
            self.network.connect_wifi(ssid,ssid)
            self.client.start_stream()
        return showDialogue 

    def start(self) -> None:
        self.generate_layout()
        image_process = thread.Thread(target=self.license_plate_process)
        image_process.start()
        self.root.mainloop()

UserInterface().start()
