# 🛰️ Watchtower

**Watchtower** is a Python toolchain for ingesting satellite telemetry (state vector) data from the [Unified Data Library (UDL)](https://unifieddatalibrary.com), processing it locally, and integrating it with the [Nominal](https://docs.nominal.io) test data platform.

## 🚀 Features

- 🔐 Authenticates with UDL using a Base64 token
- 📡 Pulls state vector data for specified satellites (`satNo`)
- 📁 Exports clean telemetry as `.csv`
- 🔗 Integrates with Nominal by preparing data for test runs
- 📅 Automatically handles UTC timestamps and historical data

## 📦 Installation

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
pip install -r requirements/dev.txt
```

### 4. Configure Environment

You’ll need:

- A UDL Base64 token
- A N2YO API key
- Nominal API credentials

Set these as environment variables in a `.env` file or export them manually.

---

## 🚀 Usage

The main script for data ingestion and processing is:

```bash
python core/import_udl_to_nominal.py [--sat-no 25544] [--api "Rest API"] \
    [--start 2025-07-05T00:00:00.000Z] [--end 2025-07-05T01:00:00.000Z]
```

Running without arguments will prompt for the same values interactively. Using the flags allows non-interactive execution which is useful for automation.

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

## ⚙️ Makefile Commands

The repository includes a `Makefile` with shortcuts for common tasks:

```bash
make install  # install Python dependencies
make lint     # run ruff checks
make test     # run the test suite
make run      # execute the main ingestion script
```

## ✅ Testing

After installing the development dependencies you can run the test suite:

```bash
make test
```

You can also invoke `pytest` directly if preferred:

```bash
pytest
```

## 📦 Packaging and Release

Build distributable artifacts using `python -m build`:

```bash
python -m build
```

This creates a wheel and source distribution under `dist/`. To publish to PyPI run:

```bash
twine upload dist/*
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

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for
details. By participating you agree to follow our
[Code of Conduct](.github/CODE_OF_CONDUCT.md).

---

## 🛡️ License

MIT License
