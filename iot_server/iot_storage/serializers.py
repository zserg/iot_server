from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from iot_storage.models import Device, Datanode, Datapoint

import time

class DeviceSerializer(serializers.ModelSerializer):
    href = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Device
        fields = ('dev_id', 'name', 'dev_type', 'description',
                  'attributes', 'created_at', 'href')
        extra_kwargs = {'dev_id': {'read_only': 'True'}}

    def create(self, validated_data):
        device = Device.objects.create_device(validated_data)
        return device


class DatanodeSerializer(serializers.ModelSerializer):
    href = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Datanode
        fields = ('name', 'node_path', 'data_type',
                  'unit', 'created_at', 'href')


def get_data_type(value):
    try:
       int(value)
       return 'int'
    except ValueError:
        pass

    try:
       float(value)
       return 'float'
    except ValueError:
        pass

    return 'str'


class DataWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, write_only=True)
    value = serializers.CharField(max_length=255)
    data_type = serializers.CharField(max_length=255, default='' )
    unit = serializers.CharField(max_length=255, default='' )
    timestamp = serializers.IntegerField(default=0)
    path = serializers.CharField(max_length=1023,default='')

    def create(self, validated_data):

        node_path = str.strip(validated_data['path'],'/')
        try:
            node = Datanode.objects.get(device__id=self.context['device'].pk,
                                         node_path=node_path,
                                         name=validated_data['name'])
        except ObjectDoesNotExist:
            if validated_data['data_type']:
                node_data_type = validated_data['data_type']
            else:
                node_data_type = get_data_type(validated_data['value'])

            node = Datanode(name=validated_data['name'], data_type=node_data_type,
                            node_path=node_path, unit=validated_data['unit'] ,
                            device=self.context['device'])
            node.save()

        if validated_data['timestamp'] == 0:
            timestamp_int = int(time.time())
        else:
            timestamp_int = validated_data['timestamp']

        datapoint = Datapoint(value=validated_data['value'],
                             created_at=timestamp_int,
                             node=node)
        datapoint.save()
        ret_data = {'name':validated_data['name'],
                    'path':validated_data['path'],
                    'v':validated_data['value']}
        #return datapoint
        return ret_data

    def to_representation(self, obj):
        return obj

class DatapointReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Datapoint
        fields = ('value', 'created_at')


class DataReadSerializer(serializers.ModelSerializer):
    points = serializers.SerializerMethodField('get_datapoints')

    class Meta:
        model = Datanode
        fields = ('name', 'node_path', 'points')

    def get_datapoints(self,obj):
        dps = Datapoint.objects.filter(node=obj)
        #dps = Datapoint.objects.all()
        serializer = DatapointReadSerializer(dps, many=True)
        return serializer.data




