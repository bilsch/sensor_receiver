from flask import Flask
from flask import request, abort, make_response
from influxdb import InfluxDBClient

app = Flask(__name__)
influx_database = 'temperature_sensors'
influx_client = InfluxDBClient(host="localhost", database=influx_database)


@app.route("/sensor_data/temp_sensor/<string:sensor_name>", methods=['POST'])
def add_sensor_value(sensor_name):
    """
    Will receive temperature sensor data

    Fields:
    temp ( require )
    humidity ( optional )

    :return: http status
        If recorded successfully, 200 else 500
    """
    if request.content_type != 'application/json':
        return make_response('<html><body>Must send data as <b>application/json</b>!</body></html>', 500)

    data: dict = request.get_json(force=True)
    data["sensor_name"] = sensor_name

    if 'temperature' in data.keys():
        influx_client.write(points=data)
        return make_response(data)
    else:
        return make_response('<html><body>You must include at least <b>temperature</b></body></html>')


@app.route("/sensors", methods=['GET'])
def get_temp_sensors():
    """
    Will return sensor ids which have submitted data within the past 24 hours
    :return:
    """
    return "Not implemented yet"


@app.route('/')
def hello_world():
    return 'Sensors!'

if __name__ == '__main__':
    app.run()
