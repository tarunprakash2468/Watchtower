# 🛰️ Watchtower

**Watchtower** is a Python toolchain for ingesting satellite telemetry (state vector) data from the [Unified Data Library (UDL)](https://unifieddatalibrary.com), processing it locally, and integrating it with the [Nominal](https://docs.nominal.io) test data platform.

## 🚀 Features

- 🔐 Authenticates with UDL using a Base64 token
- 📡 Pulls state vector data for specified satellites (`satNo`)
- 📁 Exports clean telemetry as `.csv`
- 🔗 Creates corresponding "Runs" in Nominal, linked to digital "Assets"
- 📅 Automatically handles UTC timestamps and historical data

## 🛠️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/watchtower.git
cd watchtower
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file or configure manually

You’ll need:

- A UDL Base64 token
- A valid satellite catalog number (`satNo`)
- Nominal API credentials (set up via `nom` CLI or SDK)

---

## 🛰️ Pulling State Vector Data

```python
python core/query_data.py
```

This script pulls historical state vector data for a given satellite over a specified time window and saves it to `satellite_data.csv`.

You can configure:

- `satellite_number = 25544`  # ISS example
- `now` and `yesterday` time window (default is past 7 days or longer)
- UDL endpoint + filters: `epoch=...&satNo=...`

---

## 🔗 Creating a Run in Nominal

After generating data:

```python
python core/upload_to_nominal.py
```

This script:

- Retrieves the asset in Nominal matching `platform` + `serial_num`
- Creates a new run using timestamps from the dataset
- Attaches metadata and links the run to the asset

---

## 📂 Project Structure

```
core/
├── query_data.py         # Pull UDL state vector data and save as CSV
├── upload_to_nominal.py  # Create asset/run in Nominal with timestamps
data/
└── satellite_data.csv    # Output CSV with parsed telemetry
```

---

## ✅ Example Output

```
Data saved to 'satellite_data.csv'
Created run in Nominal: "ISS Historical Pass 2024-07-01 to 2024-07-02"
```

---

## 🧠 Notes

- UDL API uses HTTPS with a token-based Basic Auth scheme
- Nominal SDK requires the asset to exist or be created beforehand
- All times are handled in UTC with `datetime.timezone.utc`

---

## 📘 Resources

- [Unified Data Library API Docs](https://unifieddatalibrary.com/storefront)
- [Nominal Developer Docs](https://docs.nominal.io)
- [Satellite Catalog Numbers (SATNO)](https://www.n2yo.com/satellites/)

---

## 🧑‍💻 Author

Tarun Prakash — [@tarun_prakash](https://github.com/tarunprakash)

Built for satellite telemetry test workflows and backend integration with Nominal.

---

## 🛡️ License

MIT License
