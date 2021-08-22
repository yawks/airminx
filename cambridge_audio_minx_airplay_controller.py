#!/usr/bin/python
import sys
import socket
import base64
import urllib
import binascii

IPADDR = '192.168.1.103'
PORTNUM = 43000


class RadioRemote:
    def __init__(self):
        self.COMMANDS = {
            "helo": [0x00, 0x01, 0x02],
            "preset_thumb": [0x00, 0x02, 0x0c],
            "preset_name": [0x00, 0x02, 0x0a],
            "play_preset": [0x00, 0x02, 0x0f],
            "pause": [0x00, 0x02, 0x19, 0x00],
            "currently_playing": [0x00, 0x01, 0x14],
            "set_volume": [0x00, 0x02, 0x03],
            "get_volume": [0x00, 0x01, 0x02],  # same command as "helo"
            
			"set_stream_name": [0x00, 0x16, 0x15],
            "set_stream_url": [0x00, 0x28, 0x13],
			"play_last_stream_set": [0x00, 0x02, 0x1c, 0x50],


            "unknown1": [0x00, 0x02, 0x03, 0x0a],
            "unknown2": [0x00, 0x02, 0x03, 0x09],
            "unknown3": [0x00, 0x01, 0x06],
            "unknown4": [0x00, 0x01, 0x02],
            "unknown5": [0x00, 0x01, 0x20],
            "unknown6": [0x00, 0x01, 0x10],
            "unknown7": [0x00, 0x01, 0x1b],
            "unknown8": [0x00, 0x02, 0x07, 0x03],
            "unknown9": [0x00, 0x02, 0x03, 0x09]
        }

        # when the device acknowledge the command, the answer must end with this
        self.ack = [0xff, 0x01]

    def connect(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((IPADDR, PORTNUM))
            self.s.send(bytearray(self.COMMANDS["helo"]))
            self.s.recv(4096)  # pass
        except:
            print(str(sys.exc_info()[0]))

    def close(self):
        self.s.close()

    def _sendCommand(self, cmd):
        if not type(cmd) is bytearray:
            cmd = bytearray(cmd)
        self.s.send(cmd)
        output = self.s.recv(4096)
        if output[2:4] != bytearray(self.ack):
            print("device did no acknowledge correctly the command")
        return output[4:]

    def getPresetName(self, nb):
        name = self._sendCommand(self.COMMANDS["preset_name"] + [nb])
        if name is None or len(str(name.encode('ascii')).strip()) == 0:
            name = "-"

        # print "name:"+str(name.encode('ascii')).strip()+"#"
        return str(name.encode('ascii').strip()).replace('\x00', '')

    def getPresetThumb(self, nb):
        return self._sendCommand(self.COMMANDS["preset_thumb"] + [nb])

    def getCurrentlyPlaying(self):
        return self._sendCommand(self.COMMANDS["currently_playing"])

    def playPreset(self, nb):
        self._sendCommand(self.COMMANDS["play_preset"] + [nb])

    def pause(self):
        self._sendCommand(self.COMMANDS["pause"])

    def getVolume(self):
        return int(binascii.hexlify(b'%s' % self._sendCommand(self.COMMANDS["get_volume"])), 16)

    def volumeUp(self):
        self._sendCommand(self.COMMANDS["set_volume"] + [self.getVolume() + 1])

    def volumeDown(self):
        cur_vol = self._sendCommand(self.COMMANDS["get_volume"])
        self._sendCommand(self.COMMANDS["set_volume"] + [self.getVolume() - 1])

    def setStream(self, name, url):
        set_stream_name = bytearray()
        set_stream_name.extend(self.COMMANDS["set_stream_name"])
        set_stream_name.extend(name.encode())
        self._sendCommand(set_stream_name)

        set_stream_url = bytearray()
        set_stream_url.extend(self.COMMANDS["set_stream_url"])
        set_stream_url.extend(url.encode())
        self._sendCommand(set_stream_url)

        self._sendCommand(self.COMMANDS["play_last_stream_set"])


if __name__ == "__main__":
    radioRemote = RadioRemote()
    radioRemote.connect()
    print(radioRemote.getCurrentlyPlaying())
    radioRemote.close()
