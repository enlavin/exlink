import os
import sys
import time
import serial
import datetime

DEBUG=True

SAMSUNG_REQUEST_PREFIX='\x08\x22'
SAMSUNG_RESPONSE_SUCCESS='\x03\x0C\xF1'
SAMSUNG_RESPONSE_FAILURE='\x03\x0C\xFF'

ST_INIT=0
ST_CC1=1
ST_CC2=2

# create class TVRemote(object): 
class TVRemote(object):
    def __init__(self, device=None):
        if device is None:
            device = '/dev/ttyS0'

        self.port = serial.Serial(device,
                baudrate=9600,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=3,
                writeTimeout=1)

    def close(self):
        self.port.close()

    def _checksum(self, cmd):
        chk = 0
        for ch in cmd:
            chk = (chk + ord(ch)) % 256
        return (~chk + 1) % 256

    def _analyze_response(self):
        status = ST_INIT
        while True:
            c = self.port.read(size=1)

            # timeout
            if not c:
                return False

            if DEBUG:
                print("%02X" % ord(c), sep=' ')

            if status == ST_INIT:
                if c == SAMSUNG_RESPONSE_SUCCESS[0]:
                    status = ST_CC1
                else:
                    status = ST_INIT
            elif status == ST_CC1:
                if c == SAMSUNG_RESPONSE_SUCCESS[1]:
                    status = ST_CC2
                else:
                    status = ST_INIT
            elif status == ST_CC2:
                if c == SAMSUNG_RESPONSE_SUCCESS[2]:
                    return True
                elif c == SAMSUNG_RESPONSE_FAILURE[2]:
                    return False
                else:
                    status = ST_INIT
            else:
                status = ST_INIT

    def _send_cmd(self, cmd1=0, cmd2=0, cmd3=0, value=0, timeout=0.1):
        cmd = "%s%c%c%c%c" % (SAMSUNG_REQUEST_PREFIX, cmd1, cmd2, cmd3, value)
        cmd += chr(self._checksum(cmd))

        self.port.write(cmd.encode('latin1'))

        time.sleep(timeout)

        response = self._analyze_response()

        return response == SAMSUNG_RESPONSE_SUCCESS

    def cmd_volume_set(self, volume):
        """Set the volume to a specific level (0-255)"""
        if volume > 255:
            volume = 255
        elif volume < 0:
            volume = 0
        return self._send_cmd(0x01, 0x00, 0x00, volume)
    cmd_volume_set.nargs = 1

    def cmd_volume_up(self):
        """Pump up the volume"""
        return self._send_cmd(0x01, 0x00, 0x01, 0x00)
    cmd_volume_up.nargs = 0

    def cmd_volume_down(self):
        """Pump down the volume"""
        return self._send_cmd(0x01, 0x00, 0x02, 0x00)
    cmd_volume_down.nargs = 0

    def cmd_volume_mute(self):
        """Mute"""
        return self._send_cmd(0x02, 0x00, 0x00, 0x00)
    cmd_volume_mute.nargs = 0

    def cmd_source_tv(self):
        """Change image source to TV"""
        return self._send_cmd(0x0a, 0x00, 0x00, 0x00)
    cmd_source_tv.nargs = 0

    def cmd_source_av(self, av=0):
        """Change image source to AV"""
        return self._send_cmd(0x0a, 0x00, 0x01, av)
    cmd_source_av.nargs = 0

    def cmd_source_svideo(self, svideo=0):
        """Change image source to SVideo"""
        return self._send_cmd(0x0a, 0x00, 0x02, svideo)
    cmd_source_svideo.nargs = 0

    def cmd_source_component(self, component=0):
        """Change image source to Component"""
        return self._send_cmd(0x0a, 0x00, 0x03, component)
    cmd_source_component.nargs = 0

    def cmd_source_pc(self, pc=0):
        """Change image source to PC"""
        return self._send_cmd(0x0a, 0x00, 0x04, pc)
    cmd_source_pc.nargs = 0

    def cmd_source_hdmi(self, hdmi=0):
        """Change image source to HDMI"""
        return self._send_cmd(0x0a, 0x00, 0x05, hdmi)
    cmd_source_hdmi.nargs = 0

    def cmd_source_dvi(self, dvi=0):
        """Change image source to DVI"""
        return self._send_cmd(0x0a, 0x00, 0x06, dvi)
    cmd_source_dvi.nargs = 0

    def cmd_tv_channel_set(self, channel):
        """Change TV channel (0-255)"""
        if channel > 255:
            chanel = 255
        elif channel < 0:
            channel = 0

        return self._send_cmd(0x04, 0, 0, channel)
    cmd_tv_channel_set.nargs = 1

    def cmd_tv_channel_up(self):
        """Change to next TV channel"""
        return self._send_cmd(0x03, 0x00, 0x01, 0x00)
    cmd_tv_channel_up.nargs = 0

    def cmd_tv_channel_down(self):
        """Change to previous TV channel"""
        return self._send_cmd(0x03, 0x00, 0x02, 0x00)
    cmd_tv_channel_down.nargs = 0

    def cmd_power_off(self):
        """Power off TV. Warning: cannot be powered up again with ex-link cable"""
        return self._send_cmd(0x00, 0x00, 0x00, 0x01)
    cmd_power_off.nargs = 0

    def cmd_power_on(self):
        """Power on TV. Actually not working"""
        return self._send_cmd(0x00, 0x00, 0x00, 0x02)
    cmd_power_on.nargs = 0


    @classmethod
    def method_list(cls):
        command_methods = [cls.__dict__[m] for m in cls.__dict__.keys() if m.startswith("cmd_")]
        return command_methods

    @classmethod
    def command_list(cls):
        commands = [method.__name__[4:] for method in cls.method_list()]
        commands.sort()
        return commands

if __name__ == '__main__':
    try:
        tv = TVRemote("/dev/ttyS0")
        tv.cmd_source_pc(pc=0)
        tv.cmd_volume_mute()
        time.sleep(0.5)
        tv.cmd_set_volume(15)
    finally:
        tv.close() # close


