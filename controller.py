import time
import string
import logging
from threading import Thread

import config as cfg
from camera import Camera
from rcwl_0516 import RCWL_0516
from bot import SurveillanceBot
from role import Role

class Controller():
    
    def __init__(self):
        
        #: Init bot, camera and motion detector
        self.bot = SurveillanceBot(self.pause_unpause_callback)
        self.camera =  Camera()
        self.rcwl = RCWL_0516(self.motion_state_change_callback)
        
        #: Start detecting in dedicated thread
        Thread(target = self.rcwl.detect).start()
        
        self.motion_active = False
        
        #: Logging setup
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', level=logging.DEBUG)
        
        #: Init logger
        self.logger = logging.getLogger(__name__)
        
        self.surveillance_paused = True
        self.no_detection_timeframe_start = None #TODO allow to set starttime of a no-detection timeframe
        self.no_detection_timeframe_end = None #TODO allow to set endtime of a no-detection timeframe
        
    def pause_unpause_callback(self, pause_surveillance: bool) -> bool:
        ''' Callback for telegram bot to inform about pausing and unpausing the surveillance

            #: returns whether or not the state changed
        '''
        
        #: save if the state is about to change
        did_change = pause_surveillance != self.surveillance_paused
        
        #: set anyways
        self.surveillance_paused = pause_surveillance
        
        #: return wheter the update changed the state
        return did_change
        
        
    def motion_state_change_callback(self, is_motion_start):
        '''
        '''

        #: If motion sensor registered movement ...
        if is_motion_start:
            self.motion_active = True
            
            #: ... and camera is not yet recording and survaillance is not paused - start recording
            if not self.camera.is_recording and not self.surveillance_paused:
                Thread(target = self._start_recording).start()

        else:
            self.motion_active = False
                    
    
    def _start_recording(self):
        '''
        '''
        
        self.camera.start_recording()
        self.logger.debug('Started recording')
        self.bot.alert('Motion detected, recording started!', Role.OPEN)
        self._timer()

        #self.timer_thread = Thread(target = self._timer)
        #self.timer_thread.start()
        
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
                Thread(target = self._stop_recording).start()
                return
        
        #: If the recording oulasts the max lenght, stop
        if self.camera.is_recording:
            Thread(target = self._stop_recording).start()
            
            #: Start new recording only if surveillance is not paused
            if not self.surveillance_paused:
                self._start_recording()
            
        