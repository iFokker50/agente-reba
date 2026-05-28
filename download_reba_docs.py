import os
import requests


REBA_DOCS = [
    {
        "name": "NTP_601_REBA_INSST.pdf",
        "url": "https://www.insst.es/documents/94886/7861730/ntp_601.pdf/2989c14f-2280-4eef-9cb7-f195366352ba?download=true&t=1727418175902&version=1.2"
    }
]


def download_file(url: str, output_path: str):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()

    with open(output_path, "wb") as file:
        file.write(response.content)


def download_reba_docs(folder: str = "reba_docs"):
    os.makedirs(folder, exist_ok=True)

    for doc in REBA_DOCS:
        output_path = os.path.join(folder, doc["name"])

        if os.path.exists(output_path):
            print(f"Ya existe: {output_path}")
            continue

        print(f"Descargando: {doc['name']}")
        download_file(doc["url"], output_path)
        print(f"Guardado en: {output_path}")


if __name__ == "__main__":
    download_reba_docs()