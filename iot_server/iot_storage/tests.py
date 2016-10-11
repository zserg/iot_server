from django.test import TestCase
from iot_storage.models import Device

class DeviceTestCase(TestCase):
    def setUp(self):
        Device.objects.create(name='SmartDevice',
                              Type='Building',
                              description='Some Smart building',
                              device_id='abcdef0123456789',
                              attributes=
