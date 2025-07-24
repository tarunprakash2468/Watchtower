import os
import time
import math
import requests
import urllib3
import connect_python


def _xyz_to_lla(x: float, y: float, z: float) -> tuple[float, float, float]:
    r = math.sqrt(x * x + y * y + z * z)
    lat = math.degrees(math.asin(z / r))
    lon = math.degrees(math.atan2(y, x))
    altitude = r - 6_378_000.0
    return lat, lon, altitude


@connect_python.main
def stream_data(client: connect_python.Client):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    client.clear_stream("statevector")

    auth = os.getenv("basicAuth") or client.get_value("basic_auth")
    topic = client.get_value("topic") or "statevector"
    sample_period = float(client.get_value("sample_period") or 0.34)

    session = requests.Session()
    session.headers.update({"Authorization": auth})

    last_offset_url = f"https://unifieddatalibrary.com/sm/getLatestOffset/{topic}/"
    get_url_root = f"https://unifieddatalibrary.com/sm/getMessages/{topic}/"

    last_offset = int(session.get(last_offset_url, verify=False).text)

    while True:
        resp = session.get(get_url_root + str(last_offset), verify=False)
        resp.raise_for_status()
        messages = resp.json()
        for msg in messages:
            lat, lon, alt = _xyz_to_lla(msg["xpos"], msg["ypos"], msg["zpos"])
            client.stream(
                "statevector",
                msg["epoch"],
                names=["latitude", "longitude", "altitude", "pitch", "roll", "heading"],
                values=[lat, lon, alt, 0, 0, 0],
            )
        last_offset = int(resp.headers.get("KAFKA_NEXT_OFFSET") or last_offset)
        time.sleep(sample_period)


if __name__ == "__main__":
    stream_data()
