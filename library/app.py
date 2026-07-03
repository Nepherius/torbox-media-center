import os
from enum import Enum

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False

load_dotenv()

LEGACY_SCAN_METADATA = os.getenv("ENABLE_METADATA", "false").lower() == "true"
LEGACY_RAW_MODE = os.getenv("RAW_MODE", "false").lower() == "true"

class OrganizationModes(Enum):
    simple = "simple"
    parsed = "parsed"
    metadata = "metadata"
    raw = "raw"

class MetadataProviders(Enum):
    torbox = "torbox"
    tmdb = "tmdb"

organization_mode_env = os.getenv("ORGANIZATION_MODE", "").lower()
if organization_mode_env:
    assert organization_mode_env in [mode.value for mode in OrganizationModes], f"Invalid organization mode: {organization_mode_env}. Valid options are: {[mode.value for mode in OrganizationModes]}"
    ORGANIZATION_MODE = organization_mode_env
else:
    if LEGACY_RAW_MODE:
        ORGANIZATION_MODE = OrganizationModes.raw.value
    elif LEGACY_SCAN_METADATA:
        ORGANIZATION_MODE = OrganizationModes.metadata.value
    else:
        ORGANIZATION_MODE = OrganizationModes.simple.value

RAW_MODE = ORGANIZATION_MODE == OrganizationModes.raw.value
SCAN_METADATA = ORGANIZATION_MODE == OrganizationModes.metadata.value

METADATA_PROVIDER = os.getenv("METADATA_PROVIDER", MetadataProviders.torbox.value).lower()
assert METADATA_PROVIDER in [provider.value for provider in MetadataProviders], f"Invalid metadata provider: {METADATA_PROVIDER}. Valid options are: {[provider.value for provider in MetadataProviders]}"

METADATA_MAX_WORKERS = int(os.getenv("METADATA_MAX_WORKERS", "4"))
assert METADATA_MAX_WORKERS > 0, "METADATA_MAX_WORKERS must be greater than 0"

INCLUDE_SAMPLE_FILES = os.getenv("INCLUDE_SAMPLE_FILES", "false").lower() == "true"
SAMPLE_FILE_MAX_BYTES = int(os.getenv("SAMPLE_FILE_MAX_BYTES", str(300 * 1024 * 1024)))
assert SAMPLE_FILE_MAX_BYTES > 0, "SAMPLE_FILE_MAX_BYTES must be greater than 0"

class MountRefreshTimes(Enum):
    # times are shown in hours
    slowest = 24 # 24 hours
    very_slow = 12 # 12 hours
    slow = 6 # 6 hours
    normal = 3 # 3 hours
    fast = 2 # 2 hours
    ultra_fast = 1 # 1 hour
    instant = 0.1 # 6 minutes

MOUNT_REFRESH_TIME = os.getenv("MOUNT_REFRESH_TIME", MountRefreshTimes.normal.name)
MOUNT_REFRESH_TIME = MOUNT_REFRESH_TIME.lower()
assert MOUNT_REFRESH_TIME in [e.name for e in MountRefreshTimes], f"Invalid mount refresh time: {MOUNT_REFRESH_TIME}. Valid options are: {[e.name for e in MountRefreshTimes]}"

if MOUNT_REFRESH_TIME == "instant":
    print("!!! Instant mount refresh time may cause rate limiting issues with the API. Use with caution. !!!")

if organization_mode_env and (LEGACY_SCAN_METADATA or LEGACY_RAW_MODE):
    print("!!! ORGANIZATION_MODE is set and will be used instead of ENABLE_METADATA/RAW_MODE. !!!")

if SCAN_METADATA:
    print(f"!!! Metadata scanning is enabled using {METADATA_PROVIDER}. This may slow down the processing of files. !!!")
elif RAW_MODE:
    print("!!! Raw organization mode is enabled. Files will use the original TorBox structure. !!!")
elif ORGANIZATION_MODE == OrganizationModes.parsed.value:
    print("!!! Parsed organization mode is enabled. Files will be organized from filename hints without metadata scanning. !!!")
else:
    print("!!! Simple organization mode is enabled. Files will be placed under the movies folder without metadata scanning. !!!")

if MOUNT_REFRESH_TIME == "instant" and SCAN_METADATA:
    print("!!! Using instant mount refresh time with metadata scanning may lead to excessive API calls. Falling back to 'fast' refresh time. !!!")
    MOUNT_REFRESH_TIME = MountRefreshTimes.fast.value
else:
    MOUNT_REFRESH_TIME = MountRefreshTimes[MOUNT_REFRESH_TIME].value

def getCurrentVersion():
    return "v2.0.0"
