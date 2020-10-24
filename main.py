# -*- coding: utf-8 -*-
# @Author: meadlai
# @Date: 2020-10-22 23:25:00
# @LastEditTime: 2020-10-22 23:25:00
# @Description: This plugin is for text2audio and recording_audio2text
#

import os
import logging
import threading
import json
import time

from MsgProcess import MsgProcess, MsgType
from urllib import parse
from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):

    STATIC_RETURN_SUCCESS = {"code": 0, "message": "success"}
    STATIC_RETURN_ERROR = {"code": 1, "message": "failed"}
    STATIC_RECORDING_SECONDS = 8

    def __init__(self, prt, *args):
        self.parent = prt
        BaseHTTPRequestHandler.__init__(self, *args)

    def _set_headers_200(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _set_headers_404(self):
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        global result
        url_obj = parse.urlparse(self.path)
        logging.warning("do_GET: %s " % url_obj.path)

        if "fav" in url_obj.path:
            logging.error("NO response for favorite.ico")
            self._set_headers_404()
            return

        if "speak" in url_obj.path:
            message = url_obj.query
            self.parent.speak(message)
            self._set_headers_200()
            self.wfile.write(json.dumps(RequestHandler.STATIC_RETURN_SUCCESS).encode())
            return
        else:
            seconds = RequestHandler.STATIC_RECORDING_SECONDS
            if url_obj.query and url_obj.query.isdigit():
                seconds = int(url_obj.query)
            if seconds > 30:
                seconds = 30
            self.parent.listen(seconds)
            logging.warning("## wake here#2")
            if not result:
                self._set_headers_200()
                self.wfile.write(json.dumps(RequestHandler.STATIC_RETURN_ERROR).encode())
                return
            else:
                self._set_headers_200()
                self.wfile.write(json.dumps({"code": 0, "message": self.parent.result}).encode())
                return


result = None
result_available = threading.Event()

class Rest(MsgProcess):
    test = "test_string"

    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        logging.warning("## Rest starting ###")
        thread = threading.Thread(target=self._start_http_server)
        thread.start()
        logging.warning("## thread starting ###")

    def _start_http_server(self):
        # Here is the trick to pass parent to handler
        def handler_wrapper(*args):
            RequestHandler(self, *args)
        ##
        logging.warning("## Rest _startHTTPServer ###")
        server_address = ('0.0.0.0', 9090)
        server = HTTPServer(server_address, handler_wrapper)
        server.serve_forever()

    def speak(self, message):
        logging.warning("## :Rest.Speak: %s ", message)
        self.send(MsgType.Text, Receiver='SpeechSynthesis', Data=message)

    def listen(self, seconds):
        global result
        result = None

        logging.warning("## :Rest.Listen ## ")
        if not seconds:
            logging.info("record time not set")
            seconds = Rest.STATIC_RECORDING_TIME
            logging.warning("record time set to: %s", seconds)

        self.send(MsgType=MsgType.Start, Receiver='Record', Data=seconds)
        logging.warning("waiting here")
        # wait the callback from recognize engine to return the text
        Rest.result_available.wait()
        logging.warning("## wake here#1")

    def Text(self, message):
        global result
        logging.warning("### WebServer Text ###")
        ''' callback from recording and returning result '''
        text = message['Data']
        if not text:
            logging.warning("## NO text returned")
            return
        result = text
        logging.warning("### return text is %s", result)
        Rest.result_available.set()
        logging.warning("### thread event set: %s", self.test)
        self.test = "new value"
        logging.warning("### thread event set: %s", self.test)


