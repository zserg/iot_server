from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from iot_storage.models import Device, Datanode, Datapoint
from iot_storage.serializers import DeviceSerializer, DataWriteSerializer, DatanodeSerializer

import json
import string

@api_view(['GET', 'POST'])
def device_list(request, format=None):
    """
    List all devices, or create a new one.
    """
    if request.method == 'GET':
        devices = Device.objects.all()
        serializer = DeviceSerializer(devices, many=True)

        return Response({'fullsize': len(serializer.data),
                             'items':serializer.data})

    elif request.method == 'POST':
        serializer = DeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
def device_detail(request, deviceid):
    """
    Retrive, update or delete a device instace.
    """
    try:
        device = Device.objects.get(dev_id = deviceid)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DeviceSerializer(device)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def data_write(request, deviceid):
    #check if device exists
    try:
        dev = Device.objects.get(dev_id=deviceid)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('Bad request')

    serializer = DataWriteSerializer(data=request.data, many=True,
                                     context = {'device':dev})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        #return Response(status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def datanodes_list(request, deviceid):
    if request.method == 'GET':
        print('datanodes_list')
        try:
            nodes = Datanode.objects.filter(device__dev_id = deviceid)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = DatanodeSerializer(nodes, many=True)

        return Response({'fullsize': len(serializer.data),
                             'items':serializer.data})


def get_datanodes(deviceid, fullpath):
    fullpath = str.strip(fullpath,'/')
    path_l = str.rsplit(fullpath,'/',1)

    print('fullpath={}, path_l={}'.format(fullpath, path_l))
    if len(path_l) == 1: # name only
        name = path_l[0]
        print("aa")
            #nodes = Datanode.objects.filter(device__dev_id=deviceid)
        try:
            nodes = Datanode.objects.filter(device__dev_id=deviceid, name=name)
            print("name:{}".format(nodes[0]))
        except:
            return
    else:
        path = path_l[0]
        name = path_l[1]
        try:
            print("path:{}".format(nodes))
            nodes = Datanode.objects.filter(device__dev_id = deviceid, name=name, node_path=path)
        except:
            return

    return nodes


@api_view(['GET'])
def data_read(request, deviceid):
    if request.method == 'GET':
        if 'datanodes' not in request.GET:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            nodes_names = request.GET['datanodes'].split(',')
        print('data_read:{}'.format(nodes_names))
        if 'todate' in request.GET and 'fromdate' not in request.GET:
            return Response(status=status.HTTP_404_NOT_FOUND)

        dates_range = {'from':request.GET.get('fromdate',''),
                       'to':request.GET.get('todate','')}


        response_data = {'datanodeReads':[]}
        nodes = None
        for node_name in nodes_names:
            ns  = get_datanodes(deviceid, node_name)
            print('nodes:{}'.format(ns))
            if ns:
                if nodes:
                    nodes |= ns
                else:
                    nodes = ns
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

        for node in nodes:
            node_data = {'name': node.name,
                         'path': node.node_path,
                         'values': []}

            try:
                dpoints = Datapoint.objects.filter(device__dev_id = deviceid,
                                                   node = node)[:50]
            except:
                dpoints = []

            for dpoint in dpoints:
                dvalue = {'v': dpoint.value_int, 'ts': dpoint.timestamp}
                node_data['values'].append(dvalue)

            response_data['datanodeReads'].append(node_data)

        return JsonResponse(response_data)




