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
            board = Board(width, height)
            if 'density' in q:
                board.randomize(float(q['density'][0]))
            self.wfile.write(board.serialize().encode('ascii'))
        else:
            self.wfile.write(b'Commands:\n  /quit\n  /board?width=x&height=y&density=d\n')

class Board:
    """Represents a board in the Conway's Game of Life"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.setElements(lambda r, c : False)

    def setElements(self, f):
        self.rows = []
        for r in range(self.height):
            row = []
            for c in range(self.width):
                row.append(f(r, c))
            self.rows.append(row)

    def randomize(self, density):
        self.setElements(lambda r, c : random.randint(0, 1000) < 1000 * density)

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
        while running:
            httpd.handle_request()
        print("loop exit")
        # httpd.server_close()
    print("exiting...")

main(sys.argv)
