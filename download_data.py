from pathlib import Path
import pandas as pd
import requests

# Khởi tạo thư mục lưu trữ
output_dir = Path("data/by_station")
output_dir.mkdir(parents=True, exist_ok=True)

# Đọc file danh sách trạm chuẩn từ NOAA
stations_url = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"

# Cấu hình vị trí cột theo tài liệu kỹ thuật GHCN-Daily
col_specs = [(0, 11), (12, 20), (21, 30), (38, 40)]
col_names = ["id", "lat", "lon", "state"]

df_stations = pd.read_fwf(stations_url, colspecs=col_specs, names=col_names)

# Lọc các trạm thuộc bang Texas (state == 'TX')
texas_stations = df_stations[df_stations["state"].str.strip() == "TX"][
    "id"
].tolist()
print(f"Tong so tram tai Texas can tai: {len(texas_stations)}")

# Tải file CSV từng trạm từ AWS S3 Open Data bucket
base_s3_url = "https://noaa-ghcn-pds.s3.amazonaws.com/csv/by_station/"

# Có thể giới hạn số lượng mẫu (ví dụ: 100 trạm đầu tiên) cho việc test nhanh
for station_id in texas_stations[:100]:
    file_url = f"{base_s3_url}{station_id}.csv"
    out_path = output_dir / f"{station_id}.csv"

    if not out_path.exists():
        try:
            response = requests.get(file_url, timeout=10)
            if response.status_code == 200:
                out_path.write_bytes(response.content)
            else:
                print(f"Bo qua tram {station_id} (Ma loi: {response.status_code})")
        except Exception as e:
            print(f"Loi ket noi khi tai tram {station_id}: {e}")

print("Hoan tat qua trinh tai du lieu tram Texas!")