from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(
    title="REST API Semantic Web Negara",
    description="API untuk mengambil data negara dari GraphDB menggunakan SPARQL",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint repository GraphDB
SPARQL_ENDPOINT = "http://localhost:7200/repositories/countries"

PREFIX = """
PREFIX country: <https://tia-prastika.dev/countries#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""


def run_sparql_query(query: str):
    """Mengirim query SPARQL ke GraphDB dan mengembalikan hasil JSON."""
    try:
        response = requests.get(
            SPARQL_ENDPOINT,
            params={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=15
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Gagal mengambil data dari GraphDB: {response.text}"
            )

        return response.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Tidak bisa terhubung ke GraphDB: {str(e)}"
        )


def binding_value(item: dict, key: str, default: str = ""):
    return item.get(key, {}).get("value", default)


@app.get("/")
def home():
    return {
        "message": "REST API Semantic Web Negara berhasil berjalan",
        "graph_database": "GraphDB",
        "repository": "countries",
        "sparql_endpoint": SPARQL_ENDPOINT,
        "endpoints": [
            "/data",
            "/search?keyword=Asia",
            "/entity/AFG",
            "/api/triples",
            "/docs"
        ]
    }


@app.get("/data")
def get_all_countries():
    """Menampilkan data negara secara terstruktur."""
    query = PREFIX + """
    SELECT ?kode ?nama ?namaResmi ?ibukota ?populasi ?region
           (GROUP_CONCAT(DISTINCT ?bahasa; separator=", ") AS ?languages)
           (GROUP_CONCAT(DISTINCT ?mataUang; separator=", ") AS ?currencies)
    WHERE {
        ?negara a country:Country ;
                country:countryCode ?kode ;
                country:countryName ?nama .

        OPTIONAL { ?negara country:officialName ?namaResmi . }
        OPTIONAL { ?negara country:capital ?ibukota . }
        OPTIONAL { ?negara country:population ?populasi . }

        OPTIONAL {
            ?negara country:locatedInRegion ?regionUri .
            ?regionUri rdfs:label ?region .
        }

        OPTIONAL {
            ?negara country:hasLanguage ?languageUri .
            ?languageUri rdfs:label ?bahasa .
        }

        OPTIONAL {
            ?negara country:usesCurrency ?currencyUri .
            ?currencyUri rdfs:label ?mataUang .
        }
    }
    GROUP BY ?kode ?nama ?namaResmi ?ibukota ?populasi ?region
    ORDER BY ?nama
    """

    result = run_sparql_query(query)

    data = []
    for item in result["results"]["bindings"]:
        data.append({
            "kode": binding_value(item, "kode"),
            "nama": binding_value(item, "nama"),
            "nama_resmi": binding_value(item, "namaResmi"),
            "ibukota": binding_value(item, "ibukota"),
            "populasi": binding_value(item, "populasi"),
            "region": binding_value(item, "region"),
            "languages": binding_value(item, "languages"),
            "currencies": binding_value(item, "currencies"),
        })

    return {
        "status": "success",
        "total": len(data),
        "data": data
    }


@app.get("/search")
def search_data(keyword: str = Query(..., description="Kata kunci pencarian")):
    """Mencari data RDF berdasarkan keyword pada subject, predicate, atau object."""
    safe_keyword = keyword.replace('"', '\\"')

    query = PREFIX + f"""
    SELECT ?subject ?predicate ?object
    WHERE {{
        ?subject ?predicate ?object .
        FILTER (
            regex(str(?subject), "{safe_keyword}", "i") ||
            regex(str(?predicate), "{safe_keyword}", "i") ||
            regex(str(?object), "{safe_keyword}", "i")
        )
    }}
    LIMIT 100
    """

    result = run_sparql_query(query)

    data = []
    for item in result["results"]["bindings"]:
        data.append({
            "subject": binding_value(item, "subject"),
            "predicate": binding_value(item, "predicate"),
            "object": binding_value(item, "object"),
        })

    return {
        "status": "success",
        "keyword": keyword,
        "total": len(data),
        "data": data
    }


@app.get("/entity/{id}")
def get_entity_by_id(id: str):
    """Menampilkan detail satu entitas negara berdasarkan kode negara, misalnya AFG, AUS, BTN."""
    safe_id = id.upper().replace(" ", "_")

    query = PREFIX + f"""
    SELECT ?predicate ?object
    WHERE {{
        country:{safe_id} ?predicate ?object .
    }}
    ORDER BY ?predicate
    """

    result = run_sparql_query(query)

    data = []
    for item in result["results"]["bindings"]:
        data.append({
            "predicate": binding_value(item, "predicate"),
            "object": binding_value(item, "object"),
        })

    return {
        "status": "success",
        "id": safe_id,
        "total": len(data),
        "data": data
    }


@app.get("/api/triples")
def get_all_triples():
    """Menampilkan seluruh RDF triple dalam bentuk subject, predicate, object."""
    query = PREFIX + """
    SELECT ?subject ?predicate ?object
    WHERE {
        ?subject ?predicate ?object .
    }
    LIMIT 100
    """

    result = run_sparql_query(query)

    data = []
    for item in result["results"]["bindings"]:
        data.append({
            "subject": binding_value(item, "subject"),
            "predicate": binding_value(item, "predicate"),
            "object": binding_value(item, "object"),
        })

    return {
        "status": "success",
        "total": len(data),
        "data": data
    }