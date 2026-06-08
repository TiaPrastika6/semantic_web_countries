import re
from pathlib import Path

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD


EX = Namespace("https://tia-prastika.dev/countries#")


def slug(text):
    text = str(text or "").strip()
    text = re.sub(r"[^A-Za-z0-9]+", "_", text)
    return text.strip("_") or "Unknown"


def add_class(g, class_uri, label):
    g.add((class_uri, RDF.type, RDFS.Class))
    g.add((class_uri, RDFS.label, Literal(label, datatype=XSD.string)))


def add_data_property(g, prop, label, domain, range_type):
    g.add((prop, RDF.type, RDF.Property))
    g.add((prop, RDFS.label, Literal(label, datatype=XSD.string)))
    g.add((prop, RDFS.domain, domain))
    g.add((prop, RDFS.range, range_type))


def add_object_property(g, prop, label, domain, range_class):
    g.add((prop, RDF.type, RDF.Property))
    g.add((prop, RDFS.label, Literal(label, datatype=XSD.string)))
    g.add((prop, RDFS.domain, domain))
    g.add((prop, RDFS.range, range_class))


def convert_to_rdf(data):
    g = Graph()
    g.bind("country", EX)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)

    add_class(g, EX.Country, "Country")
    add_class(g, EX.Region, "Region")
    add_class(g, EX.Language, "Language")
    add_class(g, EX.Currency, "Currency")

    add_data_property(g, EX.countryName, "Nama negara", EX.Country, XSD.string)
    add_data_property(g, EX.officialName, "Nama resmi negara", EX.Country, XSD.string)
    add_data_property(g, EX.countryCode, "Kode negara", EX.Country, XSD.string)
    add_data_property(g, EX.capital, "Ibu kota", EX.Country, XSD.string)
    add_data_property(g, EX.population, "Populasi", EX.Country, XSD.integer)
    add_data_property(g, EX.currencyCode, "Kode mata uang", EX.Currency, XSD.string)

    add_object_property(g, EX.locatedInRegion, "Berada di region", EX.Country, EX.Region)
    add_object_property(g, EX.hasLanguage, "Memiliki bahasa", EX.Country, EX.Language)
    add_object_property(g, EX.usesCurrency, "Menggunakan mata uang", EX.Country, EX.Currency)

    for item in data:
        country_uri = EX[item["id"]]

        g.add((country_uri, RDF.type, EX.Country))
        g.add((country_uri, EX.countryName, Literal(item["nama"], datatype=XSD.string)))
        g.add((country_uri, EX.officialName, Literal(item["nama_resmi"], datatype=XSD.string)))
        g.add((country_uri, EX.countryCode, Literal(item["id"], datatype=XSD.string)))
        g.add((country_uri, EX.capital, Literal(item["ibukota"], datatype=XSD.string)))
        g.add((country_uri, EX.population, Literal(item["populasi"], datatype=XSD.integer)))

        region_uri = EX["Region_" + slug(item["region"])]
        g.add((region_uri, RDF.type, EX.Region))
        g.add((region_uri, RDFS.label, Literal(item["region"], datatype=XSD.string)))
        g.add((country_uri, EX.locatedInRegion, region_uri))

        for language in item["languages"]:
            language_uri = EX["Language_" + slug(language["nama"])]
            g.add((language_uri, RDF.type, EX.Language))
            g.add((language_uri, RDFS.label, Literal(language["nama"], datatype=XSD.string)))
            g.add((country_uri, EX.hasLanguage, language_uri))

        for currency in item["currencies"]:
            currency_uri = EX["Currency_" + slug(currency["kode"])]
            g.add((currency_uri, RDF.type, EX.Currency))
            g.add((currency_uri, RDFS.label, Literal(currency["nama"], datatype=XSD.string)))
            g.add((currency_uri, EX.currencyCode, Literal(currency["kode"], datatype=XSD.string)))
            g.add((country_uri, EX.usesCurrency, currency_uri))

    output_path = Path(__file__).resolve().parent.parent / "output" / "countries.ttl"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=str(output_path), format="turtle")

    print(f"File RDF/Turtle berhasil dibuat: {output_path}")
    print(f"Total triple RDF: {len(g)}")

    return output_path