from modules.akuisisi_data import get_data
from modules.converter_rdf import convert_to_rdf


def main():
    print("1. Mengambil data dari dataset publik REST Countries API...")
    data = get_data()

    print("2. Mengubah data JSON menjadi RDF/Turtle...")
    ttl_file = convert_to_rdf(data)

    print("3. Pipeline selesai.")
    print(f"   File JSON: data/countries.json")
    print(f"   File TTL : {ttl_file}")
    print("4. Upload file output/countries.ttl ke Apache Jena Fuseki.")


if __name__ == "__main__":
    main()