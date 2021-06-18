from pathlib import Path
import httpx
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

items_folder = Path(__file__).parent.parent / "data" / "items"
system_folder = Path(__file__).parent.parent / "data" / "system"


def _bind_namespaces(g: Graph, namespaces: dict) -> None:
    for prefix, ns in namespaces.items():
        g.bind(prefix, ns)


def get_profile_rdf():
    print("Getting profiles' RDF:")
    successful_retrievals = []
    for k, v in profile_uris.items():
        r = httpx.get(k, headers={"Accept": "text/turtle"})
        if 200 <= r.status_code < 300:
            Path(items_folder / f"{v['id']}").mkdir(parents=True, exist_ok=True)
            open(items_folder / f"{v['id']}" / f"{v['id']}.ttl", "w").write(r.text)
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
        g = Graph().parse(items_folder / id / f"{id}.ttl")
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
                r = httpx.get(res["a"], headers={"Accept": "text/turtle"})
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
    g.parse(system_folder / "catalogue.ttl")
    q = """
        CONSTRUCT {
            ?p a dcat:Resource .

            ?p dcat:distribution ?r .
            ?r a dcat:Distribution ;
               dcterms:title ?role_title_up ;
               dcat:accessURL ?access_uri ;
               dcterms:format ?f ;
               dcterms:conformsTo ?ct .
               
            ?c dcterms:hasPart ?p .
            ?p dcterms:isPartOf ?c .
        }
        WHERE {
            ?c a dcat:Catalog .
        
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


if __name__ == "__main__":
    # successful_retrievals = get_profile_rdf()
    # get_profile_validators(successful_retrievals)
    successful_retrievals = [
        "https://linked.data.gov.au/def/agop",
        "https://linked.data.gov.au/def/fsdf/dp",
        "https://linked.data.gov.au/def/loci-dp",
        "https://w3id.org/profile/ogcldapi",
        "https://w3id.org/profile/profcat",
        "https://w3id.org/profile/vocpub"
    ]
    make_dcat_items(successful_retrievals)
