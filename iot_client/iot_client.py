import requests
import argparse
import json

#SERVER=http://138.201.104.178:9000/iot_storage/api/v1/devices/
#URL='http://62.109.6.117:9000/iot_storage/api/v1/data/write/20506cbe7260433e/'
API_ROOT='iot_storage/api/v1'
PORT=80

def get_devices(host, port):
    URL = 'http://{}:{}/{}/devices/'.format(host, port, API_ROOT)
    r = requests.get(URL)
    return r.json()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description='Client for IoT API')
    parser.add_argument('--host',
                        help='IoT server address',
                        required=True)
    parser.add_argument('--port', '-p',
                        help='IoT server port (default - {})'.format(PORT),
                        default=PORT)
    parser.add_argument('--verbose', '-v',
                        help='Verbose mode',
                        action='store_true')

    parser.add_argument('--devices', '-d',
                        help='Verbose mode',
                        action='store_true')

    parser.add_argument('--create-device', '-c',
                        help='Verbose mode',
                        action='store_true')

    args = parser.parse_args()

    host = args.host;
    port = args.port

    if args.devices:
        devs = get_devices(host, port)
        print(json.dumps(devs, sort_keys=True, indent=4))


