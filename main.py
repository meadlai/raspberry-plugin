
import os
import logging
import threading
import json

from urllib import parse
from http.server import BaseHTTPRequestHandler, HTTPServer


class RequestHandler(BaseHTTPRequestHandler):

    STATIC_RETURN_SUCCESS = {"code": 0, "message": "success"}
    STATIC_RETURN_ERROR = {"code": 1, "message": "failed"}

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
        result = parse.urlparse(self.path)
        logging.warning("do_GET: %s " % result.path)

        if "fav" in result.path:
            logging.error("NO response for favorite.ico")
            self._set_headers_404()
            return

        if result.query:
            # self.send(MsgType.Text, Receiver='SpeechSynthesis', Data=message)
            message = result.query
            self.parent.speak(message)
        else:
            # return AudioUtil(1).Listen()
            # self.send(MsgType=MsgType.Start, Receiver='Record', Data=8)
            self.parent.listen()

        #
        self._set_headers_200()
        self.wfile.write(json.dumps(RequestHandler.STATIC_RETURN_SUCCESS).encode())


class Rest:

    logging.basicConfig(level=logging.INFO)

    def __init__(self):
        super().__init__()
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

    def speak(self, text):
        logging.warning("## speaking: %s", text)

    def listen(self):
        print("I am listening and recording...")
        logging.info("## listen ...")


if __name__ == '__main__':
    Rest()
