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

class Board:
    """Represents a board in the Conway's Game of Life"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.setElements(lambda r, c : False)

    def setElements(self, f):
        new_rows = []
        for r in range(self.height):
            row = []
            for c in range(self.width):
                row.append(f(r, c))
            new_rows.append(row)
        self.rows = new_rows

    def randomize(self, density):
        self.setElements(lambda r, c : random.randint(0, 1000) < 1000 * density)

    def serialize(self):
        out = ""
        for r in range(self.height):
            # Densities in life are usually low, just print deltas of True
            row = self.rows[r]
            prev_true = -1
            true_deltas = []
            for c in range(self.width):
                if row[c]:
                    true_deltas.append(c - prev_true)
                    prev_true = c
            out = out + ("%s" % true_deltas) + "\n"
        return out

    def alive(self, r, c):
        # For now we will not make the world toroidal. This will make
        # it easier to reason about sharding the world.
        if r == self.height:
            return False
        if c == self.width:
            return False
        return self.rows[r][c]

    def nextState(self, r, c):
        alive = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (j != 0 and i != 0) and self.alive(r + i, c + j):
                    alive += 1
        # Return next state according to the game rules:
        #   exactly 3 neighbors: on,
        #   exactly 2 neighbors: maintain current state,
        #   otherwise: off.
        return alive == 3 or (alive == 2 and self.alive(r, c))

    def step(self):
        self.setElements(lambda r, c : self.nextState(r, c))

board = Board(1, 1)

class myHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global board
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
        elif self.path.startswith("/step"):
            board.step()
            self.wfile.write(board.serialize().encode('ascii'))
        else:
            self.wfile.write(b'Commands:\n  /quit\n  /board?width=x&height=y&density=d\n')

def main(argv):
    random.seed(32)
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="http port", type=int, default=100)
    parser.add_argument("--width", help="width", type=int, default=100)
    parser.add_argument("--height", help="height", type=int)
    # parser.add_argument("--shards", help="shards", type=int, default=1)
    args = parser.parse_args()
    with socketserver.TCPServer(("", args.port), myHandler) as httpd:
        print("serving at port", args.port)
        while running:
            httpd.handle_request()
        print("loop exit")
        # httpd.server_close()
    print("exiting...")

main(sys.argv)
