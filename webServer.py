#!/usr/bin/python

import tornado.ioloop
import tornado.web
import tornado.websocket
import datetime
import json

import Pyro.core
import Pyro.naming

from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)

clients = dict() # we store clients in dictionary..

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        print "GET received"
        self.render("www/index.html")

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        self.id = self.get_argument("Id")
        clients[self.id] = {"id": self.id, "object": self}
        tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=1),self.count)
        print "WebSocket opened"

    def on_message(self, message):        
        self.write_message(u"yo!")
        print "Client %s received a message : %s" % (self.id, message)
        if (message=='left'):
            movement.left(0.5)
        if (message=='right'):
            movement.right(0.5)
        if (message=='forward'):
            movement.forward(0.5)
        if (message=='backward'):
            movement.backward(0.5)
        if (message=='stop'):
            movement.stop()

        
    def on_close(self):
        if self.id in clients:
            del clients[self.id]
            print "WebSocket closed"

    def count(self):
        global c
        global movement
        world = movement.all()
        self.write_message(json.dumps(world))
        #self.write_message("count : %s"%(str(c)))
        #c+=1
        #print "loop"
        tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(milliseconds=100),self.count)

c = 0

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/www/(.*)', tornado.web.StaticFileHandler, {'path':'www'}),
    (r'/ws', WebSocketHandler),
])

if __name__ == '__main__':

    movement = Pyro.core.getProxyForURI("PYRONAME://robotmovement")

    print "NameSever returned", movement
    print options
    parse_command_line()
    app.listen(options.port)
    print "starting ioloop..."
    tornado.ioloop.IOLoop.instance().start()

    print "stopping"

