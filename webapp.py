from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from exlink import TVRemote

app = Flask(__name__)
api = Api(app)
tvremote = TVRemote(device='/dev/ttyUSB0')

action_parser = reqparse.RequestParser()
action_parser.add_argument('action', str)

volume_parser = reqparse.RequestParser()
volume_parser.add_argument('level', int)


class TVVolume(Resource):
    VOLUME_ACTIONS = ['up', 'down', 'mute', 'normal']

    def _isvalid_volume_action(self, action):
        return action in TVVolume.VOLUME_ACTIONS

    def put(self):
        args = volume_parser.parse_args()
        level = int(args['level'])
        if level < 0 or level > 255:
            raise ValueError('"level" has to be between 0 and 255')

        tvremote.cmd_volume_set(int(args['level']))

        return {'level': level}, 200

    def post(self):
        args = action_parser.parse_args()
        action = args['action']
        if not self._isvalid_volume_action(action):
            raise ValueError('"action" param should be up/down/mute, not "{}"'.format(action))

        if action == 'up':
            tvremote.cmd_volume_up()
        elif action == 'down':
            tvremote.cmd_volume_down()
        elif action == 'normal':
            tvremote.cmd_volume_set(12)
        else:
            tvremote.cmd_volume_set(0)

        return {}, 204


class TVScreen(Resource):
    def _isvalid_action(self, action):
        return action == 'off'

    def post(self):
        args = action_parser.parse_args()
        action = args['action']
        if not self._isvalid_action(action):
            raise ValueError('"action" should be "off"')

        tvremote.cmd_power_off()

        return {}, 204



api.add_resource(TVVolume, '/tv/volume')
api.add_resource(TVScreen, '/tv/screen')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
