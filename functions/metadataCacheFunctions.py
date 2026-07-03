import hashlib
import json

from library.app import METADATA_PROVIDER, ORGANIZATION_MODE


def metadataCacheContext() -> str:
    return f"{ORGANIZATION_MODE}:{METADATA_PROVIDER}"


def metadataCacheKey(download_type, item_id, file_id, file_size, file_name) -> str:
    key_data = {
        "type": download_type,
        "item_id": item_id,
        "file_id": file_id,
        "file_size": file_size,
        "file_name": file_name,
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.sha256(key_str.encode()).hexdigest()


def metadataCacheKeyFromRecord(record: dict) -> str:
    return metadataCacheKey(
        record.get("type"),
        record.get("item_id"),
        record.get("file_id"),
        record.get("file_size"),
        record.get("file_name"),
    )


def metadataFields(record: dict) -> dict:
    fields = {
        key: value
        for key, value in record.items()
        if key.startswith("metadata_")
    }
    fields["metadata_cache_context"] = metadataCacheContext()
    return fields


def buildMetadataCache(records: list[dict] | None) -> dict[str, dict]:
    cache = {}
    for record in records or []:
        if record.get("metadata_cache_context") != metadataCacheContext():
            continue

        cache[metadataCacheKeyFromRecord(record)] = metadataFields(record)

    return cache
