#!/usr/local/bin/python3

import argparse
import csv
import http.client
import http.server
import math
import random
import socketserver
import sys
import urllib.parse

shards = None

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
        out = "["
        prefix = "\n  "
        for r in range(self.height):
            # Densities in life are usually low, just print deltas of True
            row = self.rows[r]
            live_columns = []
            for c in range(self.width):
                if row[c]:
                    live_columns.append(c);
            out = out + prefix + ("%s" % live_columns)
            prefix = ",\n  "
        return out + "\n]\n"

    def alive(self, r, c):
        # Toroidol world transform
        r = (r + self.height) % self.height
        c = (c + self.width) % self.width
        return self.rows[r][c]

    def nextState(self, r, c):
        alive = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (j != 0 or i != 0) and self.alive(r + i, c + j):
                    alive += 1
        # Return next state according to the game rules:
        #   exactly 3 neighbors: on,
        #   exactly 2 neighbors: maintain current state,
        #   otherwise: off.
        return alive == 3 or (alive == 2 and self.alive(r, c))

    def step(self):
        self.setElements(lambda r, c : self.nextState(r, c))

board = Board(1, 1)
def setBoard(new_board):
    global board
    board = new_board

class Shard(Board):
    def __init__(self, server, row, col, width, height):
        Board.__init__(self, width, height)
        self.server = server
        self.http_client = http.client.HTTPConnection(self.server)
        self.row = row
        self.col = col

    def randomized(width, height):
        this.http_client.request("GET", "/board?width=%d&height=%d", width, height)
        response = this.http_client.getresponse()
        if response.status != 200:
            raise RuntimeError('unexpected response from %s: %d', this.server, response.status)
        return json.loads(response.read())

    def step(north_row, east_col, south_row, west_col):
        this.http_client.request("GET", "/board?width=%d&height=%d", width, height)
        response = this.http_client.getresponse()
        if response.status != 200:
            raise RuntimeError('unexpected response from %s: %d', this.server, response.status)
        return json.loads(response.read())

class ShardedBoard(Board):
    def __init__(self, server, width, height, shards):
        Board.__init__(self, width, height)
        self.shard_rows = []
        num_shards = len(args.shards)

        # Figure out the width/height of each shard based on the overall board dimensions
        # and the number of shards. For now, we require that the number of shards is
        # a square, and the width/height of each shard is the same. This can be relaxed
        # later.
        sqrt = math.sqrt(num_shards)
        if math.floor(sqrt) != sqrt:
            raise RuntimeError('Expected number of shards to be perfect square: %d' % num_shards)

        shard_width = args.width / sqrt
        if math.floor(shard_width) != shard_width:
            raise RuntimeError('Shard width is not integral: %f' % shard_width)
        shard_width = int(shard_width)
        shard_height = args.height / sqrt
        if math.floor(shard_height) != shard_height:
            raise RuntimeError('Shard height is not integral: %f' % shard_height)
        shard_height = int(shard_height)

        c = 0
        r = 0
        shard_row = []
        for shard_server in args.shards:
            shard_row.append(Shard(shard_server, c, r, shard_width, shard_height))
            c += shard_width
            r += shard_height
            if c == args.width:
                c = 0
                r += 1
                self.shard_rows.append(shard_row)
                shard_row = []

        # Sanity check; there should be no uneven shard rows after this.
        if len(shard_row) != 0:
            raise RuntimeError('Leftover shard row: %s' % row)

class myHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global board
        print("path=%s" % self.path)
        content_type = 'text/plain'
        out = '???'
        response = 200
        if self.path == '/quit':
            print("quitting")
            out = 'quitting\n'
            quit()
        elif self.path.startswith("/board"):
            url = urllib.parse.urlparse(self.path)
            q = urllib.parse.parse_qs(url.query)
            width = int(q['width'][0]) if 'width' in q else 100
            height = int(q['height'][0]) if 'height' in q else width

            if shards == None:
                setBoard(Board(width, height))
            else:
                setBoard(ShardedBoard(width, height, arg.shards))
            if 'density' in q:
                board.randomize(float(q['density'][0]))
            out = board.serialize()
        elif self.path.startswith("/step"):
            board.step()
            out = board.serialize()
        elif self.path == "/" or self.path == "/help":
            out = 'Commands:\n  /quit\n  /board?width=x&height=y&density=d\n'
        else:
            filename = self.path[1:]
            try:
                with open(filename) as f:
                    out = f.read()
                    if self.path.endswith(".js"):
                        content_type = 'application/javascript'
                    elif self.path.endswith('.html'):
                        content_type = 'text/html'
                    elif self.path.endswith('.css'):
                        content_type = 'text/css'
            except IOError:
                content_type = 'text/plain'
                out = 'Could not read file %s' % filename
                response = 404
        self.send_response(response)
        self.send_header('Cache-Control', 'max-age=0')
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(out.encode('ascii'))

def main(argv):
    random.seed(32)
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="http port", type=int, default=100)
    parser.add_argument("--width", help="width", type=int, default=100)
    parser.add_argument("--height", help="height", type=int)
    parser.add_argument("--shards", help="shards", nargs='+')
    args = parser.parse_args()
    global shards
    shards = args.shards
    socketserver.TCPServer.allow_reuse_address=True

    with http.server.ThreadingHTTPServer(("", args.port), myHandler) as httpd:
        print("serving at port", args.port)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        print("loop exit")
        httpd.server_close()
    print("exiting...")

main(sys.argv)
