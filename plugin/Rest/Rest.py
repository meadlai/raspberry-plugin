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
import urllib.request

from MsgProcess import MsgProcess, MsgType
from urllib import parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn


class RequestHandler(BaseHTTPRequestHandler):

    STATIC_SIGNAL_EVENT = threading.Event()
    STATIC_LISTEN_RESULT_TEXT = ""
    STATIC_RETURN_SUCCESS = {"code": 0, "message": "success"}
    STATIC_RETURN_ERROR = {"code": 1, "message": "failed"}
    STATIC_RECORDING_SECONDS = 8
    STATIC_TEXT_ENCODING = 'utf-8'

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
            self.wfile.write(json.dumps(RequestHandler.STATIC_RETURN_SUCCESS).encode(RequestHandler.STATIC_TEXT_ENCODING))
            return

        if "listen" in url_obj.path:
            seconds = RequestHandler.STATIC_RECORDING_SECONDS
            if url_obj.query and url_obj.query.isdigit():
                seconds = int(url_obj.query)
            if seconds >= 30:
                seconds = 30
            self.parent.listen(seconds)
            logging.warning("## :HTTP Thread waiting...")
            RequestHandler.STATIC_SIGNAL_EVENT.wait(seconds*2)
            logging.warning("## :HTTP Thread awake...")
            RequestHandler.STATIC_SIGNAL_EVENT.clear()
            self._set_headers_200()
            self.wfile.write(json.dumps({"code": 0, "message": urllib.parse.unquote(RequestHandler.STATIC_LISTEN_RESULT_TEXT)}, ensure_ascii=False).encode(RequestHandler.STATIC_TEXT_ENCODING))
            return

        # for recording plugin to call
        if "callback" in url_obj.path:
            # set global shared variable with result
            RequestHandler.STATIC_LISTEN_RESULT_TEXT = url_obj.query
            logging.warning("## :callback invoke...")
            RequestHandler.STATIC_SIGNAL_EVENT.set()
            self._set_headers_200()
            self.wfile.write(json.dumps(RequestHandler.STATIC_RETURN_SUCCESS).encode(RequestHandler.STATIC_TEXT_ENCODING))
            return





class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

class Rest(MsgProcess):

    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        logging.warning("## Rest starting ###")
        thread = threading.Thread(target=self._start_http_server)
        thread.daemon = False
        thread.start()
        logging.warning("## thread starting ###")

    def _start_http_server(self):
        # Here is the trick to pass parent to handler
        def handler_wrapper(*args):
            RequestHandler(self, *args)
        ##
        logging.warning("## Rest _startHTTPServer ###")
        server_address = ('0.0.0.0', 9090)
        server = ThreadingSimpleServer(server_address, handler_wrapper)
        server.serve_forever()

    def speak(self, message):
        logging.warning("## :Rest.Speak: %s ", message)
        self.send(MsgType.Text, Receiver='SpeechSynthesis', Data=message)

    def listen(self, seconds):
        logging.warning("## :Rest.Listen ## ")
        if not seconds:
            logging.info("record time not set")
            seconds = Rest.STATIC_RECORDING_TIME
            logging.warning("record time set to: %s", seconds)
        self.send(MsgType=MsgType.Start, Receiver='Record', Data=seconds)
        logging.warning("## :Record starting")
        return

    def Text(self, message):
        logging.warning("### Text ###")
        ''' callback from recording and returning result '''
        text = message['Data']
        if not text:
            logging.warning("## NO text returned")
            text = ""
        logging.warning("### return text is %s", text)
        url = 'http://localhost:9090/callback?'+urllib.parse.quote(text)
        logging.warning("## .url = %s", url)
        request = urllib.request.Request(url)
        result = urllib.request.urlopen(request).read()
        logging.info("## .Recording recognize callback done: %s ", result)

