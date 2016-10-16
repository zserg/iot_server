from django.db import models
from django.contrib.postgres.fields import JSONField
import uuid

class DeviceManager(models.Manager):
    def create_device(self, data):
        device = self.create(name=data['name'],
                    dev_type=data.get('type',''),
                    dev_id=str(uuid.uuid4()).replace('-','')[:16],
                    description=data.get('description',''),
                    attributes=data.get('attributes',''))
        return device

class Device(models.Model):
    name = models.CharField(max_length=255)
    dev_id = models.CharField(max_length=16)
    dev_type = models.CharField(max_length=255)
    description = models.TextField()
    attributes = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DeviceManager()


class DatanodeManager(models.Manager):
    def create_datanode(self, data):
        datanode = self.create(name=data['name'],
                    data_type=data.get('data_type',''),
                    node_path=data.get('path',''),
                    unit=data.get('unit',''),
                    device=data['device'])
        return datanode

class Datanode(models.Model):
    name = models.CharField(max_length=255)
    node_path = models.TextField()
    data_type = models.CharField(max_length=8)
    unit = models.CharField(max_length=255)
    device = models.ForeignKey(Device)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DatanodeManager()


class DatapointManager(models.Manager):
    def create_datapoint(self, data):
        p_data = data;
        p_data['v_int'] = 0
        p_data['v_str'] = ''
        p_data['v_float'] = 0.0
        p_data['v_bool'] = False

        #data_type = data.get('data_type','')
        data_type = 'int'
        if data_type == 'int':
            p_data['v_int'] = int(data['value'])
        if data_type == 'float':
            p_data['v_float'] = float(data['value'])

        datapoint = self.create(
                    data_type= data_type,
                    value_str=p_data['v_str'],
                    value_int=p_data['v_int'],
                    value_float=p_data['v_float'],
                    value_bool=p_data['v_bool'],
                    node=data['node'],
                    device=data['device'])
        return datapoint

class Datapoint(models.Model):
    data_type = models.CharField(max_length=8)
    value_str = models.CharField(max_length=255)
    value_int = models.IntegerField()
    value_float = models.FloatField()
    value_bool = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    node = models.ForeignKey(Datanode)
    device = models.ForeignKey(Device)

    objects = DatapointManager()

