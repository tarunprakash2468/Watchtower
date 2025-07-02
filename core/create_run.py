from datetime import datetime, timedelta, timezone
from nominal.core import NominalClient
from retrieve_asset import retrieve_asset

# Assumes authentication has already been performed
# Replace "default" with your profile name
client = NominalClient.from_profile("watchtower")

# Using utility from previous section on creating assets
# Hardcoding platform and serial number for this example, but typically this would be
# computed dynamically based on metadata about the data files, such as the filepath.
asset = retrieve_asset(client, platform="satellite", serial_num="25544")

# Define time window
now = datetime.now(timezone.utc)
previous = now - timedelta(days=2500)

# Format the time window for the query
start_time = previous.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
end_time = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

# Create the run in Nominal and associate with the Asset producing the data
run = client.create_run(
    name="Historial Data after 11/01/2018",
    start=previous,
    end=now,
    # Useful for looking up runs later on by asset properties
    properties={
        "platform": "satellite",
        "serial_num": "25544"
    },
    # Link back to the asset containing data for this run
    asset=asset,
    # Optional human description of the run, useful for describing what maneuvers we tested
    description="All state vectors generated 11-1-2018 or later",
)
