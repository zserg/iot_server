from django.test import TestCase, Client
from iot_storage.models import Device, Datanode, Datapoint
from django.urls import reverse
import json

class DeviceTestCase(TestCase):
    def setUp(self):
        Device.objects.create(name='SmartDevice',
                              dev_type='Building',
                              description='Some Smart Building',
                              dev_id='abcdef0123456789',
                              attributes=[{'key':'key1'}, {'value':'value1'},
                                          {'key':'key2'}, {'value':'value2'}]
                              )

    def test_device_creation(self):
        dev = Device.objects.get(name='SmartDevice')
        self.assertEqual(dev.dev_type, 'Building')
        self.assertEqual(dev.description, 'Some Smart Building')
        self.assertEqual(dev.dev_id, 'abcdef0123456789')
        self.assertIsNotNone(dev.created_at)
        self.assertEqual(dev.attributes, [{'key':'key1'}, {'value':'value1'},
                                          {'key':'key2'}, {'value':'value2'}])

class APITestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_devices_list(self):
        response = self.client.get(reverse('devices-list'))
        self.assertEqual(response.status_code,200)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                {'fullsize':0,'items':[]})


    def test_write_data_new_datanode(self):
        device = Device.objects.create_device({'name':'test_device'})
        response = self.client.post(reverse('data-write', kwargs={'deviceid':device.dev_id}),
                content_type='application/json',
                data=json.dumps({"name":"Temperature",
                      "path":"Some/Path",
                      "data_type":"int",
                      "value":42,
                      "unit":"c"})
                )
        node = Datanode.objects.filter(name='Temperature')
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(node),1)
        self.assertEqual(node[0].node_path,'Some/Path')
        self.assertEqual(node[0].unit,'c')
        self.assertEqual(node[0].device.name,'test_device')

        point = Datapoint.objects.filter(node__name='Temperature')
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(point),1)
        self.assertEqual(point[0].data_type,'int')
        self.assertEqual(point[0].value_int,42)


class APIDataTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.device = Device.objects.create_device({'name':'test_device'})
        self.client.post(reverse('data-write', kwargs={'deviceid':self.device.dev_id}),
                content_type='application/json',
                data=json.dumps({"name":"Temperature",
                                  "path":"/Some/Path",
                                  "data_type":"int",
                                  "value":42,
                                  "unit":"c"}))
        self.client.post(reverse('data-write', kwargs={'deviceid':self.device.dev_id}),
                content_type='application/json',
                data=json.dumps({"name":"Temperature",
                                  "path":"/Some/Path",
                                  "data_type":"int",
                                  "value":43,
                                  "unit":"c"}))
        self.client.post(reverse('data-write', kwargs={'deviceid':self.device.dev_id}),
                content_type='application/json',
                data=json.dumps({"name":"Temperature",
                                  "path":"/Some/Way",
                                  "data_type":"int",
                                  "value":44,
                                  "unit":"c"}))

    def test_datanodes_list(self):
        response = self.client.get(reverse('datanodes-list', kwargs={'deviceid':self.device.dev_id}))
        self.assertEqual(response.status_code,200)
        data = response.json()
        self.assertEqual(data['fullsize'],2)

    def test_data_read_path(self):
        response = self.client.get('%s?datanodes=/Some/Path' %
                                    reverse('data-read', kwargs={'deviceid':self.device.dev_id}))
        self.assertEqual(response.status_code,200)
        data = response.json()
        self.assertEqual(len(data['datanodeReads']),1)
        self.assertEqual(len(data['datanodeReads'][0]['values']),2)

    def test_data_read_name(self):
        response = self.client.get('%s?datanodes=Temperature' %
                                    reverse('data-read', kwargs={'deviceid':self.device.dev_id}))
        self.assertEqual(response.status_code,200)
        data = response.json()
        data_reads = data['datanodeReads']
        self.assertEqual(len(data_reads),2)
        for i in data_reads:
            if i['path'] == '/Some/Path':
                self.assertEqual(len(i['values']),2)
            elif i['path'] == '/Some/Way':
                self.assertEqual(len(i['values']),1)
            else:
                self.fail('fail')


