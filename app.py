from flask import Flask, Response
import requests
import xml.etree.ElementTree as ET
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def get_data():
    try:
        # Make a request to the API with updated parameters
        response = requests.get("https://api.open-meteo.com/v1/forecast?latitude=45.7485&longitude=4.8467&current=temperature_2m,apparent_temperature,cloud_cover&hourly=temperature_2m,cloud_cover&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset")
        data = response.json()

        # Log the response
        logging.debug(f"API response: {data}")

        # Check if the API call was successful
        if response.status_code != 200:
            raise ValueError("Failed to retrieve data")

        # Create a root XML element
        root = ET.Element("WeatherData")

        # Add current weather data
        current = ET.SubElement(root, "CurrentWeather")
        for key, value in data['current'].items():
            ET.SubElement(current, key).text = str(value)

            # Add hourly weather data
        hourly = ET.SubElement(root, "HourlyWeather")
        hourly_times = data['hourly']['time']
        cloud_covers = data['hourly']['cloud_cover']
        temperatures = data['hourly']['temperature_2m']  # Corrected key from 'temperature' to 'temperature_2m'

        for time, cloud_cover, temp in zip(hourly_times, cloud_covers, temperatures):
            formatted_time = time.replace('T', ' ')  # This replaces 'T' with a space
            hour = ET.SubElement(hourly, "Hour", time=formatted_time)
            ET.SubElement(hour, "CloudCover").text = str(cloud_cover)
            ET.SubElement(hour, "Temperature").text = str(temp)  # Adjusted to match corrected key

        # Add daily weather data
        daily = ET.SubElement(root, "DailyWeather")
        daily_times = data['daily']['time']
        max_temps = data['daily']['temperature_2m_max']
        min_temps = data['daily']['temperature_2m_min']
        sunrises = data['daily']['sunrise']
        sunsets = data['daily']['sunset']
        for day, max_temp, min_temp, sunrise, sunset in zip(daily_times, max_temps, min_temps, sunrises, sunsets):
            day_elem = ET.SubElement(daily, "Day", date=day)
            ET.SubElement(day_elem, "MaxTemperature").text = str(max_temp)
            ET.SubElement(day_elem, "MinTemperature").text = str(min_temp)
            ET.SubElement(day_elem, "Sunrise").text = sunrise
            ET.SubElement(day_elem, "Sunset").text = sunset


        # Convert the XML tree to a string and return it
        xml_str = ET.tostring(root, encoding='utf8', method='xml')
        return Response(xml_str, mimetype='text/xml')

    except Exception as e:
        logging.error(f"Error retrieving data: {str(e)}")
        return Response(f"Error retrieving data: {str(e)}", status=500)

if __name__ == '__main__':
    app.run(debug=True)
