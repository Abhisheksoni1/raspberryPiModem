import pyaudio, sys, socket
import threading

chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 15000
timer = 0
ip = '35.164.177.89'
p = pyaudio.PyAudio()
call_connected = False
port = 4653


def send_audio():
    while call_connected:
        client_socket.send(stream.read(chunk))


stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                output=True, frames_per_buffer=chunk)
# Create a socket connection for connecting to the server:
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((str(ip), port))
client_socket.send("MODEMSTATE")
while call_connected:
    d = client_socket.recv(4)
    if "OK" in d:
        call_connected = True
        threading.Thread(target=send_audio)
        while call_connected:
            data = client_socket.recv(1024)
            stream.write(data)
    elif "BUSY" in d:
        client_socket.send("MODEMSTATE")
    elif "exit" in d:
        call_connected = False
        client_socket.close()
