#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import shutil
import time
from functools import partial
from kivy.config import Config
import os
from kivy.graphics import Color, Rectangle, Point, GraphicException
Config.set('graphics','resizable',1)
from distutils.dir_util import copy_tree

from kivy.support import install_twisted_reactor
install_twisted_reactor() #enables Websockets
from kivy.properties import NumericProperty, StringProperty, ObjectProperty,BooleanProperty,ListProperty,DictProperty,ReferenceListProperty
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from setproctitle import setproctitle
from kivy.clock import Clock
from kivy import utils as kivyutils
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.animation import Animation
from kivy.storage.jsonstore import JsonStore
import urllib
import json
import copy
import gc
import uuid
os.environ['KIVY_IMAGE'] = 'pil'
os.environ['KIVY_TEXT'] = 'pil'
from kivy.cache import Cache
from kivy.loader import Loader
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel , TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from kivy.uix.screenmanager import NoTransition
from web.server import SnapCastConnection
from utils.loadkv import load_all_kv_files

class CloseableHeader(TabbedPanelHeader):
    pass


class GroupSettings(ModalView):

    error = StringProperty()

    def __init__(self, group,header,*args):
        self.group = group
        self.header = header
        super(GroupSettings, self).__init__(*args)
        self.app = App.get_running_app()
        self.SnapCastConnection = self.app.SnapCastConnection
        self.streams_dropdown = DropDown()

        for stream in self.app.wServer.streams:
            btn = Button(text=stream["id"] , size_hint_y=None, height=44)
            btn.bind(on_release=self.on_select_dropdown)
            self.streams_dropdown.add_widget(btn)
        self.ids.streams_btn.text = self.group.stream_id
        self.ids.streams_btn.bind(on_release=self.streams_dropdown.open)

    def on_select_dropdown(self, btn):
        self.streams_dropdown.select(btn.text)
        self.ids.streams_btn.text = btn.text
        self.SnapCastConnection.send_message(self, {"method": "Group.SetStream",
                                                    "params": {"id": self.group.sid, "stream_id": self.ids.streams_btn.text}},
                                             self.group.after_SetStream)

    def on_error(self, inst, text):
        if text:
            self.lb_error.size_hint_y = 1
            self.size = (400, 150)
        else:
            self.lb_error.size_hint_y = None
            self.lb_error.height = 0
            self.size = (400, 120)

    def _enter(self):
        if self.ids.name.text != self.group.name:
            self.SnapCastConnection.send_message(self, { "method": "Group.SetName","params": {"id": self.group.sid, "name": self.ids.name.text }}, self.group.after_SetName)


        self.dismiss()

    def _cancel(self):
        self.dismiss()


class ClientSettings(ModalView):

    error = StringProperty()

    def __init__(self, client,*args):
        self.client = client
        super(ClientSettings, self).__init__(*args)
        self.app = App.get_running_app()
        self.SnapCastConnection = self.app.SnapCastConnection
        self.groups_dropdown = DropDown()

        self.groups_name_sids = { group.name : self.app.wServer.sids_groups_inv[group] for group in self.app.wServer.sids_groups_inv.keys() }

        # btn = Button(text="New", size_hint_y=None, height=44)
        # btn.bind(on_release=self.on_select_dropdown)
        # self.groups_dropdown.add_widget(btn)

        for name in self.groups_name_sids.keys():
            btn = Button(text=name , size_hint_y=None, height=44)
            btn.bind(on_release=self.on_select_dropdown)
            self.groups_dropdown.add_widget(btn)
        self.ids.groups_btn.text = self.client.group.name
        self.ids.groups_btn.bind(on_release=self.groups_dropdown.open)

    def on_select_dropdown(self, btn):
        self.groups_dropdown.select(btn.text)
        self.ids.groups_btn.text = btn.text


    def on_error(self, inst, text):
        if text:
            self.lb_error.size_hint_y = 1
            self.size = (400, 150)
        else:
            self.lb_error.size_hint_y = None
            self.lb_error.height = 0
            self.size = (400, 120)

    def _enter(self):

        if self.ids.name.text != self.client.config_name:
            self.SnapCastConnection.send_message(self, { "method": "Client.SetName","params": {"id": self.client.sid, "name": self.ids.name.text }}, self.client.after_SetName)
        if self.ids.latency.text != self.client.config_latency:
            self.SnapCastConnection.send_message(self, { "method": "Client.SetLatency","params": {"id": self.client.sid, "latency": int(self.ids.latency.text) }}, self.client.after_SetLatency)
        if self.ids.groups_btn.text  != self.client.group.name:
            # client id an group
            print(self.client.sid)
            print(self.client.group.sid)
            # client new group
            print(self.ids.groups_btn.text)
            # select the new group id  from it’s name
            group_id   =self.groups_name_sids[self.ids.groups_btn.text] if self.ids.groups_btn.text != "New" else "123456"
            # client new group id
            #print(group_id )

            # get all clients from this group
            clients = []
            for client in self.app.wServer.sids_clients_inv:
                if client.group.sid == group_id :
                    print(client.config_host_name)
                    clients.append(client.sid)
            # add this client
            if self.client.sid not in clients:
                clients.append(self.client.sid)

            self.SnapCastConnection.send_message(self, { "method": "Group.SetClients","params": {"id": group_id, "clients": clients }}, self.app.wServer.after_GetStatus )


        self.dismiss()

    def _cancel(self):
        self.dismiss()


class wServer(Widget):
    # Base UI Widget - holds Server methods
    def __init__(self,res, **kwargs):
        super(wServer, self).__init__(**kwargs)
        self.sids_clients = {}
        self.sids_clients_inv = {}
        self.sids_groups = {}
        self.sids_groups_inv = {}

        self.app = App.get_running_app()
        self.version = None
        self.groups = self.ids.groups
        self.SnapCastConnection= self.app.SnapCastConnection

    def GetRPCVersion(self,clbk):
        self.SnapCastConnection.send_message( self,{"method": "Server.GetRPCVersion"} , clbk)

    def GetStatus(self,clbk):
        self.SnapCastConnection.send_message( self,{"method": "Server.GetStatus"} , clbk)

    def after_GetRPCVersion(self,obj,res):
        self.version = res["result"]

    def after_GetStatus(self,obj,res):
        if "error" in res:
            print res["error"]["message"]
            return
        # Delete internal refs.
        self.app.wServer.sids_groups ={}
        self.app.wServer.sids_groups_inv = {}
        self.app.wServer.sids_clients = {}
        self.app.wServer.sids_clients_inv ={}

        groups = res["result"]["server"]["groups"]
        self.app.wServer.streams = []
        self.app.wServer.streams = res["result"]["server"]["streams"]

        i = 0
        self.tabs = []

        # reset the display
        for group in self.groups.tab_list :
            self.groups.remove_widget(group)
        try:
            self.groups.remove_widget(self.groups.tab_list[0])
        except:
            pass
        for group in groups:

            Group = wGroup()
            Group.sid = group["id"]
            Group.muted = group["muted"]
            Group.name = group["name"]
            Group.stream_id = group["stream_id"]
            Group.text = Group.name  if Group.name  != "" else 'Group ' + str(i)
            Group.text +=  "\n(" + str(Group.stream_id) + ")"

            #self.groups.add_widget(Group)
            h = CloseableHeader()
            h.ids.lbl.text = Group.text
            Group.header = h
            if Group.muted == False:
                h.ids.mute_btn.background_normal = 'volume.png'
            else:
                h.ids.mute_btn.background_normal = 'volume_mute.png'

            self.groups.add_widget(h)
            h.content = Group



            for client in group["clients"]:
                Client =wClient()
                Client.sid = client["id"]
                Client.group = Group
                Client.lastseen = client["lastSeen"]
                Client.snapclient = client["snapclient"]
                Client.host = client["host"]
                Client.connected = client["connected"]
                Client.config_instance = client["config"]["instance"]
                Client.config_latency = client["config"]["latency"]
                Client.config_name = client["config"]["name"]
                Client.config_volume_muted = client["config"]["volume"]["muted"]
                Client.config_volume_percent = client["config"]["volume"]["percent"]
                Client.config_host_ip = client["host"]["ip"]
                Client.config_host_name = client["host"]["name"]

                Group.ids.clients.add_widget(Client)
            i += 1


        Clock.schedule_once(partial(self.switch), 0)

    def switch(self, *args):
        self.groups.switch_to(self.groups.tab_list[0])

    def OnVolumeChanged_Client(self,res):
        widget = self.app.wServer.sids_clients[res["params"]["id"]]
        widget.config_volume_percent = res["params"]["volume"]["percent"]
        widget.config_volume_muted = res["params"]["volume"]["muted"]

    def OnNameChanged_Client(self,res):
        widget = self.app.wServer.sids_clients[res["params"]["id"]]
        widget.config_name = res["params"]["name"]

    def OnLatencyChanged_Client(self,res):
        widget = self.app.wServer.sids_clients[res["params"]["id"]]
        widget.config_latency = res["params"]["latency"]

    def OnNameChanged_Group(self,res):
        widget = self.app.wServer.sids_groups[res["params"]["id"]]
        widget.name = res["params"]["name"]
        widget.header.ids.lbl.text = res["params"]["name"]


    def OnMute_Group(self,res):
        widget = self.app.wServer.sids_groups[res["params"]["id"]]
        widget.mute = res["params"]["mute"]
        if  widget.mute == False:
            widget.header.ids.mute_btn.background_normal =  'volume.png'
        else:
            widget.header.ids.mute_btn.background_normal =  'volume_mute.png'

class wClient(Widget):
    def __init__(self, **kwargs):
        super(wClient, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.config_volume_percent = 0
        self.SnapCastConnection = self.app.SnapCastConnection

    def set_volume(self, val):
        if val  !=   self.config_volume_percent :
            self.SnapCastConnection.send_message( self, {"method": "Client.SetVolume","params":{"id":self.sid,"volume":{"percent":val}}} , self.after_SetVolume)
        else:
            pass

    def set_mute(self):
        self.SnapCastConnection.send_message( self, {"method": "Client.SetVolume","params":{"id":self.sid,"volume":{"muted": not self.config_volume_muted}}} , self.after_SetMute)

    def press_client_settings(self):
        client_settings = ClientSettings(self)
        client_settings.open()

    def after_SetName(self, obj,res):
        obj.client.config_name =res["result"]["name"]


    def after_SetLatency(self, obj,res):
        obj.client.config_latency =res["result"]["latency"]


    def after_SetVolume(self, obj,res):
        self.config_volume_percent = res["result"]["volume"]["percent"]

    def after_SetMute(self, obj,res):
        self.config_volume_muted = res["result"]["volume"]["muted"]

    def _get_sid(self):
        return self._sid
    def _set_sid(self, value):
        self._sid = value
        self.app.wServer.sids_clients[value] = self
        self.app.wServer.sids_clients_inv = {v: k for k, v in self.app.wServer.sids_clients.iteritems()}
    sid = property(_get_sid, _set_sid)

class wGroup(BoxLayout):

    def __init__(self, **kwargs):
        super(wGroup, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.SnapCastConnection = self.app.SnapCastConnection

    def set_mute(self,obj,header):
        self.SnapCastConnection.send_message( header, {"method": "Group.SetMute","params":{"id":self.sid,"mute": not self.muted}} , self.after_SetMute)


    def after_SetMute(self, obj,res):
        self.muted = res["result"]["mute"]
        if  self.muted == False:
            obj.ids.mute_btn.background_normal =  'volume.png'
        else:
            obj.ids.mute_btn.background_normal =  'volume_mute.png'

    def after_SetStream(self, obj,res):
        obj.group.stream_id = res["result"]["stream_id"]
        text = obj.group.name if obj.group.name != "" else 'Group ' + obj.group.host_name
        obj.header.lbl.text = text + "\n(" + str(obj.group.stream_id) + ")"


    def after_SetName(self, obj,res):
        obj.group.name =res["result"]["name"]
        text = obj.group.name if obj.group.name != "" else 'Group ' + obj.group.host_name
        obj.header.lbl.text = text + "\n(" + str(obj.group.stream_id) + ")"

        self.text = obj.group.name

    def press_group_settings(self,obj,header):
        group_settings = GroupSettings(obj,header)
        group_settings.open()

    def _get_sid(self):
        return self._sid
    def _set_sid(self, value):
        self._sid = value
        self.app.wServer.sids_groups[value] = self
        self.app.wServer.sids_groups_inv = {v: k for k, v in self.app.wServer.sids_groups.iteritems()}
    sid = property(_get_sid, _set_sid)

class SnapcastUIApp(App):

    def __init__(self):
        super(SnapcastUIApp, self).__init__()
        self.register_event_type('on_btn_setting')
        self.root_dir = os.path.dirname(os.path.realpath(__file__))
        self.icon = os.path.join(self.root_dir, "res", "icon.png")
        self.platform = kivyutils.platform
        setproctitle('SnapCastUI')
        self.messenger_evt = None
        self.SnapCastConnection = SnapCastConnection()
        self.SnapCastConnection.connect_to_snapcast( "localhost", 1780)
        self.ws_open = False


    def on_start(self):
        self.wServer = self.root_window.children[0]


    def build(self):
        return wServer('')




    def Snapcast_onOpen(self):
        # On snapcast connection

        self.wServer.GetRPCVersion(self.wServer.after_GetRPCVersion)
        self.wServer.GetStatus(self.wServer.after_GetStatus)























    def on_btn_setting(self, sSection, sKey, sValue):
        pass