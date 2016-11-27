from django.test import TestCase, Client
from iot_storage.models import Device, Datanode, Datapoint
from django.urls import reverse
from django.contrib.auth.models import User

import json
from rest_framework.test import APIClient

class DeviceTestCase(TestCase):
    def setUp(self):
        Device.objects.create(name='SmartDevice',
                              dev_type='Building',
                              description='Some Smart Building',
                              dev_id='abcdef0123456789',
                              attributes=[{'key': 'key1'}, {'value': 'value1'},
                                          {'key': 'key2'}, {'value': 'value2'}]
                              )

    def test_device_creation(self):
        dev = Device.objects.get(name='SmartDevice')
        self.assertEqual(dev.dev_type, 'Building')
        self.assertEqual(dev.description, 'Some Smart Building')
        self.assertEqual(dev.dev_id, 'abcdef0123456789')
        self.assertIsNotNone(dev.created_at)
        self.assertEqual(dev.attributes, [{'key': 'key1'}, {'value': 'value1'},
                                          {'key': 'key2'}, {'value': 'value2'}])

class APITestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='test')
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_devices_list_empty(self):
        response = self.client.get(reverse('device-list'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                {'fullsize': 0, 'items': []})

    def test_devices_list(self):
        device = Device.objects.create_device({'name': 'dev1'})
        device = Device.objects.create_device({'name': 'dev2'})
        response = self.client.get(reverse('device-list'), HTTP_HOST='localhost')

        #  import ipdb; ipdb.set_trace()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['fullsize'], 2)
        self.assertEqual(len(data['items']), 2)


    def test_write_data_new_datanode_int(self):
        device = Device.objects.create_device({'name': 'test_device'})
        response = self.client.post(reverse('data-write', kwargs={'deviceid': device.dev_id}),
                content_type='application/json',
                data=json.dumps([{"name": "Temperature",
                      "path": "Some/Path",
                      "data_type": "int",
                      "value": 42,
                      "unit": "c"}])
                )
        node = Datanode.objects.filter(name='Temperature')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(node), 1)
        self.assertEqual(node[0].node_path, 'Some/Path')
        self.assertEqual(node[0].unit, 'c')
        self.assertEqual(node[0].device.name, 'test_device')

        point = Datapoint.objects.filter(node__name='Temperature')
        self.assertEqual(len(point), 1)
        self.assertEqual(point[0].value, '42')

    def test_write_data_new_datanode_str(self):
        device = Device.objects.create_device({'name': 'test_device'})
        response = self.client.post(reverse('data-write', kwargs={'deviceid': device.dev_id}),
                content_type='application/json',
                data=json.dumps([{"name": "Temperature",
                      "path": "Some/Path",
                      "data_type": "str",
                      "value": "42",
                      "unit": "c"}])
                )
        node = Datanode.objects.filter(name='Temperature')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(node), 1)
        self.assertEqual(node[0].node_path, 'Some/Path')
        self.assertEqual(node[0].unit, 'c')
        self.assertEqual(node[0].device.name, 'test_device')

        point = Datapoint.objects.filter(node__name='Temperature')
        self.assertEqual(len(point), 1)
        self.assertEqual(point[0].value, "42")


    def test_write_data_new_datanode_empty_type_int(self):
        device = Device.objects.create_device({'name': 'test_device'})
        response = self.client.post(reverse('data-write', kwargs={'deviceid': device.dev_id}),
                content_type='application/json',
                data=json.dumps([{"name": "Temperature",
                      "path": "Some/Path",
                      "value": "42",
                      "unit": "c"}])
                )
        node = Datanode.objects.filter(name='Temperature')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(node), 1)
        self.assertEqual(node[0].node_path, 'Some/Path')
        self.assertEqual(node[0].unit, 'c')
        self.assertEqual(node[0].data_type, 'int')
        self.assertEqual(node[0].device.name, 'test_device')

        point = Datapoint.objects.filter(node__name='Temperature')
        self.assertEqual(len(point), 1)
        self.assertEqual(point[0].value, "42")

    def test_write_data_new_datanode_empty_type_float(self):
        device = Device.objects.create_device({'name': 'test_device'})
        response = self.client.post(reverse('data-write', kwargs={'deviceid': device.dev_id}),
                content_type='application/json',
                data=json.dumps([{"name": "Temperature",
                      "path": "Some/Path",
                      "value": "42.0",
                      "unit": "c"}])
                )
        self.assertEqual(response.status_code, 201)

        node = Datanode.objects.filter(name='Temperature')
        self.assertEqual(len(node), 1)
        self.assertEqual(node[0].node_path, 'Some/Path')
        self.assertEqual(node[0].unit, 'c')
        self.assertEqual(node[0].data_type, 'float')
        self.assertEqual(node[0].device.name, 'test_device')

        point = Datapoint.objects.filter(node__name='Temperature')
        self.assertEqual(len(point), 1)
        self.assertEqual(point[0].value, "42.0")

    def test_write_data_error_type(self):
        device = Device.objects.create_device({'name': 'test_device'})
        response = self.client.post(reverse('data-write', kwargs={'deviceid': device.dev_id}),
                content_type='application/json',
                data=json.dumps([{"name": "Temperature",
                      "path": "Some/Path",
                      "value": "42.0",
                      "unit": "c"}])
                )

        response = self.client.post(reverse('data-write', kwargs={'deviceid': device.dev_id}),
                content_type='application/json',
                data=json.dumps([
                    {"name": "Temperature",
                      "path": "Some/Path",
                      "value": "42.1",
                      "data_type": "int"},
                    {"name": "Temperature",
                      "path": "Some/Path",
                      "value": "wrong",
                      "data_type": "str"}
                    ])
                )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['detail'],
                        "Write data type doesn't match the datanode data type")

    def test_write_data_timestamp_error(self):
        device = Device.objects.create_device({'name': 'test_device'})
        response = self.client.post(reverse('data-write', kwargs={'deviceid': device.dev_id}),
                content_type='application/json',
                data=json.dumps([{"name": "Temperature",
                      "path": "Some/Path",
                      "value": "42.0",
                      "timestamp": 'sometimes'}])
                )

        self.assertEqual(response.status_code, 400)


class APIDataTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='test')
        self.client = APIClient()
        self.client.force_authenticate(user=user)

        self.device = Device.objects.create_device({'name': 'test_device'})
        self.client.post(reverse('data-write', kwargs={'deviceid': self.device.dev_id}),
                content_type='application/json',
                data=json.dumps([{"name": "Temperature",
                                  "path": "/Some/Path",
                                  "data_type": "int",
                                  "timestamp": 1,
                                  "value": 41,
                                  "unit": "c"}]))
        self.client.post(reverse('data-write', kwargs={'deviceid': self.device.dev_id}),
                content_type='application/json',
                data=json.dumps([{"name": "Temperature",
                                  "path": "/Some/Path",
                                  "data_type": "int",
                                  "timestamp": 2,
                                  "value": 42,
                                  "unit": "c"}]))
        self.client.post(reverse('data-write', kwargs={'deviceid': self.device.dev_id}),
                content_type='application/json',
                data=json.dumps([{"name": "Temperature",
                                  "path": "/Some/Path",
                                  "data_type": "int",
                                  "timestamp": 3,
                                  "value": 43,
                                  "unit": "c"}]))
        self.client.post(reverse('data-write', kwargs={'deviceid': self.device.dev_id}),
                content_type='application/json',
                data=json.dumps([{"name": "Temperature",
                                  "path": "/Some/Path",
                                  "data_type": "int",
                                  "timestamp": 4,
                                  "value": 44,
                                  "unit": "c"}]))
        self.client.post(reverse('data-write', kwargs={'deviceid': self.device.dev_id}),
                content_type='application/json',
                data=json.dumps([{"name": "Temperature",
                                  "path": "/Some/Path",
                                  "data_type": "int",
                                  "timestamp": 5,
                                  "value": 45,
                                  "unit": "c"}]))
        self.client.post(reverse('data-write', kwargs={'deviceid': self.device.dev_id}),
                content_type='application/json',
                data=json.dumps([{"name": "Temperature",
                                  "path": "/Some/Way",
                                  "data_type": "int",
                                  "timestamp": 3,
                                  "value": 44,
                                  "unit": "c"}]))

    def test_datanodes_list(self):
        response = self.client.get(reverse('datanodes-list', kwargs={'deviceid': self.device.dev_id}),
                                   HTTP_HOST='localhost')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['fullsize'], 2)

    def test_data_read_path(self):
        response = self.client.get('%s?datanodes=/Some/Path/Temperature' %
                                    reverse('data-read', kwargs={'deviceid': self.device.dev_id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(len(data[0]['points']), 1)


    def test_data_read_name(self):
        # import ipdb; ipdb.set_trace()
        response = self.client.get('%s?datanodes=Temperature' %
                                    reverse('data-read', kwargs={'deviceid': self.device.dev_id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(len(data[0]['points']), 1)
        self.assertEqual(len(data[1]['points']), 1)

    def test_data_read_timestamp_range(self):
        # import ipdb; ipdb.set_trace()
        response = self.client.get(reverse('data-read', kwargs={'deviceid': self.device.dev_id}),
                {'datanodes': 'Some/Path/Temperature', 'fromdate': 2, 'todate': 4})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(len(data[0]['points']), 3)
        self.assertEqual(data[0]['points'][0]['value'], '42')
        self.assertEqual(data[0]['points'][1]['value'], '43')
        self.assertEqual(data[0]['points'][2]['value'], '44')

    def test_data_read_timestamp_from(self):
        # import ipdb; ipdb.set_trace()
        response = self.client.get(reverse('data-read', kwargs={'deviceid': self.device.dev_id}),
                {'datanodes': 'Some/Path/Temperature', 'fromdate': 1, 'limit': 10})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(len(data[0]['points']), 5)
        self.assertEqual(data[0]['points'][0]['value'], '41')

    def test_data_read_timestamp_from_desc(self):
        # import ipdb; ipdb.set_trace()
        response = self.client.get(reverse('data-read', kwargs={'deviceid': self.device.dev_id}),
                {'datanodes': 'Some/Path/Temperature', 'fromdate': 1, 'limit': 10,
                 'order': 'desc'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(len(data[0]['points']), 5)
        self.assertEqual(data[0]['points'][0]['value'], '45')

