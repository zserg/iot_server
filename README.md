# IoT Storage Server
IoT storage API server based on Django REST framework.
## Data Model
User -> Device -> Data Node

A user can have multiple devices. Data values are stored in the device's data nodes. A new data node is created when the server writes data into the one that has never been appeared before.
## API URL
https://<server_name>/iot_storage/api/v1
## Endpoints
/devices

/data

# HTTP API
## Authentication
API server uses token based authentication. Firts you have to create a user/password via django admin site:
https://<server_name>/admin

**Get a token for the user**:
```
curl -d 'username=<user>&password=<password>' http://localhost:8000/iot_storage/api/v1/api-token-auth/
```
```
{
   "token":"0b618dda9e96100928c1285069a8a8212fa4392c"
}
```
**Create a device**:

URL: /devices/

HTTP method: POST

Authentication Required: Yes
```
curl -H 'Authorization: Token 0b618dda9e96100928c1285069a8a8212fa4392c' \
   -H 'Content-Type: application/json' \
   -d '{"name":"Sensor #1",
        "dev_type":"temperature_sensor",
        "description":"Main room temp sensor"
        }' \
       http://localhost:8000/iot_storage/api/v1/devices/
```
```
{
   "dev_id":"22bf78c836514daf",
   "name":"Sensor #1",
   "dev_type":"temperature_sensor",
   "description":"Main room temp sensor",
   "attributes":{},
   "created_at":"2018-10-12T21:39:45.932758+03:00",
   "href":"http://localhost:8000/iot_storage/api/v1/devices/22bf78c836514daf/
   "}
```
**Get list of devices**:

URL: /devices/

HTTP method: GET

Authentication Required: Yes
```
curl -H 'Authorization: Token 0b618dda9e96100928c1285069a8a8212fa4392c' \
       http://localhost:8000/iot_storage/api/v1/devices/
```
```
{
   "fullsize":2,
   "items":[
            {
               "dev_id":"22bf78c836514daf",
               "name":"Sensor #1",
               "dev_type":"temperature_sensor",
               "description":"Main room temp sensor",
               "attributes":{},
               "created_at":"2018-10-12T21:39:45.932758+03:00",
               "href":"http://localhost:8000/iot_storage/api/v1/devices/22bf78c836514daf/"
             },
             {
               "dev_id":"cd0bf1fcd2e941d6",
               "name":"Sensor #2",
               "dev_type":"",
               "description":"",
               "attributes":{},
               "created_at":"2018-10-12T21:46:34.517636+03:00",
               "href":"http://localhost:8000/iot_storage/api/v1/devices/cd0bf1fcd2e941d6/"
               }
              ]
}
```
**Get a single device**:

URL: /devices/deviceId/

HTTP method: GET

Authentication Required: Yes
```
curl -H 'Authorization: Token 0b618dda9e96100928c1285069a8a8212fa4392c' \
     http://localhost:8000/iot_storage/api/v1/devices/22bf78c836514daf/
```
```
{
   "dev_id":"22bf78c836514daf",
   "name":"Sensor #1",
   "dev_type":"temperature_sensor",
   "description":"Main room temp sensor",
   "attributes":{},
   "created_at":"2018-10-12T21:39:45.932758+03:00",
   "href":"http://localhost:8000/iot_storage/api/v1/devices/22bf78c836514daf/"
}
```
**Writing data**:

URL: /data/write/deviceId/

HTTP method: POST

Authentication Required: Yes
```
curl -H 'Authorization: Token 0b618dda9e96100928c1285069a8a8212fa4392c' \
     -H 'Content-Type: application/json' \
     -d '[
          {"name":"Temperature",
           "path":"house/main_room",
           "data_type":"C",
           "value":"12.2"}
         ]' \
      http://localhost:8000/iot_storage/api/v1/data/write/22bf78c836514daf/
```
```
[
  {
   "name":"Temperature",
   "path":"house/main_room",
   "v":"12.2"
  }
]
```
Writing multiple data value into the same data node:
```
curl -H 'Authorization: Token 0b618dda9e96100928c1285069a8a8212fa4392c' \
     -H 'Content-Type: application/json' \
     -d '[
          {"name":"Temperature",
           "path":"house/main_room",
           "data_type":"C",
           "value":"12.2"},

          {"name":"Temperature",
           "path":"house/main_room",
           "data_type":"C",
           "value":"13.0"},

          {"name":"Temperature",
           "path":"house/main_room",
           "data_type":"C",
           "value":"14.2"},

         ]' \
      http://localhost:8000/iot_storage/api/v1/data/write/22bf78c836514daf/
```
```
[
  {
   "name":"Temperature",
   "path":"house/main_room",
   "v":"12.2"
  },
  {
   "name":"Temperature",
   "path":"house/main_room",
   "v":"13.0"
  },
  {
   "name":"Temperature",
   "path":"house/main_room",
   "v":"14.2"
  },

]
```
**Get a device's datanodes list**

URL: /devices/deviceId/datanodes/

HTTP method: GET

Authentication Required: Yes
```
curl -H 'Authorization: Token 0b618dda9e96100928c1285069a8a8212fa4392c' \
     http://localhost:8000/iot_storage/api/v1/devices/22bf78c836514daf/datanodes/
```
```
{
  "fullsize":1,
  "items":[
            {
              "name":"Temperature",
              "node_path":"house/main_room",
              "data_type":"float",
              "unit":"",
              "created_at":"2018-10-13T22:29:02.628756+03:00",
              "href":"http://localhost:8000/iot_storage/api/v1/data/read/22bf78c836514daf?datanodes=house/main_room/Temperature"
            }
          ]
}
```
**Reading data**:
URL: /data/read/deviceId/

HTTP method: GET

Authentication Required: Yes
```
curl -H 'Authorization: Token 0b618dda9e96100928c1285069a8a8212fa4392c' \
"http://localhost:8000/iot_storage/api/v1/data/read/22bf78c836514daf?\
datanodes=house/main_room/Temperature&fromdate=1539458937&limit=2"
```
```
[
  {
    "name":"Temperature",
    "node_path":"house/main_room",
    "points":[
                {
                  "value":"12.2",
                  "created_at":1539458937
                },
                {
                  "value":"12.2",
                  "created_at":1539522081
                }
             ]
  }
]
```
