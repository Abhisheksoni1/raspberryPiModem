import serial
import pyaudio
from serial.serialutil import SerialException
import socket
import time
import threading


class RaspberryPi:
    def __init__(self):
        self.Modem = serial.Serial('COM3', 115200, timeout=5)
        self.port = 4653
        self.call_connected = False
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.CHUNK = 1024
        self.RATE = 44100
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  output=True,
                                  frames_per_buffer=self.CHUNK)

    def connect_to_modem(self):
        """try to open port"""
        try:
            self.Modem.open()
            return True
        except SerialException:
            return False

    def check_modem_status(self):
        """check if line is busy or not i.e. if ringing then its not busy 1 = ringing"""
        try:
            self.Modem.write("AT+CRC=?\n")
            if self.Modem.read(1).decode('utf-8') == 1:
                return True
            else:
                return False
        except SerialException:
            return False

    def start_call(self, number):
        try:
            # enable hang-up voice call with ATH commnad using AT+CVHU=0
            self.Modem.write("AT+CVHU=0\n")
            time.sleep(.5)
            self.Modem.write("ATDT{}\n".format(number))
            time.sleep(1)
            # ORIGIN:1,0 this means : CALL ID = 1; CALL TYPE = 0 (voice)
            self.Modem.read(10).decode('utf-8')
            if "CONF:1" in self.Modem.read(6).decode('utf-8'):
                # CONF:1 this means tha CALL with ID=1 is started
                raspberry_pi.call_connected = True
                return True
            else:
                return False
        except SerialException:
            return False


def receive_audio():
    while raspberry_pi.call_connected:
        data = raspberry_pi.server_socket.recv(raspberry_pi.CHUNK)
        raspberry_pi.Modem.write(data)
        if "ATH" in data:
            raspberry_pi.Modem.write("ATH\n")
            raspberry_pi.call_connected = False

if __name__ == "__main__":
    raspberry_pi = RaspberryPi()
    if raspberry_pi.connect_to_modem():
        raspberry_pi.server_socket.bind('', raspberry_pi.port)
        raspberry_pi.server_socket.listen(5)
        client_socket, address = raspberry_pi.server_socket.accept()
        while raspberry_pi.call_connected:
            data = raspberry_pi.server_socket.recv(10).decode('utf-8')
            if data == "MODEMSTATE":
                if raspberry_pi.check_modem_status():
                    raspberry_pi.server_socket.send("OK")
                    if raspberry_pi.start_call(raspberry_pi.server_socket.recv(12)):
                        threading.Thread(target=receive_audio)
                        while raspberry_pi.call_connected:
                            raspberry_pi.server_socket.sendall(raspberry_pi.stream.read(raspberry_pi.CHUNK))
                else:
                    raspberry_pi.server_socket.send("Busy")
        else:
            raspberry_pi.server_socket.send("exit")
            raspberry_pi.server_socket.close()
    else:
        print("Unable to connect to modem")