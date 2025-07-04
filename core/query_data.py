import requests
import urllib3
import base64
import os
import inquirer
import json
import pandas as pd
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# --- CONFIGURATION ---

# Base64 API token from UDL utility
load_dotenv()  # take environment variables
basicAuth = os.getenv('basicAuth')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define satellite
satellite_number = input("Enter the satellite number (e.g. 25544 for ISS): ")

# Define which UDL API to use
questions = [
    inquirer.List(
        "API",
        message="Which UDL API should be used?",
        choices=["Rest API", "History Rest API", "Bulk Data Request API", "Secure Messaging API"],
    ),
]

answers = inquirer.prompt(questions)

# Define time window
def get_valid_date(prompt_label="time"):
    while True:
        date_str = input(f"Enter {prompt_label} (ISO 8601, e.g. 2025-07-03T18:30:00.00Z): ")
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            print("Invalid date format. Please use ISO 8601 format.")

start_time = get_valid_date(prompt_label="start date & time").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
end_time = get_valid_date(prompt_label="end date & time").strftime("%Y-%m-%dT%H:%M:%S.%fZ")

# Build the query URL
base_url = "https://unifieddatalibrary.com"
query_url = (
    f"{base_url}/udl/statevector?"
    f"epoch={start_time}..{end_time}&"
    f"satNo={satellite_number}"
)

# --- MAKE THE REQUEST ---

response = requests.get(query_url, headers={'Authorization': basicAuth}, verify=False)
data = response.json()

print(json.dumps(data, indent=2))

# --- EXTRACT FIELDS ---

# Parse data from JSON response
parsed_data = []
for entry in data:
    try:
        parsed_data.append({
            'timestamp': entry['epoch'],
            'pos.x': entry['xpos'],
            'pos.y': entry['ypos'],
            'pos.z': entry['zpos'],
            'vel.x': entry['xvel'],
            'vel.y': entry['yvel'],
            'vel.z': entry['zvel'],
        })
    except KeyError as e:
        print(f'Skipping entry due to missing key: {e}')

# Convert to DataFrame
df = pd.DataFrame(parsed_data)
df.to_csv(f'data/satellite_{satellite_number}_data.csv', index=False)
print(f"Data saved to satellite_{satellite_number}_data.csv")