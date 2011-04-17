#!/usr/bin/env python
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
import exlink

server = SimpleJSONRPCServer(('0.0.0.0', 9000))
tv = exlink.TVRemote("/dev/ttyS0")
commands = [fname for fname in dir(tv) if fname.startswith("cmd_")]
for command in commands:
    server.register_function(getattr(tv,command), command[4:])

server.serve_forever()

