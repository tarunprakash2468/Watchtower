import os
from datetime import datetime
from typing import List, Dict, Any

import argparse
import pandas as pd
import questionary
import requests
import urllib3
import time
from dotenv import load_dotenv
from nominal.core import NominalClient

PLACEHOLDERS = {
    'basicAuth': 'YOUR_BASIC_AUTH',
    'nom_key': 'YOUR_NOMINAL_KEY',
    'n2yo_key': 'YOUR_N2YO_KEY',
}


# --- CONFIGURATION ---
def load_env_variables() -> tuple[str, str, str]:
    load_dotenv()
    basic_auth = os.getenv('basicAuth')
    nom_key = os.getenv('nom_key')
    n2yo_key = os.getenv('n2yo_key')

    secrets = {
        'basicAuth': basic_auth,
        'nom_key': nom_key,
        'n2yo_key': n2yo_key,
    }

    if not all(secrets.values()):
        raise ValueError("Secrets are not set in environment variables")

    for key, value in secrets.items():
        if value == PLACEHOLDERS.get(key):
            raise ValueError(f"Environment variable {key} is using a placeholder value")

    return basic_auth, nom_key, n2yo_key


def get_valid_date(prompt_label: str) -> datetime:
    while True:
        date_str = input(f"Enter {prompt_label} (ISO 8601, e.g. 2025-07-03T18:30:00.000000Z): ")
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            print("Invalid date format. Please use ISO 8601 format.")


def select_udl_api() -> str:
    return questionary.select(
        "Which UDL API should be used?",
        choices=[
            questionary.Choice(title="Rest API                  — recent data (30–365 days)", value="Rest API"),
            questionary.Choice(title="History Rest API          — archived time series (30+ days)", value="History Rest API"),
            questionary.Choice(title="Bulk Data Request API     — large async downloads (CSV/JSON)", value="Bulk Data Request API"),
            questionary.Choice(title="Secure Messaging API      — real-time streaming (restricted)", value="Secure Messaging API"),
        ]
    ).ask()


def build_udl_url(api: str, sat_no: str, start: str, end: str) -> str:
    base = "https://unifieddatalibrary.com"
    match api:
        case "Rest API":
            return f"{base}/udl/statevector?epoch={start}..{end}&satNo={sat_no}"
        case "History Rest API":
            return f"{base}/udl/statevector/history?epoch={start}..{end}&satNo={sat_no}"
        case "Bulk Data Request API":
            return f"{base}/udl/statevector/history/aodr?epoch={start}..{end}&satNo={sat_no}&outputFormat=JSON"
        case _:
            raise ValueError("Unsupported API or restricted access")


def fetch_udl_data(url: str, auth: str) -> List[Dict[str, Any]]:
    response = requests.get(url, headers={'Authorization': auth}, verify=False)
    if response.status_code != 200:
        raise RuntimeError(f"UDL request failed ({response.status_code}): {response.text}")
    return response.json()


def parse_statevector(data: List[Dict[str, Any]]) -> pd.DataFrame:
    parsed: List[Dict[str, float | str]] = []
    for entry in data:
        try:
            parsed.append({
                'timestamp': entry['epoch'],
                'pos.x': entry['xpos'],
                'pos.y': entry['ypos'],
                'pos.z': entry['zpos'],
                'vel.x': entry['xvel'],
                'vel.y': entry['yvel'],
                'vel.z': entry['zvel'],
            })
        except KeyError as e:
            print(f"Skipping entry due to missing key: {e}")
    return pd.DataFrame(parsed)


def fetch_satellite_name(sat_no: str, n2yo_key: str) -> str:
    url = f"https://api.n2yo.com/rest/v1/satellite/tle/{sat_no}&apiKey={n2yo_key}"
    response = requests.get(url)
    return response.json()["info"]["satname"]


def upload_to_nominal(client: NominalClient, satellite_name: str, sat_no: str, start: str, end: str, df: pd.DataFrame):
    filename = f"data/satellite_{sat_no}_data.csv"
    df.to_csv(filename, index=False)

    asset = client.create_asset(name=satellite_name, properties={"platform": "satellite", "serial_num": sat_no})
    dataset = client.create_dataset(
        name="State Vectors",
        properties={"platform": "satellite", "serial_num": sat_no},
        description=f"All state vectors generated between {start} and {end}",
        prefix_tree_delimiter="."
    )
    dataset.add_tabular_data(path=filename, timestamp_column="timestamp", timestamp_type="iso_8601")
    asset.add_dataset("state_vectors", dataset)

    client.create_run(
        name=f"Historical Data between {start} and {end}",
        start=datetime.fromisoformat(start.replace("Z", "")),
        end=datetime.fromisoformat(end.replace("Z", "")),
        properties={"platform": "satellite", "serial_num": sat_no},
        asset=asset,
        description=f"All state vectors generated between {start} and {end}"
    )


def stream_secure_messaging_to_nominal(
    client: NominalClient,
    auth: str,
    topic: str,
    asset_name: str,
    *,
    max_messages: int = 10,
    sample_period: float = 0.34,
    send_to_connect: bool = False,
) -> None:
    """Stream real-time UDL data to Nominal Core and optionally Connect."""

    session = requests.Session()
    session.headers.update({"Authorization": auth})

    last_offset_url = f"https://unifieddatalibrary.com/sm/getLatestOffset/{topic}/"
    get_url_root = f"https://unifieddatalibrary.com/sm/getMessages/{topic}/"

    last_offset = int(session.get(last_offset_url, verify=False).text)

    asset = client.create_asset(name=asset_name, properties={"topic": topic})
    dataset = client.create_dataset(
        name=f"{topic} Stream",
        description=f"Live data from {topic}",
        prefix_tree_delimiter=".",
    )
    asset.add_dataset("stream", dataset)

    connect_client = None
    if send_to_connect:
        try:
            import connect_python
            connect_client = connect_python.Client()
            connect_client.clear_stream("statevector")
        except Exception as exc:  # pragma: no cover - optional dependency
            print(f"Failed to initialise Connect client: {exc}")

    processed = 0
    with dataset.get_write_stream(batch_size=1) as stream:
        while processed < max_messages:
            response = session.get(get_url_root + str(last_offset), verify=False)
            response.raise_for_status()
            messages = response.json()
            for msg in messages:
                ts = msg["epoch"]
                stream.enqueue("pos.x", ts, msg["xpos"])
                stream.enqueue("pos.y", ts, msg["ypos"])
                stream.enqueue("pos.z", ts, msg["zpos"])
                stream.enqueue("vel.x", ts, msg["xvel"])
                stream.enqueue("vel.y", ts, msg["yvel"])
                stream.enqueue("vel.z", ts, msg["zvel"])
                if connect_client:
                    connect_client.stream(
                        "statevector",
                        ts,
                        names=["x", "y", "z", "vx", "vy", "vz"],
                        values=[
                            msg["xpos"],
                            msg["ypos"],
                            msg["zpos"],
                            msg["xvel"],
                            msg["yvel"],
                            msg["zvel"],
                        ],
                    )
                processed += 1
                if processed >= max_messages:
                    break
            last_offset = int(response.headers.get("KAFKA_NEXT_OFFSET") or last_offset)
            if processed < max_messages:
                time.sleep(sample_period)


# --- CLI & MAIN ENTRY POINT ---
def parse_cli_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch UDL telemetry and upload to Nominal")
    parser.add_argument("--sat-no", help="Satellite number (e.g. 25544 for ISS)")
    parser.add_argument("--api", choices=[
        "Rest API",
        "History Rest API",
        "Bulk Data Request API",
        "Secure Messaging API",
    ], help="UDL API to use")
    parser.add_argument("--start", help="Start datetime in ISO 8601 format")
    parser.add_argument("--end", help="End datetime in ISO 8601 format")
    parser.add_argument("--topic", help="Secure messaging topic (for Secure Messaging API)")
    parser.add_argument("--connect", action="store_true", help="Also stream data to Nominal Connect")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    args = parse_cli_args(argv)

    basic_auth, nom_key, n2yo_key = load_env_variables()
    client = NominalClient.from_token(nom_key)

    sat_no = args.sat_no or input("Enter the satellite number (e.g. 25544 for ISS): ")
    api = args.api or select_udl_api()
    if api == "Secure Messaging API":
        topic = args.topic or input("Enter Secure Messaging topic (e.g. statevector): ")
        stream_secure_messaging_to_nominal(
            client,
            basic_auth,
            topic,
            sat_no,
            send_to_connect=args.connect,
        )
        return

    if args.start:
        start_dt = datetime.fromisoformat(args.start.replace("Z", ""))
    else:
        start_dt = get_valid_date("start date & time")
    if args.end:
        end_dt = datetime.fromisoformat(args.end.replace("Z", ""))
    else:
        end_dt = get_valid_date("end date & time")
    start = start_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end = end_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    url = build_udl_url(api, sat_no, start, end)
    data = fetch_udl_data(url, basic_auth)
    df = parse_statevector(data)

    sat_name = fetch_satellite_name(sat_no, n2yo_key)
    upload_to_nominal(client, sat_name, sat_no, start, end, df)


if __name__ == "__main__":
    main()  # pragma: no cover
