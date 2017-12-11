import argparse
from bottle import request, response, route, run
import bottle
from command import Command
from config import Config
from hardware import Hardware
import json
import logging
from time import time

parser = argparse.ArgumentParser()
c = Config()

parser.add_argument('--node', help='Node id', default='master', choices=c.settings['nodes'].keys())
parser.add_argument('--loglevel', help='Log level for server & playback', default='INFO')
args = parser.parse_args()

logging.getLogger().setLevel(args.loglevel)
hw = Hardware(c, args.node)

script = []


@route('/cmd', method='POST')
def start_show():
    global script
    logging.info("Starting!")
    t = time()

    hw.play_script(script)

    response.content_type = "application/json"
    return json.dumps({'total_runtime': time() - t})


@route('/cmd', method='PUT')
def receive_commands():
    global script
    body = request.json

    script = map(lambda r: Command(r['timeout'], r['changes']), body['commands'])

    response_body = {'commands': len(script), 'total_runtime': sum(cm.timeout for cm in script)}
    logging.info("Loaded commands: {}".format(response_body))

    response.content_type = "application/json"
    return json.dumps(response_body)


bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024
run(host='0.0.0.0', port=c.settings['nodes'][args.node]['port'])

