import sys
import os

import django
import signal

import collections
import time
import datetime
import requests
import base64

import webrtcvad
import pyaudio
import sounddevice

from django.utils import timezone
from Crypto.Cipher import AES
from threading import Timer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ACI.settings")
django.setup()

#jackd -d dummy

url = 'http://0.0.0.0:8080/detection/update'
#headers = {'User-Agent': 'Mozilla/5.0'}
client = requests.session()
client.get(url)
csrftoken = client.cookies['csrftoken']
cookies = {'csrftoken': csrftoken}
username = 'update'.rjust(16)
password = 'updatepassword'.rjust(16)
room_name = '101'
cryptkey = csrftoken[:32]
cipher = AES.new(cryptkey,AES.MODE_ECB)
username_crypt = base64.b64encode(cipher.encrypt(username))
password_crypt = base64.b64encode(cipher.encrypt(password))
occupied_data = dict(username=username_crypt, password=password_crypt, csrfmiddlewaretoken=csrftoken, next='/', room_name=room_name, room_status="True")
avaliable_data = dict(username=username_crypt, password=password_crypt, csrfmiddlewaretoken=csrftoken, next='/', room_name=room_name, room_status="False")

def signal_handler(signal, frame):
    global stop
    stop = True

def activate_phase_two():
    global phase_two_timer, phase_one, phase_two, num_voiced, ring_buffer, date_occupied
    if num_voiced > 0.5 * ring_buffer.maxlen:
        print("\n >50% speech - activating phase two\n ")
        date_occupied = timezone.now()
        r = requests.post(url, occupied_data, headers=dict(Referer=url), cookies=cookies)
        phase_two = True
        phase_two_timer = Timer(10.0, check_phase_two)
        phase_two_timer.start()
        
    else:
        print("\n no consistent speech detected - deactivating phase one\n ")
        phase_one = False
        if phase_two:
            print("\n THIS STATE SHOULD NEVER HAPPEN \n ")
    ring_buffer.clear()
    num_voiced = 0

def check_phase_two():
    global phase_two_timer, phase_one, phase_two, num_voiced, ring_buffer
    if num_voiced > 0.5 * ring_buffer.maxlen:
        print("\n phase 2 still active\n ")
        phase_two_timer = Timer(10.0, check_phase_two)
        phase_two_timer.start()
    else:
        print("\n speech no longer detected - resetting\n ")
        date_freed = timezone.now()
        avaliable_data['date_occupied'] = date_occupied
        avaliable_data['date_freed'] = date_freed
        r = requests.post(url, avaliable_data, headers=dict(Referer=url), cookies=cookies)
        phase_one = False
        phase_two = False
        
    ring_buffer.clear()
    num_voiced = 0

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK_DURATION_MS = 30
PADDING_DURATION_MS = 1500
CHUNK_SIZE = int(RATE * CHUNK_DURATION_MS / 1000)
CHUNK_BYTES = CHUNK_SIZE * 2
NUM_PADDING_CHUNKS = int(PADDING_DURATION_MS / CHUNK_DURATION_MS)

vad = webrtcvad.Vad(1)
vad.set_mode(2) # sensitivity threshold
pa = pyaudio.PyAudio()

stop = False
active = False
phase_one = False
phase_two = False

phase_one_timer = Timer(10.0, activate_phase_two)
phase_two_timer = Timer(10.0, check_phase_two)

ring_buffer = collections.deque(maxlen = NUM_PADDING_CHUNKS)
voiced_chunks = []
num_voiced = 0

stream = pa.open(format = FORMAT,
                 channels = CHANNELS,
                 rate = 16000,
                 input = True,
                 start = False,
                 frames_per_buffer = CHUNK_SIZE)

StartTime = time.time()

print(" Listening: ")
stream.start_stream()

try:
    while not stop:      
        chunk = stream.read(CHUNK_SIZE)
        active = vad.is_speech(chunk, RATE)
                        
        if active:
            sys.stdout.write('|')
            if not phase_one:
                print("\n voice detected - activating phase one\n ")
                phase_one_timer = Timer(10.0, activate_phase_two)
                phase_one_timer.start()
                phase_one = True
            else:
                ring_buffer.append(("check", active))
                num_voiced += 1
        else:
            sys.stdout.write('_')
            if phase_one:
                ring_buffer.append(("check", active))

        sys.stdout.flush()
except KeyboardInterrupt:
    stop = True


print('\n exiting \n')
phase_two_timer.cancel()
phase_one_timer.cancel()
stream.stop_stream()
stream.close()
print(" done ")
quit()
