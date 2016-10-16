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

    # def test_devices_create(self):
    #     response = self.client.post(reverse('devices-list'))
    #     self.assertEqual(response.status_code,200)
    #     self.assertJSONEqual(str(response.content, encoding='utf8'),
    #             {'fullsize':0,'items':[]})

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



