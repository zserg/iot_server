import requests
import argparse
import json
import sys

#SERVER=http://138.201.104.178:9000/iot_storage/api/v1/devices/
#URL='http://62.109.6.117:9000/iot_storage/api/v1/data/write/20506cbe7260433e/'
API_ROOT='iot_storage/api/v1'
PORT=80

def get_devices(host, port):
    URL = 'http://{}:{}/{}/devices/'.format(host, port, API_ROOT)
    r = requests.get(URL)
    return r.json()

def device_details(host, port, devid):
    URL = 'http://{}:{}/{}/devices/{}/'.format(host, port, API_ROOT, devid)
    r = requests.get(URL)
    return r.json()

def get_datanodes(host, port, devid):
    URL = 'http://{}:{}/{}/devices/{}/datanodes/'.format(host, port, API_ROOT, devid)
    r = requests.get(URL)
    return r.json()

def create_device(host, port, **kwargs):
    URL = 'http://{}:{}/{}/devices/'.format(host, port, API_ROOT)
    r = requests.post(URL, json = kwargs)
    return r.json()

def write_data(host, port, devid,  **kwargs):
    URL = 'http://{}:{}/{}/data/write/{}/'.format(host, port, API_ROOT, devid)
    data = []
    data.append(kwargs)
    r = requests.post(URL, json = data)
    return r.json()

def read_data(host, port, devid,  **kwargs):
    URL = 'http://{}:{}/{}/data/read/{}'.format(host, port, API_ROOT, devid)
    r = requests.get(URL, params = kwargs)
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
                        help='List of devices',
                        action='store_true')

    parser.add_argument('--nodes',
                        help='List of datanodes',
                        action='store_true')

    parser.add_argument('--create-device', '-c',
                        help='Create new device',
                        action='store_true')

    parser.add_argument('--write', '-w',
                        help='Write data',
                        action='store_true')

    parser.add_argument('--read', '-r',
                        help='Read data',
                        action='store_true')

    parser.add_argument('--name',
                        help='Name of the new device')

    parser.add_argument('--datanodes',
                        help='Name of the new device')

    parser.add_argument('--dev-type',
                        help='Type of the new device')

    parser.add_argument('--devid', help='Device ID')
    parser.add_argument('--node-name', help='Datanode name')
    parser.add_argument('--node-path', help='Datanode path')
    parser.add_argument('--value', help='Value to write')


    args = parser.parse_args()

    host = args.host;
    port = args.port
    params = {}

    if args.devices:
        devs = get_devices(host, port)
        print(json.dumps(devs, sort_keys=True, indent=4))

    elif args.create_device:
        if not args.name:
            print('name is required')
            sys.exit(1)

        params['name'] = args.name
        if args.dev_type:
            params['type'] = args.dev_type

        dev = create_device(host, port, **params)
        print(json.dumps(dev, sort_keys=True, indent=4))

    elif args.write:
        if (not args.node_name or
            not args.value or
            not args.devid):
            print('Device id, datanode name and value are required')
            sys.exit(1)

        deviceid = args.devid
        params['name'] = args.node_name
        params['value'] = args.value
        if args.node_path:
            params['path'] = args.node_path

        status = write_data(host, port, deviceid, **params)
        print(json.dumps(status, sort_keys=True, indent=4))

    #list of datanodes
    elif args.nodes:
        if not args.devid:
            print('Device id is required')
            sys.exit(1)

        deviceid = args.devid
        nodes = get_datanodes(host, port, deviceid)
        print(json.dumps(nodes, sort_keys=True, indent=4))

    elif args.read:
        if (not args.datanodes or
            not args.devid):
            print('Device id, datanode name or path are required')
            sys.exit(1)

        deviceid = args.devid
        params['datanodes'] = args.datanodes
        status = read_data(host, port, deviceid, **params)
        print(json.dumps(status, sort_keys=True, indent=4))



