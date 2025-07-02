from nominal.core import NominalClient
from retrieve_asset import retrieve_asset

# Assumes authentication has already been performed.
# Replace "default" with your profile name.
client = NominalClient.from_profile("watchtower")

# Using utility from previous section on creating assets
# Hardcoding platform and serial number for this example, but typically this would be
# computed dynamically based on metadata about the data files, such as the filepath.
asset = retrieve_asset(client, platform="satellite", serial_num="25544")

# Create dataset (only required for the first upload for a given data source)
dataset = client.create_dataset(
    # Human readable name for the dataset
    name="State Vectors",
    # Key-value properties that are useful for looking up and finding this dataset
    properties={
        "platform": "satellite",
        "serial_num": "25544",
    },
    # Optional description for the dataset, useful for storing notes for future readers
    description="All state vectors generated 11-1-2018 or later",
    # Optional method to preserve the hierachical structure of the data
    prefix_tree_delimiter="."
)
dataset.add_tabular_data(
    path="core/satellite_25544_data.csv",
    # Column within the parquet file containing absolute or relative timestamp information
    # for all other columns within the file
    timestamp_column="timestamp",
    # Type of data contained within the timestamp column.
    # Using absolute floating point seconds from unix epoch for this example, but a wide variety
    # of formats are supported, such as other resolutions of time, relative timestamps, or even custom-formatted
    # string timestamps (e.g. ISO8601).
    timestamp_type="iso_8601"
)

# Attach the dataset to the asset
asset.add_dataset(
    # reference name for this dataset within the asset
    # This can be used later to retrieve a reference to this dataset via the same reference name for
    # future flight tests
    "state_vectors",
    dataset,
)
