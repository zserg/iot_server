#!/usr/bin/env python
import requests
import argparse
import json
import sys
import configparser
import re
import time

CONFIG_FILE = '.iot_client.cfg'


def parse_args(config_only=False):
    """
    Function to parsing of command line arguments
    Usage:
    list                                 : list of devices
    list <dev>                           : list of datanodes of <dev>
    show <dev>                           : show device details
    create <name> [OPTIONS]              : create device
    write <dev> <name> <value> [OPTIONS] : write data
    read <dev> <nodes> [OPTIONS]         : read data
    get-token <user> <password>          : get auth token
    help [command]                       : print help
    """
    error = False

    config_opts = [
            {'name': 'url', 'help': 'IoT server address (http://example.com:8000/api/)'},  # noqa: E502
            {'name': 'token', 'help': 'Authorizarion token'},
            {'name': 'user', 'help': 'User name'},
            {'name': 'password', 'help': 'Passowrd'}]

    commands = ['list', 'create', 'show', 'write', 'read', 'help', 'get-token']

    parser = argparse.ArgumentParser(description='Client for IoT API')
    parser.add_argument('command', help='Command to execute',
                        choices=commands)
    parser.add_argument('command_args', help='Command arguments', nargs='*')
    parser.add_argument('--config', default=CONFIG_FILE,
                        help='Config file name, default: .iot_client.cfg')

    for opt in config_opts:
        parser.add_argument('--{}'.format(opt['name']), help=opt['help'])

    parser.add_argument('--descr', help='New device description')
    parser.add_argument('--dev-type', help='New device type')
    parser.add_argument('--unit', help='Data value units')
    parser.add_argument('--path', help='Node path')

    if not config_only:
        args = parser.parse_args()
        args = vars(args)
    else:
        args = {'config':CONFIG_FILE}
    config = configparser.RawConfigParser()
    config.read(args['config'])

    # check if command line argument exists,
    # else select from config file
    opts = {}
    for opt in config_opts:
        name = opt['name']
        value = args.get(name)
        if value:  # pick up value from command line
            opts[name] = value
        else:
            try:
                value = config.get('config', name)
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                value = None

            opts[name] = value  # pick up value from config file

    if not opts['url']:
        print('Error: url option is absent'.format(name))
        error = True

    if not opts['token']:
        print('Error: auth token is absent'.format(name))
        error = True

    return error, args, opts


class Processor(object):
    """
    Class to process requests to IoT Server API
    """
    def __init__(self, args, opts):
        self.cmd = args.get('command')
        self.cmd_args = args.get('command_args')
        self.base_url = opts['url']
        self.headers = {'Authorization': 'Token {}'.format(opts['token'])}
        self.descr = args.get('descr')
        self.dev_type = args.get('dev_type')
        self.unit = args.get('unit')
        self.path = args.get('path')
        self.fromdate = self.fromdate_parse(args.get('fromdate'))

    def fromdate_parse(self, raw_date):
        # -NNs : NN seconds from now
        if raw_date:
            m = re.match(r'-(\d)s', raw_date)
            if m:
               return int(time.time())-int(m.group(1))


    def cmd_process(self):
        if self.cmd == 'list' and len(self.cmd_args) == 0:
            return self.list_devices()

        if self.cmd == 'show':
            if len(self.cmd_args) == 1:
                dev_id = self.cmd_args[0]
                return self.device_details(dev_id)
            else:
                return {"error":
                        "the show command requires <devid> argument"}

        if self.cmd == 'list' and len(self.cmd_args) == 1:
            dev_id = self.cmd_args[0]
            return self.list_datnodes(dev_id)

        if self.cmd == 'create':
            if len(self.cmd_args) == 1:
                data = {}
                data['name'] = self.cmd_args[0]
                if self.descr:
                    data['description'] = self.descr
                if self.dev_type:
                    data['dev_type'] = self.dev_type
                return self.create_device(data)
            else:
                return {"error":
                        "the create command requires <name> argument"}

        if self.cmd == 'write':
            if len(self.cmd_args) == 3:
                data = {}
                dev_id = self.cmd_args[0]
                data['name'] = self.cmd_args[1]
                data['value'] = self.cmd_args[2]
                if self.unit:
                    data['unit'] = self.unit
                if self.path:
                    data['path'] = self.path
                return self.write_data(dev_id, data)
            else:
                return {"error":
                        "the create command requires <devid>, <name> and <value> arguments"}  # noqa: E501

        if self.cmd == 'read':
            if len(self.cmd_args) == 2:
                data = {}
                dev_id = self.cmd_args[0]
                data['datanodes'] = self.cmd_args[1]
                return self.read_data(dev_id, data)
            else:
                return {"error":
                        "the read command requires <devid> and <nodes> arguments"}  # noqa: E501

        if self.cmd == 'get-token':
            if len(self.cmd_args) == 2:
                data = {}
                data['username'] = self.cmd_args[0]
                data['password'] = self.cmd_args[1]
                return self.get_token(data)
            else:
                return {"error":
                        "the get-token command requires <username> and <password> arguments"}  # noqa: E501

    def list_devices(self):
        """
        Request list of devices
        """
        url = '{}/devices/'.format(self.base_url)
        r = requests.get(url, headers=self.headers)
        resp = {'status':r.status_code}
        if r.text:
            resp['data'] = r.json()
        else:
            resp['data'] = ''
        return resp

    def device_details(self, dev_id):
        """
        Request device details
        """
        url = '{}/devices/{}'.format(self.base_url, dev_id)
        r = requests.get(url, headers=self.headers)
        resp = {'status':r.status_code}
        if r.text:
            resp['data'] = r.json()
        else:
            resp['data'] = ''
        return resp

    def list_datnodes(self, dev_id):
        """
        Request list of datanodes
        """
        url = '{}/devices/{}/datanodes/'.format(self.base_url, dev_id)
        r = requests.get(url, headers=self.headers)
        resp = {'status':r.status_code}
        if r.text:
            resp['data'] = r.json()
        else:
            resp['data'] = ''
        return resp

    def create_device(self, data):
        """
        Request to create new device
        """
        url = '{}/devices/'.format(self.base_url)
        r = requests.post(url, json=data, headers=self.headers)
        resp = {'status':r.status_code}
        if r.text:
            resp['data'] = r.json()
        else:
            resp['data'] = ''
        return resp

    def write_data(self, dev_id, data):
        """
        Request to write data
        """
        url = '{}/data/write/{}/'.format(self.base_url, dev_id)
        r_data = []
        r_data.append(data)
        r = requests.post(url, json=r_data, headers=self.headers)
        resp = {'status':r.status_code}
        if r.text:
            resp['data'] = r.json()
        else:
            resp['data'] = ''
        return resp

    def read_data(self, dev_id, params):
        """
        Request to read data
        """
        data = ''
        for key in params.keys():
            data += '{}={}&'.format(key, params[key])
        data = data.rstrip('&')
        url = '{}/data/read/{}?{}'.format(self.base_url, dev_id, data)
        r = requests.get(url, headers=self.headers)
        resp = {'status':r.status_code}
        if r.text:
            resp['data'] = r.json()
        else:
            resp['data'] = ''
        return resp

    def get_token(self, data):
        """
        Request auth token
        """
        url = '{}/api-token-auth/'.format(self.base_url)
        r = requests.post(url, json=data)
        resp = {'status':r.status_code}
        if r.text:
            resp['data'] = r.json()
        else:
            resp['data'] = ''
        return resp

if __name__ == '__main__':

    (error, args, opts) = parse_args()

    if error:
        sys.exit(1)

    processor = Processor(args, opts)
    status = processor.cmd_process()
    print(json.dumps(status, sort_keys=True, indent=4))
