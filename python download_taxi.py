import sys
import gzip
import shutil
import urllib.request
from urllib.error import HTTPError, URLError
from pathlib import Path

URL_PREFIX = "https://d37ci6vzurychx.cloudfront.net/trip-data"


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python download_taxi.py <taxi_type> <year>\n"
                 "Example: python download_taxi.py yellow 2026")

    taxi_type, year = sys.argv[1], sys.argv[2]

    for month in range(1, 13):
        fmonth = f"{month:02d}"                      # zero-pad: 1 -> "01"

        file_name = f"{taxi_type}_tripdata_{year}-{fmonth}.parquet"
        url = f"{URL_PREFIX}/{file_name}"

        local_dir = Path("data/raw") / taxi_type / year / fmonth
        local_path = local_dir / file_name

        print(f"downloading {url} to {local_path}")
        local_dir.mkdir(parents=True, exist_ok=True)   # mkdir -p

        try:
            urllib.request.urlretrieve(url, local_path)
        except (HTTPError, URLError) as e:
            # e.g. 403/404 for months that haven't been published yet
            print(f"  skipped {fmonth}: {e}")
            local_path.unlink(missing_ok=True)         # remove partial file
            continue

        print(f"compressing {local_path}")
        gz_path = local_path.with_name(local_path.name + ".gz")
        with open(local_path, "rb") as f_in, gzip.open(gz_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        local_path.unlink()                            # gzip CLI deletes the original


if __name__ == "__main__":
    main()