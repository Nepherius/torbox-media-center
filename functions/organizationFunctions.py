import os
import posixpath

from library.app import ORGANIZATION_MODE, OrganizationModes
from functions.mediaFunctions import cleanTitle, cleanYear, constructSeriesTitle

SERIES_MEDIA_TYPES = {"series", "anime"}


def cleanPathSegment(value, fallback: str | None = None) -> str | None:
    if value is None:
        return fallback

    cleaned = cleanTitle(str(value)).strip().strip(".")
    if cleaned in ("", ".", ".."):
        return fallback

    return cleaned


def splitOriginalPath(path: str | None) -> list[str]:
    if not path:
        return []

    parts = []
    for part in str(path).replace("\\", "/").split("/"):
        cleaned = cleanPathSegment(part)
        if cleaned:
            parts.append(cleaned)

    return parts


def formatTitleYear(title: str | None, year: str | int | None = None) -> str:
    cleaned_title = cleanPathSegment(title, "Unknown")
    cleaned_year = cleanYear(year)
    if cleaned_year:
        return f"{cleaned_title} ({cleaned_year})"
    return cleaned_title


def inferMediaType(title_data: dict | None) -> str:
    title_data = title_data or {}
    if title_data.get("season") is not None or title_data.get("episode") is not None:
        return "series"
    return "movie"


def buildSimpleMetadata(query: str, title_data: dict, file_name: str, item_name: str) -> dict:
    return {
        "metadata_title": cleanTitle(query),
        "metadata_link": None,
        "metadata_mediatype": "movie",
        "metadata_image": None,
        "metadata_backdrop": None,
        "metadata_years": None,
        "metadata_season": None,
        "metadata_episode": None,
        "metadata_filename": cleanPathSegment(file_name, "Unknown"),
        "metadata_rootfoldername": cleanPathSegment(item_name or title_data.get("title") or query, "Unknown"),
    }


def buildParsedMetadata(query: str, title_data: dict, file_name: str, item_name: str) -> dict:
    title_data = title_data or {}
    parsed_title = title_data.get("title") or os.path.splitext(file_name or "")[0] or query
    parsed_year = cleanYear(title_data.get("year"))
    media_type = inferMediaType(title_data)

    metadata = {
        "metadata_title": cleanTitle(parsed_title),
        "metadata_link": None,
        "metadata_mediatype": media_type,
        "metadata_image": None,
        "metadata_backdrop": None,
        "metadata_years": parsed_year,
        "metadata_season": title_data.get("season"),
        "metadata_episode": title_data.get("episode"),
        "metadata_filename": cleanPathSegment(file_name, "Unknown"),
        "metadata_rootfoldername": formatTitleYear(parsed_title or item_name, parsed_year),
    }

    if media_type in SERIES_MEDIA_TYPES:
        season = title_data.get("season") or 1
        metadata["metadata_foldername"] = constructSeriesTitle(season=season, folder=True) or "Season 1"

    return metadata


def isRawOrganization() -> bool:
    return ORGANIZATION_MODE == OrganizationModes.raw.value


def isSeriesMedia(data: dict) -> bool:
    return data.get("metadata_mediatype") in SERIES_MEDIA_TYPES


def topLevelFolder(data: dict) -> str:
    if isSeriesMedia(data):
        return "series"
    return "movies"


def organizedPathParts(data: dict, include_top_level: bool = True) -> list[str]:
    if isRawOrganization():
        return splitOriginalPath(data.get("path"))

    file_name = cleanPathSegment(
        data.get("metadata_filename") or data.get("file_name") or os.path.basename(data.get("path") or ""),
        "Unknown",
    )
    root_folder = cleanPathSegment(
        data.get("metadata_rootfoldername") or data.get("folder_name") or data.get("metadata_title"),
        "Unknown",
    )

    parts = []
    if include_top_level:
        parts.append(topLevelFolder(data))
    parts.append(root_folder)

    if isSeriesMedia(data):
        parts.append(cleanPathSegment(data.get("metadata_foldername"), "Season 1"))

    parts.append(file_name)
    return parts


def organizedFolderPath(data: dict, include_top_level: bool = True) -> str | None:
    parts = organizedPathParts(data, include_top_level=include_top_level)
    if not parts:
        return None

    folder_parts = parts[:-1]
    if not folder_parts:
        return ""

    return os.path.join(*folder_parts)


def organizedFileName(data: dict) -> str | None:
    parts = organizedPathParts(data)
    if not parts:
        return None
    return parts[-1]


def organizedFusePath(data: dict) -> str | None:
    parts = organizedPathParts(data)
    if not parts:
        return None

    return "/" + posixpath.join(*parts)
