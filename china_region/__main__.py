import json
import requests
import pandas as pd
import sys


def fetch_data(adcode):
    url = f"https://restapi.amap.com/v3/config/district?key={api_key}&keywords={adcode}&subdistrict=0"
    response = requests.get(url)
    data = json.loads(response.text)
    if data["status"] == '0':
        raise Exception(f"fetch error {data["info"]}")
    district = data["districts"][0]
    return {
        "value": district["adcode"],
        "center": district["center"],
        "label": district["name"],
    }


if __name__ == "__main__":

    api_key = sys.argv[len(sys.argv) - 1]

    df = pd.read_excel("assets/amap_adcode.xlsx")
    # 排除第一条和最后一条数据
    df = df.drop(index=0)
    df = df.drop(df.index[-1])
    # 过滤省份数据
    province_df = df[df["adcode"].astype(str).str.endswith("0000")]
    provinces = []
    for _, province_row in province_df.iterrows():
        province_code = province_row["adcode"]
        province = fetch_data(province_code)
        # 过滤城市数据
        city_df = df[
            (df["adcode"].astype(str).str.startswith(str(int(province_code / 10000))))
            & (df["adcode"].astype(str).str.endswith("00"))
            & (df["adcode"].astype(str) != str(province_code))
            ]
        cities = []
        for _, city_row in city_df.iterrows():
            city_code = city_row["adcode"]
            city = fetch_data(city_code)
            cities.append(city)

        province["children"] = cities
        provinces.append(province)

    with open("assets/output.json", "w", encoding="utf-8") as f:
        json.dump(provinces, f, ensure_ascii=False)
