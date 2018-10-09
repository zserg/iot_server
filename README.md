# IoT Storage Server
IoT API server based on Django REST framework.

# HTTP API
## Data Model
User -> Device -> Data Node
## API URL
https://<server_name>/api/v1
## Endpoints
### /devices
#### Create device
URL: /devices

HTTP method: POST

Authentication Required: Yes

Body:
```
{ 
   "name": "Sensor1",
   "manufacturer": "IDT",
   "type": "temp_sensor",
   "description": "The main room temperature sensor",
   "attributes":[{  
      "key":"Version",
      "value": "1.1.2"},
      {
       "key":"Type","value":"i2c"}
       ]
}
```
#### Get devices
URL: /devices

HTTP method: GET

Authentication Required: Yes

Response:
```
```
#### Get device info
URL: /devices/deviceId

HTTP method: GET

Authentication Required: Yes

#### Get a device's datanodes list
URL: /devices/deviceId/datanodes/

HTTP method: GET

Authentication Required: Yes
### /data
#### Write data
URL: /data/write/deviceId/

HTTP method: POST

Authentication Required: Yes

#### Read data
URL: /data/read/deviceId/

HTTP method: GET

Authentication Required: Yes
