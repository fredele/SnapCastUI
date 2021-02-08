#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import re
import os
from kivy.lang.builder import Builder

def load_all_kv_files():
    '''Import all .kv files '''

    Builder.load_file('./widgets/volslider.kv')
    Builder.load_file('./screens/playlist.kv')
    Builder.load_file('./screens/artwork.kv')
    Builder.load_file('./screens/player.kv')
    Builder.load_file('./widgets/cover.kv')
    Builder.load_file('./widgets/alpha.kv')
    Builder.load_file('./widgets/trackalbum.kv')
    Builder.load_file('./widgets/trackplaylist.kv')
    Builder.load_file('./widgets/tracksearch.kv')
    Builder.load_file('./basewidgets/rotatedimage.kv')
    Builder.load_file('./widgets/bargraph.kv')
    Builder.load_file('./widgets/trackprogress.kv')
    Builder.load_file('./widgets/thumbnail.kv')
    Builder.load_file('./widgets/file.kv')
    Builder.load_file('./widgets/thumbnails.kv')
    Builder.load_file('./widgets/files.kv')
    Builder.load_file('./widgets/next.kv')
    Builder.load_file('./widgets/restart.kv')
    Builder.load_file('./widgets/previous.kv')
    Builder.load_file('./widgets/play.kv')
    Builder.load_file('./widgets/mute.kv')
    Builder.load_file('./widgets/vol.kv')
    Builder.load_file('./modals/vol.kv')
    Builder.load_file('./screens/albumviewer.kv')
    Builder.load_file('./modals/videoviewer.kv')
    Builder.load_file('./modals/fileselected.kv')
    Builder.load_file('./modals/videoselected.kv')
    Builder.load_file('./modals/queryselected.kv')
    Builder.load_file('./modals/streamselected.kv')
    Builder.load_file('./modals/artworkviewer.kv')
    Builder.load_file('./widgets/menu.kv')
    Builder.load_file('./modals/dsp.kv')
    Builder.load_file('./modals/lyrics.kv')
    Builder.load_file('./screens/search.kv')
    Builder.load_file('./modals/settings.kv')
    Builder.load_file('./modals/select.kv')
    Builder.load_file('./modals/editviewer.kv')
    Builder.load_file('./widgets/widgets.kv')
    Builder.load_file('./dsp/dspbasewidgets.kv')