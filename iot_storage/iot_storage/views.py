from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from iot_storage.models import Device, Datanode
from iot_storage.serializers import DeviceSerializer, DataWriteSerializer
from iot_storage.serializers import DatanodeSerializer
from iot_storage.serializers import DataReadSerializer

MAX_LIMIT = 10000
DEFAULT_LIMIT = 1000


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def device_list(request, format=None):
    """
    List all devices, or create a new one.
    """
    if request.method == 'GET':
        devices = Device.objects.all()
        serializer = DeviceSerializer(devices, many=True,
                                      context={'request': request})

        return Response({'fullsize': len(serializer.data),
                         'items': serializer.data})

    elif request.method == 'POST':
        # import ipdb; ipdb.set_trace()
        serializer = DeviceSerializer(data=request.data,
                                      context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
@permission_classes((IsAuthenticated,))
def device_detail(request, deviceid):
    """
    Retrive or delete a device instace.
    """
    try:
        device = Device.objects.get(dev_id=deviceid)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DeviceSerializer(device, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'DELETE':
        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def data_write(request, deviceid):
    # check if device exists
    # import ipdb; ipdb.set_trace()
    try:
        dev = Device.objects.get(dev_id=deviceid)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('Bad request')

    serializer = DataWriteSerializer(data=request.data, many=True,
                                     context={'device': dev})
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def datanodes_list(request, deviceid):
    # import ipdb; ipdb.set_trace()
    if request.method == 'GET':
        try:
            nodes = Datanode.objects.filter(device__dev_id=deviceid)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = DatanodeSerializer(nodes, many=True,
                                        context={'request': request})

        return Response({'fullsize': len(serializer.data),
                         'items': serializer.data})


def get_datanodes(deviceid, fullpath):
    fullpath = str.strip(fullpath, '/')
    path_l = str.rsplit(fullpath, '/', 1)

    if len(path_l) == 1:  # name only
        name = path_l[0]
        try:
            nodes = Datanode.objects.filter(device__dev_id=deviceid, name=name)
        except ObjectDoesNotExist:
            return
    else:
        path = path_l[0]
        name = path_l[1]
        try:
            nodes = Datanode.objects.filter(device__dev_id=deviceid,
                                            name=name, node_path=path)
        except ObjectDoesNotExist:
            return

    return nodes


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def data_read(request, deviceid):
    if request.method == 'GET':
        # import ipdb; ipdb.set_trace()
        if 'datanodes' not in request.GET:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            nodes_names = request.GET['datanodes'].split(',')

        if 'todate' in request.GET and 'fromdate' not in request.GET:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if 'fromdate' not in request.GET:
            limit = 1
        else:
            limit = int(request.GET.get('limit', DEFAULT_LIMIT))
            if limit > MAX_LIMIT:
                limit = MAX_LIMIT

        dates_range = {'from': int(request.GET.get('fromdate', '0')),
                       'to': int(request.GET.get('todate', '0'))}

        if request.GET.get('order', '') == 'desc':
            order = '-created_at'
        else:
            order = 'created_at'

        offset = request.GET.get('offset', 0)

        nodes = None
        for node_name in nodes_names:
            ns = get_datanodes(deviceid, node_name)
            if ns:
                if nodes:
                    nodes |= ns
                else:
                    nodes = ns
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = DataReadSerializer(nodes, many=True,
                                        context={'daterange': dates_range,
                                                 'order': order,
                                                 'limit': limit,
                                                 'offset': offset})

        return Response(serializer.data)
