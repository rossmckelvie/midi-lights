import argparse
from command import Command
from config import Config
from hardware import Hardware
import json
from time import time
from twisted.internet import reactor, endpoints
from twisted.logger import Logger
from twisted.web.server import Site
from twisted.web.resource import Resource


class HardwareServer(Resource):
    log = Logger()

    def __init__(self, hardware):
        self.hardware = hardware
        self.script = None
        self.show_instance = None

    def render_POST(self, request):
        t = time()

        self.hardware.play_script(self.script)
        return json.dumps({'total_runtime': time() - t})

    def render_PUT(self, request):
        content = request.content.read()
        body = json.loads(content)

        script = map(lambda r: Command(r['timeout'], r['changes']), body['commands'])
        self.script = script

        response = json.dumps({'commands': len(self.script), 'total_runtime': sum(c.timeout for c in script)})
        self.log.info("Loaded commands: {}".format(response))

        request.setHeader(b"Content-Type", b"application/json")
        return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    hw = Hardware(Config())

    parser.add_argument('--port', help='Server port, default 4444', default=4444, type=int)

    args = parser.parse_args()

    root = Resource()
    root.putChild("cmd", HardwareServer(hw))
    endpoint = endpoints.serverFromString(reactor, "tcp:{}".format(args.port))
    endpoint.listen(Site(root))
    reactor.run()
