import base64, json, os, pandas, questionary, requests, sys, urllib3
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# --- CONFIGURATION ---

# Base64 API token from UDL utility
load_dotenv()  # take environment variables
basicAuth = os.getenv('basicAuth')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define satellite
satellite_number = input("Enter the satellite number (e.g. 25544 for ISS): ")
print()

# Define which UDL API to use
answer = questionary.select(
    "Which UDL API should be used?",
    choices=[
        questionary.Choice(title="Rest API              — fast access for recent data", value="Rest API"),
        questionary.Choice(title="History Rest API      — archived time series, forensic analysis", value="History Rest API"),
        questionary.Choice(title="Bulk Data Request API — async large dataset export (CSV/JSON)", value="Bulk Data Request API"),
        questionary.Choice(title="Secure Messaging API  — real-time streaming (restricted)", value="Secure Messaging API"),
    ]
).ask()
print()

# End program if Secure Messaging API is selected
if answer == 'Secure Messaging API':
    print("Secure Messaging API requires access request. Please contact UDL support for access.")
    sys.exit()

# Define time window
def get_valid_date(prompt_label="time"):
    while True:
        date_str = input(f"Enter {prompt_label} (ISO 8601, e.g. 2025-07-03T18:30:00.000000Z): ")
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            print("Invalid date format. Please use ISO 8601 format.")

start_time = get_valid_date(prompt_label="start date & time").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
end_time = get_valid_date(prompt_label="end date & time").strftime("%Y-%m-%dT%H:%M:%S.%fZ")

# Build the query URL
base_url = "https://unifieddatalibrary.com"
query_url = None

if answer == "Rest API":
    query_url = f"{base_url}/udl/statevector?epoch={start_time}..{end_time}&satNo={satellite_number}"
elif answer == "History Rest API":
    query_url = f"{base_url}/udl/statevector/history?epoch={start_time}..{end_time}&satNo={satellite_number}"
elif answer == "Bulk Data Request API":
    query_url = f"{base_url}/udl/statevector/history/aodr?epoch={start_time}..{end_time}&satNo={satellite_number}&outputFormat=JSON"
elif answer == "Secure Messaging API":
    exit()

if query_url is None:
    print("Query URL could not be determined.")
    exit()

# --- MAKE THE REQUEST ---

response = requests.get(query_url, headers={'Authorization': basicAuth}, verify=False)

if response.status_code == 200:
    try:
        data = response.json()
    except json.decoder.JSONDecodeError:
        print("Response was not valid JSON:")
        print(response.text)
        exit()
else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)
    exit()

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
df = pandas.DataFrame(parsed_data)
df.to_csv(f'data/satellite_{satellite_number}_data.csv', index=False)
print(f"\nData saved to satellite_{satellite_number}_data.csv")