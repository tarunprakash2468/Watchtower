# 🛰️ Watchtower

**Watchtower** is a Python toolchain for ingesting satellite telemetry (state vector) data from the [Unified Data Library (UDL)](https://unifieddatalibrary.com), processing it locally, and integrating it with the [Nominal](https://docs.nominal.io) test data platform.

## 🚀 Features

- 🔐 Authenticates with UDL using a Base64 token
- 📡 Pulls state vector data for specified satellites (`satNo`)
- 📁 Exports clean telemetry as `.csv`
- 🔗 Integrates with Nominal by preparing data for test runs
- 📅 Automatically handles UTC timestamps and historical data

## 🛠️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/watchtower.git
cd watchtower
```

### 2. Install the CLI

Install the package in editable mode so the `watchtower` command is available:

```bash
pip install -e .
```
### 3. Install development dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

You’ll need:

- A UDL Base64 token
- A N2YO API key
- Nominal API credentials

Set these as environment variables in a `.env` file or export them manually.

---

## 🛰️ Pulling and Processing State Vector Data

The main script for data ingestion and processing is:

```python
python core/import_udl_to_nominal.py
```

This script pulls historical state vector data for a given satellite over a specified time window from UDL and saves it to a CSV file in the `data/` directory (e.g., `satellite_25544_data.csv`).

You can configure:

- `satellite_number` (e.g., `25544` for ISS)
- Time window (default: past 7 days)
- UDL endpoint and filters

---

## 📂 Project Structure

```
core/
├── import_udl_to_nominal.py      # Main script: pulls UDL data and prepares for Nominal
data/                             # Output CSV with parsed telemetry
├── satellite_25544_data.csv      
├── satellite_25545_data.csv
├── satellite_46826_data.csv
```

---

## 📘 Resources

- [Unified Data Library API Docs](https://unifieddatalibrary.com/storefront)
- [Nominal Developer Docs](https://docs.nominal.io)
- [Satellite Catalog Numbers (SATNO)](https://www.n2yo.com/satellites/)

---

## 🧑‍💻 Author

Tarun Prakash — [@tarunprakash2468](https://github.com/tarunprakash2468)

Built for satellite telemetry test workflows and backend integration with Nominal.

---

## 🛡️ License

MIT License
