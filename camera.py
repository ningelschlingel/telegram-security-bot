from picamera import PiCamera
import config as cfg
from utils import randomstr, get_abspath, delete_file, shell_cmd
import string


class Camera():
    
    def __init__(self):
        self.cam = PiCamera()
        self.cam.resolution = (1280, 720)
        self.is_recording = False
        self.video_folder = cfg.VIDEO_FOLDER
        self.recording_format = cfg.CAMERA_RECORDING_FORMAT
        self.converting_format = cfg.CAMERA_CONVERTING_FORMAT
        self.video_name = 'video'

    def start_recording(self) -> None:
        #self.cam.start_recording('Videos/test.h264')
        if not self.is_recording:
            print('Started recording')
            self._set_video_name()
            self.cam.start_recording(self.video_name + self.recording_format)
            self.is_recording = True
        
    def stop_recording(self) -> str:
        if self.is_recording:
            print('Stopped recording')
            self.cam.stop_recording()
            self._convert()
            self.is_recording = False
            return self.video_folder + self.video_name + self.converting_format
        return None
    
    def _set_video_name(self):
        if not cfg.OVERRIDE_VIDEO:
            self.video_name = randomstr(14)
        
    def _convert(self):
        convert = 'MP4Box -add {before} {after};'.format(before = self.video_name + self.recording_format, after = self.video_folder + self.video_name + self.converting_format)
        delete = ' rm ' + self.video_name + self.recording_format
        shell_cmd(convert + delete)
        
        