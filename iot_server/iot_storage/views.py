from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist

from iot_storage.models import Device, Datanode, Datapoint
import json

def devices_list(request):
    if request.method == 'GET':
        try:
            devs = Device.objects.all()[:10]
        except:
            devs = []

        fullsize = len(devs)
        items = []
        for i in devs:
            items.append({
                'name':i.name,
                'type':i.dev_type,
                'deviceId':i.dev_id,
                'description':i.description,
                'attributes':i.attributes
                })
        response_data = {'fullsize':fullsize,
                    'items':items}

        return JsonResponse(response_data)
    else:
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if 'name' in body:
            dev = Device.objects.create_device(body)
            dev.save()
            response_data = {
                    'name':dev.name,
                    'deviceId':dev.dev_id
                    }
            return JsonResponse(response_data)
        else:
            return HttpResponseBadRequest('Bad request')


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





