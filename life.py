#!/usr/local/bin/python3

import argparse
import csv
import http.server
import random
import socketserver
import sys
import urllib.parse

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
            self.wfile.write(b'quitting!\n')
            quit()
        elif self.path.startswith("/board"):
            url = urllib.parse.urlparse(self.path)
            q = urllib.parse.parse_qs(url.query)
            width = int(q['width'][0]) if 'width' in q else 100
            height = int(q['height'][0]) if 'height' in q else width
            density = float(q['density'][0]) if 'density' in q else 0.1
            print("width=%d height=%d density=%f" % (width, height, density))
            board = Board(width, height, density)
            self.wfile.write(board.serialize().encode('ascii'))
        else:
            self.wfile.write(b'Commands:\n  /quit\n  /board?width=x&height=y&density=d\n')

class Board:
    """Represents a board in the Conway's Game of Life"""

    def __init__(self, width, height, density):
        self.width = width
        self.height = height
        self.rows = []
        for r in range(height):
            row = []
            for c in range(width):
                row.append(random.randint(0, 1000) < 1000 * density)
            self.rows.append(row)

    def serialize(self):
        out = ""
        for h in range(self.height):
            # Densities in life are usually low, just print deltas of True
            row = self.rows[h]
            prev_true = -1
            true_deltas = []
            for c in range(self.width):
                if row[c]:
                    true_deltas.append(c - prev_true)
                    prev_true = c
            out = out + ("%s" % true_deltas) + "\n"
        return out

def main(argv):
    random.seed(32)
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
        # httpd.server_close()
    print("exiting...")

main(sys.argv)
