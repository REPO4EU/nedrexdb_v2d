import subprocess as _sp
from pathlib import Path as _Path
import shutil as _shutil
import os as _os


from requests.exceptions import HTTPError as _HTTPError


from nedrexdb import config as _config
from nedrexdb.common import Downloader, change_directory
from nedrexdb.logger import logger


def download_opentargets():
    logger.info("Downloading OpenTargets")

    root = _Path(_config["db.root_directory"]) / _config["sources.directory"]
    target_dir = root / "opentargets"
    target_dir.mkdir(exist_ok=True, parents=True)

    target = target_dir / _config["sources.opentargets"]["gene_disease_associations"]["filename"]
    url = _config["sources.opentargets"]["gene_disease_associations"]["url"]
    print(target_dir.resolve())


    # OpenTargets downloads a directory -> delete old directory first, in case content was changed
    if _os.path.exists(target.resolve()) and _os.path.isdir(target.resolve()):
        _shutil.rmtree(target.resolve())

    # Download (Downloader class does not work, since target is a directory)
    _sp.call(
        (
            "wget",
            "--no-verbose",
            "--read-timeout",
            "10",
            "--recursive",
            "--no-parent",
            "--no-host-directories",
            "--cut-dirs",
            "8",
            "-P",
            f"{target_dir.resolve()}/",
            url,
        )
    )