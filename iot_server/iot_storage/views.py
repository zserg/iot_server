from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from iot_storage.models import Device, Datanode, Datapoint
from iot_storage.serializers import DeviceSerializer

import json

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



def datanodes_list(request, deviceid):
    if request.method == 'GET':
        try:
            nodes = Datanode.objects.filter(device__dev_id = deviceid)[:10]
        except:
            nodes = []

        fullsize = len(nodes)
        items = []
        for i in nodes:
            items.append({
                'name':i.name,
                'path':i.node_path,
                'deviceId':i.device.id,
                'unit':i.unit
                })
        response_data = {'fullsize':fullsize,
                    'items':items}

        return JsonResponse(response_data)

def data_write(request, deviceid):
    #check if device exists
    try:
        dev = Device.objects.get(dev_id=deviceid)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('Bad request')

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        body['device'] = dev
        if 'name' in body and 'value' in body:
            #check if datanode exists
            try:
                node = Datanode.objects.get(node_path=body['path'],
                                            name=body['name'])
            except ObjectDoesNotExist:
                node = Datanode.objects.create_datanode(body)
                node.save()

            data = body;
            #data['device'] = dev
            data['node'] = node
            point = Datapoint.objects.create_datapoint(data)
            point.save()

            response_data = {
                    'name':node.name,
                    'path':node.node_path
                    }
            return JsonResponse(response_data)
        else:
            return HttpResponseBadRequest('Bad request')

def get_datanodes(deviceid, name_or_path):
    if '/' in name_or_path:
        try:
            nodes = Datanode.objects.filter(device__dev_id = deviceid,
                                            node_path__contains = name_or_path)[:10]
        except:
            return

    else:
        try:
            nodes = Datanode.objects.filter(device__dev_id = deviceid,
                                            name = name_or_path)[:10]
        except:
            return
    return nodes



def data_read(request, deviceid):
    if request.method == 'GET':
        if 'datanodes' not in request.GET:
            return HttpResponseBadRequest('Bad request: datanode is absent')
        else:
            nodes_names = request.GET['datanodes'].split(',')

        if 'todate' in request.GET and 'fromdate' not in request.GET:
            return HttpResponseBadRequest('Bad request: todate is absent')

        dates_range = {'from':request.GET.get('fromdate',''),
                       'to':request.GET.get('todate','')}



        response_data = {'datanodeReads':[]}
        nodes = None
        for node_name in nodes_names:
            ns  = get_datanodes(deviceid, node_name)
            if ns:
                if nodes:
                    nodes |= ns
                else:
                    nodes = ns

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




