from pathlib import Path
import sys
import glob
import httpx
import os
import requests
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, PROF


profile_uris = {
    "https://w3id.org/profile/profcat": {
        "id": "profcat",
    },
    "https://w3id.org/profile/vocpub": {
        "id": "vocpub",
    },
    "https://linked.data.gov.au/def/agop": {
        "id": "agop",
    },
    "https://linked.data.gov.au/def/loci-dp": {
        "id": "loci-dp",
    },
    "https://w3id.org/profile/ogcldapi": {
        "id": "ogcldapi",
    },
    "https://linked.data.gov.au/def/fsdf/dp": {
        "id": "fsdf-dp",
    },
}

namespaces = {
    "dcat": DCAT,
    "dcterms": DCTERMS,
    "prof": PROF,
    "role": Namespace("http://www.w3.org/ns/dx/prof/role/")
}

data_folder = Path(__file__).parent.parent / "data"
items_folder = Path(__file__).parent.parent / "data" / "items"
system_folder = Path(__file__).parent.parent / "data" / "system"

proxies = {
    "https://": f"https://github.com/",
}


def _bind_namespaces(g: Graph, namespaces: dict) -> None:
    for prefix, ns in namespaces.items():
        g.bind(prefix, ns)


def get_profile_rdf():
    print("Getting profiles' RDF:")
    successful_retrievals = []
    for k, v in profile_uris.items():
        print(k)
        r = requests.get(k, headers={"Accept": "text/turtle"})
        if 200 <= r.status_code < 300:
            Path(items_folder / f"{v['id']}").mkdir(parents=True, exist_ok=True)
            open(items_folder / f"{v['id']}" / f"{v['id']}.ttl", "wb").write(r.content)
            print(f"got {v['id']}")
            successful_retrievals.append(k)
        else:
            print(f"failed getting {v['id']}")

    return successful_retrievals


def get_profile_validators(successful_retrievals):
    """
    For each successfully-retreived profile,
    SPARQL query for all the Resources of role 'validator'
    Download, parse and merge all the resources into a graph (g2)
    Serialize that g2 to items/{PROFILE-ID}/validator.ttl
    """
    print("Getting validators:")
    for p in successful_retrievals:
        id = profile_uris[p]["id"]
        print(f"Getting validators for {id}")
        g = Graph().parse(items_folder / id / f"{id}.ttl", format="ttl")
        q = """
            SELECT ?a ?f
            WHERE {
                ?r  prof:hasRole role:validation ;
                    prof:hasArtifact ?a ;
                    dcterms:conformsTo <https://www.w3.org/TR/shacl/> ;
                    dcterms:format ?f ;
                .
            }
            """
        g2 = Graph()
        try:
            for res in g.query(q, initNs=namespaces):
                r = requests.get(res["a"], headers={"Accept": "text/turtle"})
                if 200 <= r.status_code < 300:
                    g2.parse(data=r.text, format="turtle")
                else:
                    print(f"Failed to get validator {res['a']} for {id}")
            open(items_folder / f"{id}" / "validator.ttl", "w").write(g2.serialize())
            print(f"Saved validators for {id}")
        except Exception as e:
            print(f"Failed parsing RDF for validators for {id}")
            print(e)


def make_dcat_items(successful_retrievals):
    """
    For each successfully-retrieved profile,
    CONSTRUCT that it's a dcat:Resource with HTML & RDF distributions at PID URI
    """
    g = Graph()
    for p in successful_retrievals:
        id = profile_uris[p]["id"]
        g.parse(items_folder / id / f"{id}.ttl")
    q = """
        CONSTRUCT {
            ?p a dcat:Resource .

            ?p dcat:distribution ?r .
            ?r a dcat:Distribution ;
               dcterms:title ?role_title_up ;
               dcat:accessURL ?access_uri ;
               dcterms:format ?f ;
               dcterms:conformsTo ?ct .
        }
        WHERE {
            ?p  a prof:Profile .

            OPTIONAL {
                ?p prof:hasResource ?r .

                ?r prof:hasRole ?role ;
                   prof:hasArtifact ?a .
            }
            OPTIONAL {
                ?r                   
                   dcterms:format ?f ;
                   dcterms:conformsTo ?ct .                   
            }
            BIND (STRAFTER(STR(?role), "/role/") AS ?role_title)
            BIND (CONCAT(UCASE(SUBSTR(?role_title, 1, 1)), SUBSTR(?role_title, 2)) AS ?role_title_up)
            BIND (STR(?a) AS ?access_uri)
        }
        """
    x = g.query(q, initNs=namespaces)
    _bind_namespaces(x.graph, namespaces)
    open(system_folder / "items.ttl", "w").write(x.serialize(format="ttl").decode())


def push_data(endpoint, username, password):

    if endpoint is None:
        raise ValueError("You must set the SPARQL_ENDPOINT!")

    print(f"Loading data into {endpoint}")
    print(data_folder)
    # load all turtle files in ./items/* & ./system/*
    for f in glob.glob(f"{data_folder}/**/*.ttl", recursive=True):
        r = httpx.post(
            endpoint,
            params={"graph": "https://original.com"},
            headers={"Content-Type": "text/turtle"},
            content=open(f, "rb").read(),
            auth=(username, password)
        )
        if 200 <= r.status_code < 300:
            print("ok")
        else:
            print(r.status_code)
            print(r.text)

    print("Done")
    return


if __name__ == "__main__":
    successful_retrievals = get_profile_rdf()
    get_profile_validators(successful_retrievals)
    make_dcat_items(successful_retrievals)

    SPARQL_ENDPOINT = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SPARQL_ENDPOINT")
    SPARQL_USERNAME = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SPARQL_USERNAME")
    SPARQL_PASSWORD = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SPARQL_PASSWORD")

    push_data(endpoint=SPARQL_ENDPOINT,
              username=SPARQL_USERNAME,
              password=SPARQL_PASSWORD)
