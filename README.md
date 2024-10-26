# entsoe-data-downloader
Script to scrape and download open data from www.entsoe.eu/data/transparency-platform


# How to run?

1. Install `uv`
    * https://docs.astral.sh/uv/getting-started/installation/#installing-uv
2. Run
    ```sh
    uv run --with requests --with bs4 entsoe-download-csv.py
    ```