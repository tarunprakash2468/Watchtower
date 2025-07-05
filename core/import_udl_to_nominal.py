import os, pandas as pd, questionary, requests, sys, urllib3
from datetime import datetime
from dotenv import load_dotenv
from nominal.core import NominalClient
from typing import List, Dict, Any


# --- CONFIGURATION ---
def load_env_variables() -> tuple[str, str, str]:
    load_dotenv()
    basic_auth = os.getenv('basicAuth')
    nom_key = os.getenv('nom_key')
    n2yo_key = os.getenv('n2yo_key')
    if not (basic_auth and nom_key and n2yo_key):
        raise ValueError("Secrets are not set in environment variables")
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


# --- MAIN ENTRY POINT ---
def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    basic_auth, nom_key, n2yo_key = load_env_variables()
    client = NominalClient.from_token(nom_key)

    sat_no = input("Enter the satellite number (e.g. 25544 for ISS): ")
    api = select_udl_api()
    if api == "Secure Messaging API":
        print("Secure Messaging API requires access request. Contact UDL support.")
        sys.exit(1)

    start_dt = get_valid_date("start date & time")
    end_dt = get_valid_date("end date & time")
    start = start_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end = end_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    url = build_udl_url(api, sat_no, start, end)
    data = fetch_udl_data(url, basic_auth)
    df = parse_statevector(data)

    sat_name = fetch_satellite_name(sat_no, n2yo_key)
    upload_to_nominal(client, sat_name, sat_no, start, end, df)


if __name__ == "__main__":
    main()