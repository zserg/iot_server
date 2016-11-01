from django.db import models
from django.contrib.postgres.fields import JSONField
import uuid

class DeviceManager(models.Manager):
    def create_device(self, data):
        device = self.create(name=data['name'],
                    dev_id=self.get_dev_id())
        return device

    def get_dev_id(self):
        return str(uuid.uuid4()).replace('-','')[:16]

class Device(models.Model):
    name = models.CharField(max_length=255)
    dev_id = models.CharField(max_length=16)
    dev_type = models.CharField(max_length=255, default='')
    description = models.TextField(default='')
    attributes = JSONField(default=dict())
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DeviceManager()
    def __str__(self):
        return 'Device - {}: name - {}'.format(self.dev_id, self.name)


# class DatanodeManager(models.Manager):
#     def create_datanode(self, data):
#         datanode = self.create(name=data['name'],
#                     data_type=data.get('data_type',''),
#                     node_path=data.get('path',''),
#                     unit=data.get('unit',''),
#                     device=data['device'])
#         return datanode

class Datanode(models.Model):
    name = models.CharField(max_length=255)
    node_path = models.TextField(default='')
    data_type = models.CharField(max_length=8, default='str')
    unit = models.CharField(max_length=255, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)

    def __str__(self):
        return 'Device - {}: node - {} [{}]'.format(self.device.dev_id,self.name, self.node_path)

    # objects = DatanodeManager()


# class DatapointManager(models.Manager):
#     def create_datapoint(self, data):
#         p_data = data;

#         #data_type = data.get('data_type','')
#         if
#         data_type = 'int'
#         if data_type == 'int':
#             p_data['v_int'] = int(data['value'])
#         if data_type == 'float':
#             p_data['v_float'] = float(data['value'])

#         datapoint = self.create(
#                     data_type= data_type,
#                     value_str=p_data['v_str'],
#                     value_int=p_data['v_int'],
#                     value_float=p_data['v_float'],
#                     value_bool=p_data['v_bool'],
#                     node=data['node'],
#                     device=data['device'])
#         return datapoint

class Datapoint(models.Model):
    data_type = models.CharField(max_length=8, default='str' )
    value = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    node = models.ForeignKey(Datanode, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)

    # objects = DatapointManager()

