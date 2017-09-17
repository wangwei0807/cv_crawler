#!/usr/bin/env python
# -*- coding:utf8 -*-
#
# created by shibaofeng@ipin.com 2017/8/4
#
from pyvirtualdisplay import Display


class Xvfb(object):
    def __init__(self, width=1366, height=768, visible=0):
        self.__virtual_display = None
        self.width = width
        self.height = height
        self.visible = visible

    def __init_display(self):
        if self.__virtual_display is None:
            self.__virtual_display = Display(visible=self.visible, size=(self.width, self.height))
            self.__virtual_display.start()

    def __enter__(self):
        self.__init_display()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_display()

    def _close_display(self):
        if self.__virtual_display:
            try:
                self.__virtual_display.close()
            except:
                pass
        self.__virtual_display = None

    @staticmethod
    def run(func, *args, **kwargs):
        runner = Xvfb()
        with runner:
            return func(*args, **kwargs)