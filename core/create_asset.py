from nominal.core import NominalClient

# Get a client to interact with Nominal.
# Assumes authentication has already been performed.
# Replace "default" with your profile name.
client = NominalClient.from_profile("watchtower")

asset = client.create_asset(
    # Human readable name for the asset
    name="International Space Station",
    # Optional description, useful if you have notes about this glider.
    description="The International Space Station (ISS) is a habitable artificial satellite in low Earth orbit.",
    # Properties which can help us find this asset later.
    # Ideally, you should be able to uniquely identify any physical asset
    # using some combination of these properties.
    properties={
        "platform": "satellite",
        "serial_num": "25544",
    }
)