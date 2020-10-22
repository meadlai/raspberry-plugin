# -*- coding: utf-8 -*-
# @Author: meadlai
# @Date: 2020-10-22 23:25:00
# @LastEditTime: 2020-10-22 23:25:00
# @Description: 本插件语音Rest识别,Rest播报
import os
import logging
import threading

from MsgProcess import MsgProcess, MsgType
from urllib import parse
from http.server import BaseHTTPRequestHandler, HTTPServer



class Rest(MsgProcess):

    class RequestHandler(BaseHTTPRequestHandler):

        # 处理声音::文字转声音 || 声音(录音)转文字
        # curl -X PUT raspberrypi:9090/speak?message=hello
        # curl -X PUT raspberrypi:9090/listen
        def do_PUT(self):
            result = parse.urlparse(self.path)
            logging.warning("do_PUT: %s " % result.path)
            if result.query:
                message = "大家好"
                #self.send(MsgType.Text, Receiver='SpeechSynthesis', Data=message)
                self.parent.Speak(message)
                return "Success"
            else:
                # return AudioUtil(1).Listen()
                #self.send(MsgType=MsgType.Start, Receiver='Record', Data=8)
                self.parent.Listen()

    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        logging.warning("## Rest 正在启动 ###")
        thread = threading.Thread(target=self._startHTTPServer)
        thread.start()
        logging.warning("## thread 正在启动 ###")

    def _startHTTPServer(self):
        logging.warning("## Rest _startHTTPServer ###")
        serverAddress = ('0.0.0.0', 9090)
        server = HTTPServer(serverAddress, Rest.RequestHandler)
        server.serve_forever()

    def Speak(self, message):
        logging.warning("## Outter:Rest.Speak: %s ", message)
        self.send(MsgType.Text, Receiver='SpeechSynthesis', Data=message)

    def Listen(self):
        logging.warning("## Outter:Rest.Listen ## ")
        self.send(MsgType=MsgType.Start, Receiver='Record', Data=8)

    def Text(self, message):  
        logging.warning("### WebServer Text ###")
        ''' 处理文本内容 调用相关插件 '''
        text = message['Data']
        if not text:
            return
        logging.warning("### return text is %s", text)
        self.Stop()  # 报完IP即退出。

