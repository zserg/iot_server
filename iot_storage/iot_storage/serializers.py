from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers, status
from iot_storage.models import Device, Datanode, Datapoint
from rest_framework.exceptions import APIException


import time


class DeviceSerializer(serializers.ModelSerializer):
    href = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = ('dev_id', 'name', 'dev_type', 'description',
                  'attributes', 'created_at', 'href')
        extra_kwargs = {'dev_id': {'read_only': 'True'}}

    def create(self, validated_data):
        device = Device.objects.create_device(validated_data)
        return device

    def get_href(self, obj):
        return '{}://{}{}'.format(self.context['request'].scheme,
                                  self.context['request'].META['HTTP_HOST'],
                                  obj.get_absolute_url())


class DatanodeSerializer(serializers.ModelSerializer):
    href = serializers.SerializerMethodField()

    class Meta:
        model = Datanode
        fields = ('name', 'node_path', 'data_type',
                  'unit', 'created_at', 'href')

    def get_href(self, obj):
        return '{}://{}{}'.format(self.context['request'].scheme,
                                  self.context['request'].META['HTTP_HOST'],
                                  obj.get_absolute_url())


class DataWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, write_only=True)
    value = serializers.CharField(max_length=255)
    data_type = serializers.CharField(max_length=255, default='')
    unit = serializers.CharField(max_length=255, default='')
    timestamp = serializers.IntegerField(default=0)
    path = serializers.CharField(max_length=1023, default='')

    def get_node(self, device, path, name):
        try:
            node = Datanode.objects.get(device__id=device,
                                        node_path=path,
                                        name=name)
        except ObjectDoesNotExist:
            node = None

        return node

    def get_data_type(self, value):
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

    def validate(self, attrs):
        device = self.context['device'].pk
        node_name = attrs['name']
        node_path = str.strip(attrs['path'], '/')
        value = attrs['value']
        node = self.get_node(device, node_path, node_name)
        if node:
            if self.get_data_type(value) != node.data_type:
                raise DataWriteError("Write data type doesn't match the datanode data type")  # noqa
            attrs['data_type'] = node.data_type
        else:
            attrs['data_type'] = self.get_data_type(value)

        if attrs['timestamp'] == 0:
            attrs['timestamp'] = int(time.time())
        elif attrs['timestamp'] < 0:
            raise DataWriteError("Negative timestamp")

        attrs['path'] = node_path

        return attrs

    def create(self, validated_data):

        try:
            node = Datanode.objects.get(device__id=self.context['device'].pk,
                                        node_path=validated_data['path'],
                                        name=validated_data['name'])
        except ObjectDoesNotExist:
            node = Datanode(name=validated_data['name'],
                            data_type=validated_data['data_type'],
                            node_path=validated_data['path'],
                            unit=validated_data['unit'],
                            device=self.context['device'])
            node.save()

        datapoint = Datapoint(value=validated_data['value'],
                              created_at=validated_data['timestamp'],
                              node=node)
        datapoint.save()
        ret_data = {'name': validated_data['name'],
                    'path': validated_data['path'],
                    'v': validated_data['value']}
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

    def get_datapoints(self, obj):
        # import ipdb; ipdb.set_trace()
        fromdate = self.context['daterange']['from']
        todate = self.context['daterange']['to']
        order = self.context['order']
        offset = self.context['offset']
        limit = self.context['limit']

        if fromdate and not todate:
            dps = Datapoint.objects.filter(node=obj, created_at__gte=fromdate).order_by(order)  # noqa
        elif fromdate and todate:
            dps = Datapoint.objects.filter(node=obj, created_at__gte=fromdate,
                                           created_at__lte=todate).order_by(order)  # noqa
        else:
            dps = Datapoint.objects.filter(node=obj).order_by('-created_at')
            offset = 0
            limit = 1

        # count = dps.count()
        # if
        serializer = DatapointReadSerializer(dps[offset:offset+limit],
                                             many=True)
        return serializer.data


class DataWriteError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message):
        self.detail = message
