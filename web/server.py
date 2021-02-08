#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from autobahn.twisted.websocket import WebSocketClientProtocol,WebSocketClientFactory
import json
import copy
import base64
from kivy import utils as kivyutils
from kivy.network.urlrequest import UrlRequest
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from kivy.app import App
from kivy.clock import Clock
import socket
from kivy.app import App
from kivy.core.window import Window
import time, os
import urllib
import uuid

########################################################
#
#  Protocols
#
########################################################


class WSClientProtocol(WebSocketClientProtocol):
    def __init__(self,**kwargs):
        super(WebSocketClientProtocol, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def onConnect(self, res):
        self.factory.connectedProtocol = self
        print('connect')

    def onOpen(self):
        self.factory.resetDelay()
        print('open')

        self.app.Snapcast_onOpen()

    def send_message(self, msg):
        du = json.dumps(msg)
        self.sendMessage(bytes(du))

    def onClose(self, wasClean, code, reason):
        self.factory._proto = None
        print('onClose')
        self.app.ws_open = False

    def onMessage(self, payload, isBinary):
        message = json.loads(payload.decode('utf8'))
        self.factory.serverconn.on_message(message)

class WSClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = WSClientProtocol

    def clientConnectionFailed(self, connector, reason):
        print('clientConnectionFailed')
        self.retry(connector)
        pass

    def clientConnectionLost(self, connector, reason):
        print('clientConnectionLost')
        self.retry(connector)
        pass

    def __init__(self, url, serverconn):
        WebSocketClientFactory.__init__(self, url)
        self.serverconn = serverconn

class SnapCastConnection():
    """
    Python Library to talk with SnapCast
    """
    def __init__(self, **kwargs):
        from kivy.app import App
        self.app = App.get_running_app()
        self.messages = []

    def connect_to_snapcast(self, host, port):
        self.factory = WSClientFactory("ws://" + host + ":" + str(port) + "/jsonrpc", self)

        reactor.connectTCP(host, int(port), self.factory)
        print('Connect to server')

    def send_message(self, inst,msg,clbk):  # sends message to snapcast
        mesg = copy.copy(msg)
        mesg["id"] = str(uuid.uuid4())
        mesg["jsonrpc"] = "2.0"

        if self.factory.connectedProtocol is None:
            print("No connection")
        else:
            reactor.callFromThread(self.factory.connectedProtocol.send_message, mesg)
            mesg2 = copy.copy(mesg)
            mesg2["clbk"] = clbk
            mesg2["inst"] = inst
            self.messages.append(mesg2)



    def on_message(self,result):
        if "id" in result:
            for message in self.messages:
                if message["id"] == result["id"] :
                    if "inst" in message:
                        found = True
                        message["clbk"](message["inst"], result)
        else:
            method =result["method"]
            method = method.split(".")
            method = method[1] + "_" +method[0]
            try:
                method_to_call = getattr(self.app.wServer, method)
                method_to_call(result)
            except:
                print("No implementation for : "  + method)
