import pandas as pd
from pathlib import Path
import requests

# Tạo thư mục lưu trữ nếu chưa có
output_dir = Path("data/by_station")
output_dir.mkdir(parents=True, exist_ok=True)
Path("data/raw").mkdir(parents=True, exist_ok=True)

# Tải các file metadata gốc của NOAA nếu chưa có
stations_url = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
inventory_url = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt"

def download_file(url, dest):
    if not dest.exists():
        print(f"Dang tai {url}...")
        r = requests.get(url)
        dest.write_bytes(r.content)

download_file(stations_url, Path("data/raw/ghcnd-stations.txt"))
download_file(inventory_url, Path("data/raw/ghcnd-inventory.txt"))

# Đọc file trạm và inventory
col_specs_st = [(0,11), (12,20), (21,30), (38,68)]
df_stations = pd.read_fwf("data/raw/ghcnd-stations.txt", colspecs=col_specs_st, names=['STATION','LAT','LON','NAME'])

col_specs_inv = [(0,11), (31,35), (36,40), (41,45)]
df_inv = pd.read_fwf("data/raw/ghcnd-inventory.txt", colspecs=col_specs_inv, names=['STATION','ELEMENT','FIRST','LAST'])

# Lọc các trạm ở Texas có chứa TMAX
tx_stations = df_stations[df_stations.STATION.str.startswith('USC') | df_stations.STATION.str.startswith('USW') | df_stations.STATION.str.startswith('US1')]
good_tmax = df_inv[(df_inv.ELEMENT == 'TMAX') & (df_inv.FIRST <= 1990) & (df_inv.LAST >= 2024)].STATION

selected_stations = tx_stations[tx_stations.STATION.isin(good_tmax)]['STATION'].tolist()

print(f"Tong so tram TMAX hop le tai Texas can tai: {len(selected_stations)}")

# Tải file CSV từng trạm từ AWS S3 (giới hạn 100 trạm đầu tiên để test nhanh)
base_s3_url = "https://noaa-ghcn-pds.s3.amazonaws.com/csv/by_station/"

for station_id in selected_stations[:100]:
    file_url = f"{base_s3_url}{station_id}.csv"
    out_path = output_dir / f"{station_id}.csv"
    
    if not out_path.exists():
        try:
            response = requests.get(file_url, timeout=10)
            if response.status_code == 200:
                out_path.write_bytes(response.content)
                print(f"Da tai thanh cong: {station_id}")
            else:
                print(f"Bo qua tram {station_id} (Ma loi: {response.status_code})")
        except Exception as e:
            print(f"Loi ket noi khi tai tram {station_id}: {e}")

print("Hoan tat qua trinh tai du lieu tram TMAX Texas!")