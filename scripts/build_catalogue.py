from os.path import *
from pathlib import Path
from rdflib import Graph, URIRef
from rdflib.namespace import DCAT, DCTERMS, RDF, SKOS, PROF

APP_DIR = dirname(dirname(realpath(__file__)))
PROFILES_DIR = join(APP_DIR, "profiles")


def validate_profile(profile_folder_path):
    pass


def validate_profiles(profiles_folder_path=PROFILES_DIR):
    # call validate_profile() per profile
    # generate some sort of log
    pass


if __name__ == "__main__":
    # 1. validate all loaded profiles
    # 2. generate catalogue from valid profiles
    # 3. load profiles & catalogue to DB
    cat = Graph()
    cat.bind("dcterms", DCTERMS)
    cat.bind("w3idcat", "https://w3id.org/profile/")
    cat.bind("audef", "https://linked.data.gov.au/def/")
    cat.parse(join(APP_DIR, "catalogue-start.ttl"), format="turtle")

    shared_properties = [
        DCTERMS.title,
        DCTERMS.description,
        DCTERMS.contributor,
        DCTERMS.created,
        DCTERMS.creator,
        DCTERMS.modified,
        DCTERMS.publisher,
    ]

    # testing
    for path in Path(PROFILES_DIR).rglob('profile.ttl'):
        g = Graph().parse(str(path), format="turtle")
        for s in g.subjects(predicate=RDF.type, object=PROF.Profile):
            cat.add((URIRef("https://w3id.org/profile/"), DCTERMS.hasPart, s))
            cat.add((URIRef(s), RDF.type, DCAT.Resource))
            for p, o in g.predicate_objects(subject=s):
                if p in shared_properties:
                    cat.add((s, p, o))

    print(cat.serialize(format="turtle").decode())
