import json
from pathlib import Path

import requests


API_URL = "https://restcountries.com/v3.1/all?fields=name,cca3,capital,region,subregion,population,area,languages,currencies,flags"
LIMIT_DATA = 25


def normalize_country(item):
    name = item.get("name", {})
    capital = item.get("capital") or []
    languages = item.get("languages") or {}
    currencies = item.get("currencies") or {}

    return {
        "id": item.get("cca3", ""),
        "nama": name.get("common", ""),
        "nama_resmi": name.get("official", ""),
        "ibukota": capital[0] if capital else "",
        "region": item.get("region", ""),
        "subregion": item.get("subregion", ""),
        "populasi": item.get("population", 0),
        "languages": [
            {
                "kode": kode,
                "nama": nama
            }
            for kode, nama in languages.items()
        ],
        "currencies": [
            {
                "kode": kode,
                "nama": detail.get("name", ""),
                "simbol": detail.get("symbol", "")
            }
            for kode, detail in currencies.items()
        ]
    }


def get_data():
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    raw_data = response.json()

    countries = []
    for item in raw_data:
        if item.get("cca3"):
            countries.append(normalize_country(item))

    countries = sorted(countries, key=lambda x: x["nama"])[:LIMIT_DATA]

    output_path = Path(__file__).resolve().parent.parent / "data" / "countries.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(countries, file, indent=2, ensure_ascii=False)

    print(f"Data berhasil disimpan ke {output_path}")
    print(f"Jumlah entitas utama: {len(countries)} negara")

    return countries