#from time import sleep
from camera import Camera
from rcwl_0516 import RCWL_0516
from bot import SurveillanceBot
import config as cfg
import time
import string
from threading import Thread


class MotionDetectionHandler():
    
    def __init__(self):
        self.bot = SurveillanceBot()
        self.camera =  Camera()
        self.md = RCWL_0516(self.motion_state_change)
        self.detect_thread = Thread(target = self.md.detect)
        self.detect_thread.start()
        self.motion_active = False
        self.paused = False
        self.no_detection_timeframe_start = None #TODO
        self.no_detection_timeframe_end = None #TODO
        
    def motion_state_change(self, is_motion_start):
        if is_motion_start:
            self.motion_active = True
            if not self.camera.is_recording:
                self.camera.start_recording()
                self.bot.alert()
        if not is_motion_start:
            self.motion_active = False
            self.check_thread = Thread(target = self.check)
            self.check_thread.start()
        
    def check(self):
        for i in range(cfg.BUFFER_TIME_SECONDS):
            time.sleep(1)
            if self.motion_active:
                return
        if self.camera.is_recording:
            video = self.camera.stop_recording()
            self.bot.send_surveillance_video(video)