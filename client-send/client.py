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

def sendAllInt(socket, integerData):
    try:
        strLen = struct.pack('i', integerData)
        socket.sendall(strLen)
    except socket.error as msg:
        return False
    return True

def sendAllString(socket, string):
    try:
        socket.sendall(string)
    except socket.error as msg:
        return False
    return True

def sendFile(sock, filePath, relativePath):
    length = len(relativePath)
    result = sendAllInt(sock, length)
    if not result:
        return
    result = sendAllString(sock, relativePath)
    if not result:
        return
    fileSize = os.path.getsize(filePath)
    result = sendAllInt(sock, fileSize)
    if not result:
        return
    file = open(filePath, 'r')
    if not file:
        return
    data = file.read(1024)
    while len(data) != 0:
        result = sendAllString(sock, data)
        if not result:
            file.close()
            return
        data = file.read(1024)
    file.close()


def relativePathWithFilePath(filePath, fileDirPath, peerSystem, pathSeparator):
    relative = filePath[len(fileDirPath)+1:]
    print 'relative:', relative, ' file dir:', fileDirPath, ' filePath:', filePath
    peerPathSeparator = '\\' if peerSystem == 'Windows' else '/'
    if peerPathSeparator != pathSeparator:
        relative = string.join(string.split(relative, pathSeparator), peerPathSeparator)
    return relative

if len(sys.argv) != 3:
    exitWithString('python client.py /Users/kudocc/Desktop/xxx 127.0.0.1:7777')
filePath = sys.argv[1]
filePath = os.path.realpath(filePath)
system = platform.system()
pathSeparator = '\\' if system == 'Windows' else '/'
print 'path separator:', pathSeparator
#check filePath
if not os.path.exists(filePath):
    exitWithString('file or directory does not exit')
#check host:port
address = sys.argv[2]
index = string.find(address, ':');
if index == -1:
    exitWithString('can not find : in address string')
ip = address[:index]
#ip = '192.168.0.102'
port = int(address[index+1:])
#port = 7777
print 'ip:', ip, ' port:', port
s = None
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
    s = None
try:
    print 'before'
    s.connect((ip, port))
    print 'after'
except socket.error as msg:
    print 'here'
    s.close()
    s = None
if s is None:
    print 'could not open socket'
    sys.exit(1)

#get peer system
dataBuf = ''
peerSystem = ''
while 1:
    data = s.recv(1024)
    if len(data) == 0:
        exitWithString('peer close socket')
    dataBuf += data
    if len(dataBuf) < 4:
        continue
    systemLen = struct.unpack('i', dataBuf[0:4])
    systemLen = int(systemLen[0])
    if len(dataBuf) < 4 + systemLen:
        continue
    peerSystem = dataBuf[4:]
    break
print 'peer system:', peerSystem

if os.path.isfile(filePath):
    dir = os.path.dirname(filePath)
    relative = relativePathWithFilePath(filePath, dir, peerSystem, pathSeparator)
    sendFile(s, filePath, relative)
    sys.exit(1)

dir = os.path.dirname(filePath)
list_dirs = os.walk(filePath)
listFile = []
for root, dirs, files in list_dirs:
    for f in files:
        listFile.append(os.path.join(root, f))

for path in listFile:
    relative = relativePathWithFilePath(path, dir, peerSystem, pathSeparator)
    sendFile(s, path, relative)
    print 'sended file:', path, ' relative:', relative

s.close()






