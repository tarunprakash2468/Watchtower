import base64, json, nominal, os, pandas, questionary, requests, sys, urllib3
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from nominal.core import NominalClient

# --- SETUP & CONFIG ---

# API token from .env file
load_dotenv()
basicAuth = os.getenv('basicAuth')
n2yo_key = os.getenv('n2yo_key')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Get a client to interact with Nominal.
client = NominalClient.from_profile("watchtower")

# --- USER INPUT ---

# Define satellite
satellite_number = input("Enter the satellite number (e.g. 25544 for ISS): ")
print()

# Define UDL API
answer = questionary.select(
    "Which UDL API should be used?",
    choices=[
        questionary.Choice(title="Rest API                  — recent data (30–365 days)", value="Rest API"),
        questionary.Choice(title="History Rest API          — archived time series (30+ days)", value="History Rest API"),
        questionary.Choice(title="Bulk Data Request API     — large async downloads (CSV/JSON)", value="Bulk Data Request API"),
        questionary.Choice(title="Secure Messaging API      — real-time streaming (restricted)", value="Secure Messaging API"),
    ]
).ask()
print()

# Check UDL API selection
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

start_dt = get_valid_date(prompt_label="start date & time")
end_dt = get_valid_date(prompt_label="end date & time")

start_time = start_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
end_time = end_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

# --- MAKE REQUEST ---

# Define query URL
base_udl_url = "https://unifieddatalibrary.com"
query_udl_url = None

if answer == "Rest API":
    query_udl_url = f"{base_udl_url}/udl/statevector?epoch={start_time}..{end_time}&satNo={satellite_number}"
elif answer == "History Rest API":
    query_udl_url = f"{base_udl_url}/udl/statevector/history?epoch={start_time}..{end_time}&satNo={satellite_number}"
elif answer == "Bulk Data Request API":
    query_udl_url = f"{base_udl_url}/udl/statevector/history/aodr?epoch={start_time}..{end_time}&satNo={satellite_number}&outputFormat=JSON"
elif answer == "Secure Messaging API":
    exit()

if query_udl_url is None:
    print("Query URL could not be determined.")
    exit()

# Submit request to UDL API
udl_response = requests.get(query_udl_url, headers={'Authorization': basicAuth}, verify=False)

# Check UDL response status
if udl_response.status_code == 200:
    try:
        data = udl_response.json()
    except json.decoder.JSONDecodeError:
        print("udl_response was not valid JSON:")
        print(udl_response.text)
        exit()
else:
    print(f"Request failed with status code {udl_response.status_code}")
    print(udl_response.text)
    exit()

# --- PARSE DATA ---

# Parse data from JSON
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

# Convert data structure
df = pandas.DataFrame(parsed_data)
df.to_csv(f'data/satellite_{satellite_number}_data.csv', index=False)

# --- CREATE ASSET ---

# Look up satellite in N2YO API
base_n2yo_url = "https://api.n2yo.com/rest/v1/satellite/"
query_n2yo_url = f"{base_n2yo_url}/tle/{satellite_number}&apiKey={n2yo_key}"
n2yo_response = requests.get(query_n2yo_url)
n2yo_data = n2yo_response.json()
satellite_name = n2yo_data["info"]["satname"]

# Create an asset in Nominal
asset = client.create_asset(
    name=satellite_name,
    properties={
        "platform": "satellite",
        "serial_num": satellite_number,
    }
)

# --- UPLOAD DATA ---

# Retrieve asset
def retrieve_asset(
    client: nominal.NominalClient,
    platform: str,
    serial_num: str
) -> nominal.Asset:
    properties = {"platform": platform, "serial_num": serial_num}
    existing_assets = client.search_assets(
        properties=properties
    )
    if len(existing_assets) > 1:
        raise RuntimeError(
            f"Too many assets ({len(existing_assets)}) found with properties {properties}"
        )
    elif len(existing_assets) == 0:
        raise RuntimeError(
            f"No such asset found with properties {properties}"
        )
    else:
        return existing_assets[0]

asset = retrieve_asset(client, platform="satellite", serial_num=satellite_number)

# Create dataset
dataset = client.create_dataset(
    name="State Vectors",
    properties={
        "platform": "satellite",
        "serial_num": satellite_number,
    },
    description=f"All state vectors generated between {start_time} and {end_time}",
    prefix_tree_delimiter="."
)

# Add tabular data
dataset.add_tabular_data(
    path=f"data/satellite_{satellite_number}_data.csv",
    timestamp_column="timestamp",
    timestamp_type="iso_8601"
)

# Attach dataset
asset.add_dataset(
    "state_vectors",
    dataset,
)

# Create run
run = client.create_run(
    name=f"Historial Data between {start_time} and {end_time}",
    start=start_dt,
    end=end_dt,
    properties={
        "platform": "satellite",
        "serial_num": satellite_number
    },
    asset=asset,
    description=f"All state vectors generated between {start_time} and {end_time}",
)
