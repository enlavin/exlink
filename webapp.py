from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from exlink import TVRemote

app = Flask(__name__)
api = Api(app)
tvremote = TVRemote(device='/dev/ttyUSB0')

volumedir_parser = reqparse.RequestParser()
volumedir_parser.add_argument('dir', str)

volume_parser = reqparse.RequestParser()
volume_parser.add_argument('level', int)



class TVVolume(Resource):
    def put(self):
        args = volume_parser.parse_args()
        level = int(args['level'])
        if level < 0 or level > 255:
            raise ValueError('"level" has to be between 0 and 255')

        tvremote.cmd_volume_set(int(args['level']))

    def post(self):
        args = volumedir_parser.parse_args()
        if args['dir'] not in ['up', 'down', 'mute']:
            raise ValueError('"dir" param should be up/down/mute, not "{}"'.format(args['dir']))

        if args['dir'] == 'up':
            tvremote.cmd_volume_up()
        elif args['dir'] == 'down':
            tvremote.cmd_volume_down()
        else:
            tvremote.cmd_volume_mute()



api.add_resource(TVVolume, '/tv/volume')

if __name__ == '__main__':
    app.run(debug=True)
