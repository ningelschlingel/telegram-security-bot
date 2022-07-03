import os
import string
import random
from subprocess import call

def randomstr(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k = length))

def delete_file(filename):
    file = get_abspath(filename)
    if os.path.isfile(file):
        os.remove(file)
        
def get_abspath(path):
    return os.path.abspath(path)

def shell_cmd(cmd):
    call(cmd, shell=True)
    
if __name__ == '__main__':
    convert = 'MP4Box -add {before} {after}'.format(before = 'O8Y0MVGS6L85WZ.h264', after = 'videos/HURENSOHN.mp4')
    delete = 'rm ' + 'asdfasdf.h264 O8Y0MVGS6L85WZ.h264'
    shell_cmd(convert + '; ' + delete)