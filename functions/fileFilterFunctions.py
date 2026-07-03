import os
import re

from library.app import INCLUDE_SAMPLE_FILES, SAMPLE_FILE_MAX_BYTES

SAMPLE_NAME_RE = re.compile(r"^samples?(?:\s*\d+)?$")
SAMPLE_MARKER_RE = re.compile(r"(^|[\s._-])samples?(?:\d+)?($|[\s._-])")


def normalizedName(value: str | None) -> str:
    if not value:
        return ""

    stem = os.path.splitext(os.path.basename(value))[0]
    normalized = re.sub(r"[\W_]+", " ", stem.lower())
    return normalized.strip()


def pathSegments(value: str | None) -> list[str]:
    if not value:
        return []

    return [segment for segment in str(value).replace("\\", "/").split("/") if segment]


def isSampleFile(file: dict, include_sample_files: bool = INCLUDE_SAMPLE_FILES, sample_max_bytes: int = SAMPLE_FILE_MAX_BYTES) -> bool:
    if include_sample_files:
        return False

    names = [
        normalizedName(file.get("short_name")),
        normalizedName(file.get("name")),
    ]
    names.extend(normalizedName(segment) for segment in pathSegments(file.get("name")))

    if any(SAMPLE_NAME_RE.match(name) for name in names):
        return True

    file_size = file.get("size")
    try:
        file_size = int(file_size) if file_size is not None else None
    except (TypeError, ValueError):
        file_size = None

    if file_size is not None and file_size <= sample_max_bytes:
        return any(SAMPLE_MARKER_RE.search(str(value or "").lower()) for value in [file.get("short_name"), file.get("name")])

    return False
