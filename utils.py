import os
import time
import string
import random
import logging
import subprocess

def randomstr(length=8) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k = length))

def shell_cmd(cmd) -> None:
    subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL)
    
def timestring() -> str:
    return time.strftime('%Y-%m-%d-%Z-%H-%M-%S')

def basename(path) -> str:
    return os.path.basename(os.path.normpath(path))
    
if __name__ == '__main__':
    #convert = 'MP4Box -add {before} {after}'.format(before = 'video.h264', after = 'videos/video.mp4')
    #delete = 'rm ' + 'video.h264'
    #shell_cmd(convert + '; ' + delete)
    #print(timestring())
    print(basename('/ajksdf/aksjfdh/jkasdfhiuva///askjdfh/82343789345u&%%/(5/file.txt/'))