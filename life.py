#!/usr/local/bin/python3

import argparse
import csv
import http.server
import socketserver
import sys

running = True
def quit():
    global running
    running = False
    print("running = %s" % running)

def isRunning():
    global running
    print("isRunning = %s" % running)
    return running

class myHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        print("path=%s" % self.path)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        if self.path == '/quit':
            print("quitting")
            self.wfile.write(b'quitting!')
            quit()
        else:
            self.wfile.write(b'Hello, world!')

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="http port", type=int, default=100)
    parser.add_argument("--width", help="width", type=int, default=100)
    parser.add_argument("--height", help="height", type=int)
    args = parser.parse_args()
    with socketserver.TCPServer(("", args.port), myHandler) as httpd:
        print("serving at port", args.port)
        while isRunning():
            httpd.handle_request()
        print("loop exit")
        httpd.server_close()
    print("exiting...")

main(sys.argv)
