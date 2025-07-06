# Pipeline Instructions

This document describes how to run the full Watchtower pipeline.

1. Ensure you have all necessary API credentials:
   - `basicAuth` for UDL
   - `nom_key` for Nominal
   - `n2yo_key` for N2YO

2. Install dependencies:
   ```bash
   pip install -e .
   pip install -r requirements/dev.txt
   ```

3. Run the ingestion script:
   ```bash
   python core/import_udl_to_nominal.py --sat-no 25544 --api "Rest API" \
       --start 2025-07-05T00:00:00.000Z --end 2025-07-05T01:00:00.000Z
   ```

This will download state vector data from UDL and upload it to Nominal.
