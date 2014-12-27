# Copyright (c) 2010-2014, TOMOHIRO KUSUMI
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import fileobj.extension
import fileobj.filebytes
import fileobj.util
from fileobj.util import get_size_string, byte_to_int, le_to_int

USB_DT_DEVICE    = 0x01
USB_DT_CONFIG    = 0x02
USB_DT_STRING    = 0x03
USB_DT_INTERFACE = 0x04
USB_DT_ENDPOINT  = 0x05

TYPE_CLASS       = (0x01 << 5)
HID_DT_HID       = (TYPE_CLASS | 0x01)
HID_DT_REPORT    = (TYPE_CLASS | 0x02)
HID_DT_PHYSICAL  = (TYPE_CLASS | 0x03)

def get_text(co, fo, args):
    b = fo.read(args[-1], fileobj.util.KiB)
    if not b:
        fileobj.extension.fail("Empty buffer")
    desc = []
    while b:
        if len(b) <= 2:
            fileobj.extension.fail("Invalid descriptor: " + btoh(b))
        bLength = fileobj.filebytes.ord(b[0:1])
        bDescriptorType = fileobj.filebytes.ord(b[1:2])
        if bLength <= 0:
            fileobj.extension.fail("Invalid bLength: %d" % bLength)
        d = b[:bLength]
        if len(d) != bLength or len(d) <= 2:
            fileobj.extension.fail("Invalid bLength: %d" % bLength)
        desc.append(d)
        b = b[bLength:]
    l = []
    for b in desc:
        bLength = fileobj.filebytes.ord(b[0:1])
        bDescriptorType = fileobj.filebytes.ord(b[1:2])
        if bDescriptorType == USB_DT_DEVICE:
            l.extend(__get_device_descriptor(b))
        elif bDescriptorType == USB_DT_CONFIG:
            l.extend(__get_config_descriptor(b))
        elif bDescriptorType == USB_DT_STRING:
            l.extend(__get_string_descriptor(b))
        elif bDescriptorType == USB_DT_INTERFACE:
            l.extend(__get_interface_descriptor(b))
        elif bDescriptorType == USB_DT_ENDPOINT:
            l.extend(__get_endpoint_descriptor(b))
        elif bDescriptorType == HID_DT_HID:
            l.extend(__get_hid_descriptor(b))
        else:
            l.extend(__get_unknown_descriptor(b))
        l.append('')
    return l

def btoh(b):
    return ''.join(["\\x%02X" % x
        for x in fileobj.filebytes.ords(b)])

def __get_device_descriptor(b):
    assert len(b) == 18, "Invalid device descriptor: " + btoh(b)
    l = []
    l.append("device descriptor " + get_size_string(len(b)))
    l.append("    bLength            = %d" % byte_to_int(b[0:1]))
    l.append("    bDescriptorType    = %d" % byte_to_int(b[1:2]))
    l.append("    bcdUSB             = 0x%04X" % le_to_int(b[2:4]))
    l.append("    bDeviceClass       = %d" % byte_to_int(b[4:5]))
    l.append("    bDeviceSubClass    = %d" % byte_to_int(b[5:6]))
    l.append("    bDeviceProtocol    = %d" % byte_to_int(b[6:7]))
    l.append("    bMaxPacketSize0    = %d" % byte_to_int(b[7:8]))
    l.append("    idVendor           = 0x%04X" % le_to_int(b[8:10]))
    l.append("    idProduct          = 0x%04X" % le_to_int(b[10:12]))
    l.append("    bcdDevice          = 0x%04X" % le_to_int(b[12:14]))
    l.append("    iManufacturer      = %d" % byte_to_int(b[14:15]))
    l.append("    iProduct           = %d" % byte_to_int(b[15:16]))
    l.append("    iSerialNumber      = %d" % byte_to_int(b[16:17]))
    l.append("    bNumConfigurations = %d" % byte_to_int(b[17:18]))
    return l

def __get_config_descriptor(b):
    assert len(b) == 9, "Invalid config descriptor: " + btoh(b)
    l = []
    l.append("config descriptor " + get_size_string(len(b)))
    l.append("    bLength             = %d" % byte_to_int(b[0:1]))
    l.append("    bDescriptorType     = %d" % byte_to_int(b[1:2]))
    l.append("    wTotalLength        = %d" % le_to_int(b[2:4]))
    l.append("    bNumInterfaces      = %d" % byte_to_int(b[4:5]))
    l.append("    bConfigurationValue = %d" % byte_to_int(b[5:6]))
    l.append("    iConfiguration      = %d" % byte_to_int(b[6:7]))
    l.append("    bmAttributes        = 0x%02X" % byte_to_int(b[7:8]))
    l.append("    bMaxPower           = %d" % byte_to_int(b[8:9]))
    return l

def __get_string_descriptor(b):
    assert len(b) > 2, "Invalid string descriptor: " + btoh(b)
    l = []
    l.append("string descriptor " + get_size_string(len(b)))
    l.append("    bLength         = %d" % byte_to_int(b[0:1]))
    l.append("    bDescriptorType = %d" % byte_to_int(b[1:2]))
    return l

def __get_interface_descriptor(b):
    assert len(b) == 9, "Invalid interface descriptor: " + btoh(b)
    l = []
    l.append("interface descriptor " + get_size_string(len(b)))
    l.append("    bLength            = %d" % byte_to_int(b[0:1]))
    l.append("    bDescriptorType    = %d" % byte_to_int(b[1:2]))
    l.append("    bInterfaceNumber   = %d" % byte_to_int(b[2:3]))
    l.append("    bAlternateSetting  = %d" % byte_to_int(b[3:4]))
    l.append("    bNumEndpoints      = %d" % byte_to_int(b[4:5]))
    l.append("    bInterfaceClass    = %d" % byte_to_int(b[5:6]))
    l.append("    bInterfaceSubClass = %d" % byte_to_int(b[6:7]))
    l.append("    bInterfaceProtocol = %d" % byte_to_int(b[7:8]))
    l.append("    iInterface         = %d" % byte_to_int(b[8:9]))
    return l

def __get_endpoint_descriptor(b):
    assert len(b) == 7, "Invalid endpoint descriptor: " + btoh(b)
    l = []
    l.append("endpoint descriptor " + get_size_string(len(b)))
    l.append("    bLength          = %d" % byte_to_int(b[0:1]))
    l.append("    bDescriptorType  = %d" % byte_to_int(b[1:2]))
    l.append("    bEndpointAddress = 0x%02X" % byte_to_int(b[2:3]))
    l.append("    bmAttributes     = 0x%02X" % byte_to_int(b[3:4]))
    l.append("    wMaxPacketSize   = 0x%04X" % le_to_int(b[4:6]))
    l.append("    bInterval        = %d" % byte_to_int(b[6:7]))
    return l

def __get_hid_descriptor(b):
    assert len(b) > 2, "Invalid hid descriptor: " + btoh(b)
    l = []
    l.append("hid descriptor " + get_size_string(len(b)))
    l.append("    bLength         = %d" % byte_to_int(b[0:1]))
    l.append("    bDescriptorType = %d" % byte_to_int(b[1:2]))
    return l

def __get_unknown_descriptor(b):
    assert len(b) > 2, "Invalid descriptor: " + btoh(b)
    l = []
    l.append("unknown descriptor " + get_size_string(len(b)))
    l.append("    bLength         = %d" % byte_to_int(b[0:1]))
    l.append("    bDescriptorType = %d" % byte_to_int(b[1:2]))
    return l
