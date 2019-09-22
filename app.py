from flask import Flask
from flask import request, abort, make_response
from influxdb import InfluxDBClient
from datetime import datetime

app = Flask(__name__)
influx_database = 'temperature_sensors'
influx_client = InfluxDBClient(host="localhost", database=influx_database)
current_databases = list(map(lambda x: x.get('name'), influx_client.get_list_database()))
if influx_database not in current_databases:
    influx_client.create_database(influx_database)

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

    data: dict = dict()
    data["measurement"] = sensor_name
    data["tags"] = {'sensor_type': "temperature"}
    data["time"] = datetime.now().isoformat()
    data['fields'] = request.get_json(force=True)

    if 'temperature' in data.get('fields').keys():
        msg = "Writing {} data to influx: {}".format(sensor_name, data)
        print(msg)
        influx_client.write_points([data])
        return make_response("<html><body>OK</body></html>\n")
    else:
        return make_response('<html><body>You must include at least <b>temperature</b></body></html>', 500)


@app.route("/sensors", methods=['GET'])
def get_temp_sensors(html=True):
    """
    Will return sensor ids which have submitted data within the past 24 hours
    :return:
    """
    current_sensors: list = list(map(lambda x: x.get('name'), influx_client.get_list_measurements()))

    if html:
        return make_response("<html><body><ol>{}</ol></body></html>".format("<li>".join(current_sensors)))
    else:
        current_sensors


@app.route('/')
def hello_world():
    return '<html><body><p><a href="/sensors">Sensors</a>!</body></html>'

if __name__ == '__main__':
    app.run()
