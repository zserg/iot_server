from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from iot_storage.models import Device, Datanode, Datapoint

from datetime import datetime

    # name = models.CharField(max_length=255)
    # dev_id = models.CharField(max_length=16)
    # dev_type = models.CharField(max_length=255)
    # description = models.TextField()
    # attributes = JSONField()
    # created_at = models.DateTimeField(auto_now_add=True)

class DeviceSerializer(serializers.ModelSerializer):
    # dev_id = serializers.Field(source='get_dev_id')

    class Meta:
        model = Device
        fields = ('dev_id', 'name', 'dev_type', 'description',
                  'attributes', 'created_at')
        extra_kwargs = {'dev_id': {'read_only': 'True'}}

    def create(self, validated_data):
        device = Device.objects.create_device(validated_data)
        return device

class DatapointSerializer(serializers.ModelSerializer):

    class Meta:
        model = Datapoint
        fields = ('data_type', 'value', 'dev_type', 'description',
                  'attributes', 'created_at')
        extra_kwargs = {'dev_id': {'read_only': 'True'}}

    def create(self, validated_data):
        device = Device.objects.create_device(validated_data)
        return device
    # data_type = models.CharField(max_length=8, default='str' )
    # value = models.CharField(max_length=255)
    # timestamp = models.DateTimeField(auto_now_add=True)
    # node = models.ForeignKey(Datanode, on_delete=models.CASCADE)
    # device = models.ForeignKey(Device, on_delete=models.CASCADE)

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
        print(validated_data)
        try:
            node = Datanode.objects.get(device__id=self.context['device'].pk,
                                         node_path=validated_data['path'])
        except ObjectDoesNotExist:
            if validated_data['data_type']:
                node_data_type = validated_data['data_type']
            else:
                node_data_type = get_data_type(validated_data['value'])

            node = Datanode(name=validated_data['name'], data_type=node_data_type,
                            node_path=validated_data['path'], unit=validated_data['unit'] ,
                            device=self.context['device'])
            node.save()

        created_at = datetime.fromtimestamp(validated_data['timestamp'])
        datapoint = Datapoint(data_type=node.data_type,
                             value=validated_data['value'],
                             timestamp=created_at,
                             node=node,
                             device=self.context['device'])
        return datapoint

