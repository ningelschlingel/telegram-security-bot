import time
import string
import logging
from threading import Thread
from camera import Camera

import config as cfg
from rcwl_0516 import RCWL_0516
from bot import SurveillanceBot

class Controller():
    
    def __init__(self):
        
        #: Init bot, camera and motion detector
        self.bot = SurveillanceBot()
        self.camera =  Camera()
        self.rcwl = RCWL_0516(self.motion_state_change)
        
        #: Start detecting in dedicated thread
        self.detect_thread = Thread(target = self.rcwl.detect)
        self.detect_thread.start()
        
        self.motion_active = False
        
        #: Init logger
        self.logger = logging.getLogger(__name__)
        
        self.paused = False #TODO allow pausing the surveillance
        self.no_detection_timeframe_start = None #TODO allow to set starttime of a no-detection timeframe
        self.no_detection_timeframe_end = None #TODO allow to set endtime of a no-detection timeframe
        
    def motion_state_change(self, is_motion_start):
        '''
        '''
        
        #:
        if is_motion_start:
            self.motion_active = True
            if not self.camera.is_recording:
                self._start_recording()
        else:
            self.motion_active = False

        self.logger.debug('Motion {} [transmitted value: {}]'.format('started' if is_motion_start else 'ended  ', is_motion_start))
                    
    
    def _start_recording(self):
        '''
        '''
        
        self.camera.start_recording()
        self.logger.debug('Started recording')
        self.bot.alert()
        self.logger.debug('Started recording')
        self.timer_thread = Thread(target = self._timer)
        self.timer_thread.start()
        
    def _stop_recording(self):
        '''
        '''
        
        video = self.camera.stop_recording()
        self.logger.debug('Stopped recording')
        self.bot.send_surveillance_video(video)
    
    def _timer(self):
        '''
        '''
        
        inactive = 0
        
        #: Check every second until max video length
        for i in range(cfg.MAX_VIDEO_LENGTH):
            time.sleep(1)
            
            #: If motion stopped, increment counter
            if not self.motion_active:
                inactive += 1
                self.logger.debug('recording [{}/{} s] - motion inactive [{}/{}]'.format(i, cfg.MAX_VIDEO_LENGTH, inactive, cfg.BUFFER_TIME_STEPS))
            #: else reset counter
            else:
                self.logger.debug('recording [{}/{} s] - motion active'.format(i, cfg.MAX_VIDEO_LENGTH))
                inactive = 0
            
            #: If motion is inactive for too long, stop video
            if inactive >= cfg.BUFFER_TIME_STEPS:
                self._stop_recording()
                return
        
        #: If the recording oulasts the max lenght, stop and start new recording
        if self.camera.is_recording:
            video = self.camera.stop_recording()
            self.bot.send_surveillance_video(video)
            self._start_recording()
            
        