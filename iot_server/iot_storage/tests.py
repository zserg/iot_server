from django.test import TestCase
from iot_storage.models import Device

class DeviceTestCase(TestCase):
    def setUp(self):
        Device.objects.create(name='SmartDevice',
                              Type='Building',
                              description='Some Smart building',
                              device_id='abcdef0123456789',
                              attributes=[{'key':'key1'}, {'value':'value1'},
                                          {'key':'key2'}, {'value':'value2'}]
                              )

    def test_device_creation(self):
        dev = Device.objects.get(name='SmartDevice')
        self.assertEqual(dev.Type, 'Building')
        self.assertEqual(dev.description, 'Some Smart Building')
        self.assertEqual(dev.device_id, 'abcdef0123456789')
        self.assertEqual(dev.attributes, 'value1')

