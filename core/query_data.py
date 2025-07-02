import requests
import base64
import pandas as pd
from datetime import datetime, timedelta, timezone

# --- CONFIGURATION ---

# Base64 API token from UDL utility
basicAuth = "Basic dGFydW4ucHJha2FzaDpCeXdtdWstcWluemkyLWd1cndvbg=="

# Define satellite
satellite_number = 25544

# Define time window
now = datetime.now(timezone.utc)
previous = now - timedelta(days=2500)

# Format the time window for the query
start_time = previous.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
end_time = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

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
df.to_csv(f'core/satellite_{satellite_number}_data.csv', index=False)
print(f"Data saved to satellite_{satellite_number}_data.csv")