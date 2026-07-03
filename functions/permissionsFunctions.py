import logging
import os


def configuredOwnership() -> tuple[int | None, int | None]:
    puid = os.getenv("PUID")
    pgid = os.getenv("PGID")

    try:
        uid = int(puid) if puid else None
        gid = int(pgid) if pgid else None
        return uid, gid
    except ValueError:
        logging.warning("PUID and PGID must be numeric. Skipping ownership changes.")
        return None, None


def applyOwnership(path: str):
    uid, gid = configuredOwnership()
    if uid is None and gid is None:
        return
    if not hasattr(os, "chown"):
        return

    try:
        current_stat = os.stat(path)
        os.chown(
            path,
            uid if uid is not None else current_stat.st_uid,
            gid if gid is not None else current_stat.st_gid,
        )
    except FileNotFoundError:
        return
    except PermissionError:
        logging.warning(f"Could not change ownership for {path}. Permission denied.")
    except OSError as e:
        logging.warning(f"Could not change ownership for {path}: {e}")


def applyOwnershipToTree(path: str):
    if not os.path.exists(path):
        return

    applyOwnership(path)
    if not os.path.isdir(path):
        return

    for root, dirs, files in os.walk(path):
        for directory in dirs:
            applyOwnership(os.path.join(root, directory))
        for file in files:
            applyOwnership(os.path.join(root, file))
