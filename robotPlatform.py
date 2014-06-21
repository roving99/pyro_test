#!/usr/bin/python
# Pyro server - gets data from md25 robot and serves as a pyro RPC

import random
import sys
import time
import math
import copy
import json
import select

import Pyro.core
import Pyro.naming

import md25_fake as md25

class Movement(Pyro.core.ObjBase):

    def _setup(self, robot):
        self.robot = robot

    def __init__(self, robot):
        Pyro.core.ObjBase.__init__(self)
        self._setup(robot)

    def reset(self):        
        self.robot.reset()

    def move(self, t,r):        
        self.robot.move(t, r)

    def stop(self):        
        self.robot.move(0.0,0.0)

    def forward(self, move_time):
        self.robot.move(0.2,0.0)

    def backward(self, move_time):
        self.robot.move(-0.2,0.0)

    def left(self, move_time):
        self.robot.move(0.0,0.2)
   
    def right(self, move_time):
        self.robot.move(0.0,-0.2)

    def all(self):
        return world
    
    def kill(self):     # kill this server!!
        running = False

world = []
running = True

m=md25.Md25()

world = m.get('all',True)

print world

if __name__ == "__main__":
    print "initialize pyro server.."
    Pyro.core.initServer()                              # Create a Pyro server and register our module with it
    print "find name server.."
    ns = Pyro.naming.NameServerLocator().getNS()        # find the name server.
    print "found", ns
    daemon = Pyro.core.Daemon()                         # create daemon
    daemon.useNameServer(ns)                            # Using the name-server discovered..
    try:
        uri = daemon.connect(Movement(m),"robotmovement")   # ..connect Movement object.
    except:
        print "failed to register name"
        sys.exit()
    lastTime = time.time()

    while running:
        socks = daemon.getServerSockets()               # get sockets that deamon is watching
        ins, outs, exs = select.select(socks, [], [], 0.1)# 0 seconds time-out = poll, do not block.
        for s in socks:
            if s in ins:                                # pyro socket waiting?
                daemon.handleRequests()
                break                                   # no need to look at rest of sockets - handleRequests does all.
        if (time.time()-lastTime)>0.1:
            world = m.get('all',True)
            lastTime = time.time()

    daemon.shutdown(True)                               # clean-up and de-register objects.

