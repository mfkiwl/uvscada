import serial
import sys
import time
import struct
#import bytearray
import binascii
import argparse

class Timeout(Exception):
    pass

# 0xC0 
SLIP_END = chr(192)
# 0xDB
SLIP_ESC = chr(219)

XYZ_STATUS =        0x00
XYZ_CONTROL =    0x01     
# Set the step register to value (2's compliment)
XYZ_STEP_SET =    0x02
# Adjust the step register by argument
XYZ_STEP_ADD =    0x03
# Adjust the step register by argument
# #define XYZ_STEP_ADD    0x04
# Minimum velocity in steps/second     
XYZ_VELMIN =        0x05
# Maximum velocity in steps/second
XYZ_VELMAX =        0x06
# Acceleration/decceleration in steps/second**2 
XYZ_ACL =        0x07
XYZ_HSTEP_DLY =  0x08
XYZ_BASE = {'X':0x20, 'Y':0x40, 'Z':0x60}


def checksum(data):
    return (~(sum([ord(c) for c in data]) % 0x100)) & 0xFF

def slip(bytes):
    ret = SLIP_END
    for b in bytes:
        if b == SLIP_END:
            # If a data byte is the same code as END character, a two byte sequence of
            # ESC and octal 334 (decimal 220) is sent instead.  
            ret += SLIP_ESC + chr(220)
        elif b == SLIP_ESC:
            # If it the same as an ESC character, an two byte sequence of ESC and octal 335 (decimal
            # 221) is sent instead
            ret += SLIP_ESC + chr(221)
        else:
            ret += b
    # When the last byte in the packet has been
    # sent, an END character is then transmitted
    return ret + SLIP_END

#def deslip(bytes):

class Indexer:
    # wtf is acm
    def __init__(self, device=None, debug=False):
        self.serial = None
        self.debug = debug
        
        # Turns out both go in opposite direction I need
        self.invert_step = True
        
        self.seq = 0
        if device is None:
            for s in ("/dev/ttyUSB0",):
                try:
                    self.try_open(s)
                    print 'Opened %s okay' % s
                    break
                except IOError:
                    print 'Failed to open %s' % s
                    continue
            if self.serial is None:
                raise IOError("Failed to find a suitable device")
        else:
            self.try_open(device)
        
        # Clear old data
        if self.debug:
            print 'Flushing %d chars' % self.serial.inWaiting()
        self.serial.flushInput()

    def try_open(self, device):
        self.device = device
        self.serial = serial.Serial(port=self.device, baudrate=38400, timeout=1, writeTimeout=1)    
        if self.serial is None:
            raise IOError('Can not connect to serial')
        
    '''
    def recv(self):
        # Sync until first ~
        if self.debug:
            print 'pr0ndexer DEBUG: recv: waiting for opening ~'
        for _i in xrange(3):
            c = self.serial.read(1)
            if self.debug:
                print 'pr0ndexer DEBUG: recv open wait: got "%s", wait: %d' % (c, self.serial.inWaiting())
            if c == '~':
                break
        else:
            raise Timeout('Timed out waiting for opening ~')
        
        if self.debug:
            print 'pr0ndexer DEBUG: recv: waiting for closing ~'
        # Read until ~
        ret = ''
        for _i in xrange(60):
            c = self.serial.read(1)
            if c == '~':
                break
            ret += c
        else:
            raise Timeout('Timed out waiting for closing ~')
        
        if self.debug:
            print 'pr0ndexer DEBUG: recv: returning: "%s"' % (ret,)
        return ret
    '''
        
    def reg_write(self, reg, value):
        '''
        uint8_t checksum;
        uint8_t seq;
        uint8_t opcode;
        uint32_t value;
        '''
        #print self.seq, reg, value
        packet = struct.pack('<BBi', self.seq, 0x80 | reg, value)
        packet = chr(checksum(packet)) + packet
        out = slip(packet)
        self.seq = (self.seq + 1) % 0x100
        
        if self.debug:
            print 'pr0ndexer DEBUG: packet: %s' % (binascii.hexlify(packet),)
            print 'pr0ndexer DEBUG: sending: %s' % (binascii.hexlify(out),)
            #if self.serial.inWaiting():
            #    raise Exception('At send %d chars waiting' % self.serial.inWaiting())
        
        '''
        FIXME: its dropping chars at line speed
        need to move to higher performance serial I/O...ISR based
        '''
        if 1:
            self.serial.write(out)
            self.serial.flush()
        else:
            for c in out:
                self.serial.write(c)
                # if it doesn't get written we will not get a reply
                self.serial.flush()
                # drops below about .01, add some margin
                time.sleep(0.015)
        
    def step(self, axis, n, wait=True):
        if self.invert_step:
            n = -n
            
        if self.debug:
            print 'pr0ndexer DEBUG: stepping %d' % (n,)
        
        self.reg_write(XYZ_BASE[axis] + XYZ_STEP_SET, n)
        if wait:
            # some margin to make sure its done
            if n == 0:
                sleep_s = 0
            else:
                sleep_s = abs(n) / 371.0 + 0.2
            if self.debug:
                print 'pr0ndexer DEBUG: sleeping %d ms for %d steps' % (sleep_s * 1000, n)
            time.sleep(sleep_s)
        
    def steps_a_second(self):
        # for delay register of 2000
        return 370
    
    def step_rel(self, axis, n, wait=True):
        if self.invert_step:
            n = -n
        
        self.reg_write(XYZ_BASE[axis] + XYZ_STEP_ADD, n)
        if wait:
            # some margin to make sure its done
            time.sleep(abs(n) / 371.0 + 0.2)

def str2bool(arg_value):
    arg_value = arg_value.lower()
    if arg_value == "false" or arg_value == "0" or arg_value == "no" or arg_value == "off":
        return False
    else:
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test utility to drive serial port")
    parser.add_argument('--debug', action="store_true", default=False, help='Debug')
    parser.add_argument('port', nargs='?', default=None, help='Serial port to open. Default: snoop around')
    args = parser.parse_args()

    indexer = Indexer(device=args.port, debug=args.debug)
    
    '''
    half step delay of 2000 takes 10 seconds to do 10,000 steps
    10,000/10 = 1000 steps/second
    '''
    
    print 'X forward'
    # 8 => 35 = 27
    # 48 => 15 = 27
    # 10000 / 27 = 370 steps/second
    # 
    indexer.step('X', -10000)
    if 0:
        for dly in (1800, 2000, 2200):
            print 'Delay %d' % dly
            indexer.reg_write(0x20 + XYZ_HSTEP_DLY, dly)
            indexer.step('X', -10000)
            time.sleep(10)
        
    if 0:
        print 'X reverse'
        indexer.step('X', -50)
        print 'Y forward'
        indexer.step('Y', 50)
        print 'Y reverse'
        indexer.step('Y', -50)


    print
    print
    print
    while True:
        r = indexer.serial.read(1024)
        print 'Read %d bytes' % len(r)
        if not r:
            break
        print r
        print binascii.hexlify(r)

