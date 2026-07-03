import re
import logging

def _normalize_number(value):
    if isinstance(value, list):
        normalized = []
        for item in value:
            normalized_item = _normalize_number(item)
            if normalized_item is not None:
                normalized.append(normalized_item)
        return normalized
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return value

def _format_number(prefix: str, value):
    try:
        return f"{prefix}{int(value):02}"
    except (TypeError, ValueError):
        return f"{prefix}{value}"

def constructSeriesTitle(season = None, episode = None, folder: bool = False):
    """
    Constructs a proper title for a series based on the season and episode.

    :param season: The season number or a list of season numbers.
    :param episode: The episode number or a list of episode numbers.
    :param folder: If True, the title will be formatted for a folder name.
    """
    season = _normalize_number(season)
    episode = _normalize_number(episode)
    title_season = None
    title_episode = None

    if isinstance(season, list) and season:
        # get first and last season
        title_season = f"{_format_number('S', season[0])}-{_format_number('S', season[-1])}"
    elif isinstance(season, int) or season is not None:
        if folder:
            title_season = f"Season {season}"
        else:
            title_season = _format_number("S", season)
    
    if isinstance(episode, list) and episode:
        # get first and last episode
        title_episode = f"{_format_number('E', episode[0])}-{_format_number('E', episode[-1])}"
    elif isinstance(episode, int) or episode is not None:
        title_episode = _format_number("E", episode)

    if title_season and title_episode:
        return f"{title_season}{title_episode}"
    elif title_season:
        return title_season
    elif title_episode:
        return title_episode
    else:
        return None
    
def cleanTitle(title: str | None):
    """
    Removes invalid characters from the title.
    """
    if title is None:
        return ""
    title = str(title)
    title = re.sub(r"[\/\\\:\*\?\"\<\>\|]", "", title)
    return title

def cleanYear(year: str | int):
    """
    Cleans the year listing which can be a string (2023-2024) or an int (2023).
    """
    try:
        if not year:
            return None
        if isinstance(year, str):
            year = re.sub(r"[–—−‐‑]", "-", year)
            year = year.split("-")[0]
            year = year.strip()
            return int(year)
        if type(year) is int:
            return year
        if year and year != "None":
            return int(year)
        else:
            return None
    except Exception as e:
        logging.error(f"Error cleaning year: {e}")
        return None
