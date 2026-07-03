import hashlib
import json
import logging
import os
import time

from functions.mediaFunctions import cleanTitle, cleanYear, constructSeriesTitle
from functions.organizationFunctions import buildParsedMetadata, formatTitleYear, inferMediaType
from library.app import getCurrentVersion
from library.tmdb import TMDB_ACCESS_TOKEN, TMDB_API_KEY, TMDB_INCLUDE_ADULT, TMDB_LANGUAGE

TMDB_API_URL = "https://api.themoviedb.org/3"
TMDB_WEB_URL = "https://www.themoviedb.org"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/original"
TMDB_CACHE_TTL = 24 * 60 * 60
_cache: dict[str, tuple[float, dict | None]] = {}


def isTmdbConfigured() -> bool:
    return bool(TMDB_ACCESS_TOKEN or TMDB_API_KEY)


def tmdbCacheKey(path: str, params: dict) -> str:
    key_data = {"path": path, "params": params}
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.sha256(key_str.encode()).hexdigest()


def tmdbImageUrl(path: str | None) -> str | None:
    if not path:
        return None
    return f"{TMDB_IMAGE_URL}{path}"


def tmdbYear(value: str | int | None) -> int | None:
    if isinstance(value, str) and len(value) >= 4:
        return cleanYear(value[:4])
    return cleanYear(value)


def tmdbTitle(result: dict, media_type: str) -> str:
    if media_type == "series":
        return cleanTitle(result.get("name") or result.get("original_name"))
    return cleanTitle(result.get("title") or result.get("original_title"))


def buildTmdbMetadata(result: dict, media_type: str, title_data: dict, file_name: str, fallback_metadata: dict) -> dict:
    extension = os.path.splitext(file_name)[-1]
    title = tmdbTitle(result, media_type) or fallback_metadata.get("metadata_title")
    year_source = result.get("first_air_date") if media_type == "series" else result.get("release_date")
    year = cleanYear(title_data.get("year")) or tmdbYear(year_source)

    metadata = dict(fallback_metadata)
    metadata.update({
        "metadata_title": title,
        "metadata_link": f"{TMDB_WEB_URL}/tv/{result.get('id')}" if media_type == "series" else f"{TMDB_WEB_URL}/movie/{result.get('id')}",
        "metadata_mediatype": media_type,
        "metadata_image": tmdbImageUrl(result.get("poster_path")),
        "metadata_backdrop": tmdbImageUrl(result.get("backdrop_path")),
        "metadata_years": year,
        "metadata_provider": "tmdb",
        "metadata_provider_id": result.get("id"),
        "metadata_rootfoldername": formatTitleYear(title, year),
    })

    if media_type == "series":
        series_season_episode = constructSeriesTitle(
            season=title_data.get("season"),
            episode=title_data.get("episode"),
        )
        metadata["metadata_foldername"] = constructSeriesTitle(
            season=title_data.get("season", 1),
            folder=True,
        ) or "Season 1"
        metadata["metadata_season"] = title_data.get("season", 1)
        metadata["metadata_episode"] = title_data.get("episode")
        metadata["metadata_filename"] = f"{title} {series_season_episode}{extension}" if series_season_episode else file_name
    else:
        metadata["metadata_filename"] = f"{formatTitleYear(title, year)}{extension}"

    return metadata


def tmdbRequest(path: str, params: dict) -> dict | None:
    if not isTmdbConfigured():
        return None

    request_params = {
        "language": TMDB_LANGUAGE,
        "include_adult": str(TMDB_INCLUDE_ADULT).lower(),
        **params,
    }
    headers = {
        "Accept": "application/json",
        "User-Agent": f"TorBox-Media-Center/{getCurrentVersion()} TMDB/1.0",
    }
    if TMDB_ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {TMDB_ACCESS_TOKEN}"
    else:
        request_params["api_key"] = TMDB_API_KEY

    cache_key = tmdbCacheKey(path, request_params)
    if cache_key in _cache:
        cached_time, cached_data = _cache[cache_key]
        if time.time() - cached_time < TMDB_CACHE_TTL:
            return cached_data
        del _cache[cache_key]

    try:
        import httpx
    except ImportError:
        logging.error("httpx is required for TMDB metadata lookups.")
        return None

    try:
        response = httpx.get(
            f"{TMDB_API_URL}{path}",
            params=request_params,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        _cache[cache_key] = (time.time(), data)
        return data
    except Exception as e:
        logging.error(f"Error searching TMDB metadata: {e}")
        _cache[cache_key] = (time.time(), None)
        return None


def searchTmdbEndpoint(media_type: str, query: str, year: int | None) -> dict | None:
    path = "/search/tv" if media_type == "series" else "/search/movie"
    params = {
        "query": query,
        "page": 1,
    }
    if year:
        if media_type == "series":
            params["first_air_date_year"] = year
        else:
            params["primary_release_year"] = year

    data = tmdbRequest(path, params)
    results = data.get("results", []) if data else []
    if not results:
        return None

    return results[0]


def searchTmdbMetadata(query: str, title_data: dict, file_name: str, item_name: str):
    fallback_metadata = buildParsedMetadata(query, title_data, file_name, item_name)
    if not isTmdbConfigured():
        return fallback_metadata, False, "TMDB metadata provider is not configured. Using parsed fallback."

    parsed_title = title_data.get("title") or query or os.path.splitext(file_name or "")[0]
    parsed_year = cleanYear(title_data.get("year"))
    preferred_type = inferMediaType(title_data)
    media_types = ["series"] if preferred_type == "series" else ["movie", "series"]

    for media_type in media_types:
        result = searchTmdbEndpoint(media_type, parsed_title, parsed_year)
        if result:
            metadata = buildTmdbMetadata(result, media_type, title_data, file_name, fallback_metadata)
            return metadata, True, f"TMDB metadata found. Searching for {query}."

    return fallback_metadata, False, f"No TMDB metadata found. Using parsed fallback. Searching for {query}."
