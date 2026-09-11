import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

client = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.getenv("QDRANT_API_KEY"),
)


def field_paths(value, prefix=""):
    paths = []

    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            paths.extend(field_paths(child, path))
    elif isinstance(value, list):
        if value:
            paths.extend(field_paths(value[0], f"{prefix}[]"))
        else:
            paths.append(prefix)
    else:
        paths.append(prefix)

    return paths


for collection in client.get_collections().collections:
    print(f"\nCOLLECTION: {collection.name}")

    points, _ = client.scroll(
        collection_name=collection.name,
        limit=1,
        with_payload=True,
        with_vectors=False,
    )

    if not points:
        print("  Empty collection")
        continue

    for path in sorted(field_paths(points[0].payload or {})):
        print(f"  {path}")