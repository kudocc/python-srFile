#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import string
import platform
import socket
import struct

def exitWithString(errorString):
    print errorString
    sys.exit(0)

HOST = None               # Symbolic name meaning all available interfaces
PORT = 7777               # Arbitrary non-privileged port

if len(sys.argv) != 2:
    exitWithString('Please input a directory path to keep files')

dirPath = sys.argv[1]
if len(dirPath) == 0:
    exitWithString('directory name length is zero')

dirPath = os.path.realpath(dirPath)
#check file name
if not os.path.exists(dirPath):
    exitWithString('directory does not exit')
if os.path.isfile(dirPath):
    eixtWithString('Can not be a file')

system = platform.system()

s = None
for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
                              socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        s = None
        print msg
        continue
    try:
        s.bind(sa)
        s.listen(1)
    except socket.error as msg:
        print msg
        s.close()
        s = None
        continue
    break
if s is None:
    print 'could not open socket'
    sys.exit(1)
conn, addr = s.accept()
print 'Connected by', addr

#send system
strSystemLen = struct.pack('i', len(system))
conn.sendall(strSystemLen)
conn.sendall(system)
print 'sended system:', system, ' length:', len(system)

dataBuffer = ''
#read file path, file data
while 1:
    data = conn.recv(1024)
    if len(data) == 0:
        break
    dataBuffer += data;
    #path len
    if len(dataBuffer) < 4:
        continue
    #path
    pathLen = struct.unpack('i', dataBuffer[0:4])
    pathLen = pathLen[0]
    if len(dataBuffer) < 4+pathLen:
        continue
    relativePath = dataBuffer[4:4+pathLen]
    if len(dataBuffer) < 8+pathLen:
        continue
    #data len
    dataLenString = dataBuffer[4+pathLen:8+pathLen]
    print 'dataLenString length:', len(dataLenString)
    dataLen = struct.unpack('i', dataLenString)
    dataLen = dataLen[0]
    #read and write to file
    filePath = os.path.join(dirPath, relativePath)
    print 'dirPath:', dirPath, ' file path:', filePath
    #create file component
    if not os.path.exists(os.path.dirname(filePath)) and not os.path.isfile(os.path.dirname(filePath)):
        try:
            os.makedirs(os.path.dirname(filePath))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    print 'relative path:', relativePath, ' file path:', filePath, ' dataLen:', dataLen
    dataBuffer = dataBuffer[8+pathLen:]
    file = open(filePath, 'w')
    #read dataLen
    file.write(dataBuffer)
    writeLen = len(dataBuffer)
    dataBuffer = ''
    while writeLen < dataLen:
        data = conn.recv(1024)
        if len(data) == 0:
            break
        dataBuffer += data
        if len(dataBuffer) + writeLen > dataLen:
            file.write(dataBuffer[:dataLen-writeLen])
            dataBuffer = dataBuffer[dataLen-writeLen:]
            writeLen = dataLen
        else:
            file.write(dataBuffer)
            writeLen += len(dataBuffer)
            dataBuffer = ''

    file.close()


conn.close()













