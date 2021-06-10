from pathlib import Path
import httpx

profile_uris = {
    "https://w3id.org/profile/vocpub": {
        "id": "vocpub",
        "modified": "2020-06-15",
    },
    "https://linked.data.gov.au/def/agop": {
        "id": "agop",
        "modified": "2021-03-17",
    },
    "https://linked.data.gov.au/def/loci-dp": {
        "id": "loci-dp",
        "modified": "2021-04-03",
    },
    "https://w3id.org/profile/ogcldapi": {
        "id": "ogcldapi",
        "modified": "2021-06-10",
    },
    "https://linked.data.gov.au/def/fsdf/dp": {
        "id": "fsdf-dp",
        "modified": "2021-06-10",
    },
}

items_folder = Path(__file__).parent.parent / "data" / "items"


def get_profile_rdf():
    for k, v in profile_uris.items():
        r = httpx.get(k, headers={"Accept": "text/turtle"})
        if 200 <= r.status_code < 300:
            Path(items_folder / f"{v['id']}").mkdir(parents=True, exist_ok=False)
            open(items_folder / f"{v['id']}" / f"{v['id']}.ttl", "w").write(r.text)
            print(f"got {v['id']}")
        else:
            print(f"failed getting {v['id']}")


def get_profile_validators():
    pass


if __name__ == "__main__":
    get_profile_rdf()
