import argparse
from command import Command
from config import Config
from hardware import Hardware
import json
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor, endpoints


class HardwareServer(Resource):
    def __init__(self, hardware):
        self.hardware = hardware

    def render_POST(self, request):
        body = json.loads(request.content.read())

        self.hardware.play_script(map(lambda r: Command(r['timeout'], r['changes']), body['commands']))

        request.setHeader(b"Content-Type", b"application/json")
        return json.dumps({'status': 'DONE'})


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
