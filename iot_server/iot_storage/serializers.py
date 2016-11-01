from rest_framework import serializers
from iot_storage.models import Device, Datanode, Datapoint

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

class DataWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    value = serializers.CharField(max_length=255)
    data_type = models.CharField(max_length=8, default='str' )
    timestamp = models.IntegerField(delault=0)
    path = serializers.TextField(delault='')

    def create(self, validated_data):
        try:
            node = Datanode.objects.get(dev_id=context['deviceid'])
        except ObjectDoesNotExist:
            node = Datanode(name=name, data_typeata['name'],
                    data_type=data.get('data_type',''),
                    node_path=data.get('path',''),
                    unit=data.get('unit',''),
                    device=data['device'])
            return HttpResponseBadRequest('Bad request')

        pass

    def validate(self, value):
        """
        Check that data_type matches the datanode's data type
        """
        try:
            node = Datanode.objects.get(dev_id=deviceid)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest('Bad request')

