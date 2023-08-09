from pymongo import MongoClient
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# MongoDB setup
mongo_uri = "mongodb+srv://djain:fYc5S8L7GY0ndmGK@weather.gnfkfe3.mongodb.net/Weather_db?ssl=true&ssl_cert_reqs=CERT_NULL"
client = MongoClient(mongo_uri)
database = client['Weather_db']
records = database['Weather_current']

# HTML content for the map visualization (will be stored in a separate file)
html_content = open('index_with_map_attribute.html').read()

@app.route('/')
def index():
    return render_template_string(html_content)

@app.route('/data')
def get_data():
    try:
        attribute = request.args.get('attribute', 'temperature')  # Selected attribute from query parameter
        # Aggregation query to fetch data for the world map
        pipeline_world_map = [
            {
                "$project": {
                    "_id": 0,
                    "lat": {"$toDouble": "$location.lat"},
                    "lon": {"$toDouble": "$location.lon"},
                    "city": "$location.name",
                    "country": "$location.country",
                    "value": {"$toInt": f"$current.{attribute}"},
                }
            },
        ]
        world_map_data = list(records.aggregate(pipeline_world_map))
        formatted_data = [[item['lat'], item['lon'], item['city'], item['country'], item['value'],
                           item['city'] + ': ' + str(item['value'])] for item in world_map_data]

        return jsonify(formatted_data)
    except Exception as e:
        return str(e)  # Return the exception message to the browser

@app.route('/cities')
def get_cities():
    # Query to fetch distinct cities to populate the dropdown
    cities = records.distinct("location.name")
    return jsonify(cities)

@app.route('/countries')
def get_countries():
    # Query to fetch distinct countries
    countries = records.distinct("location.country")
    return jsonify(countries)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
