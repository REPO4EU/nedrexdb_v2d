import gzip as _gzip
import sqlite3
import subprocess as _sp

from nedrexdb.db import MongoInstance
from nedrexdb.db.parsers import _get_file_location_factory
from nedrexdb.db.models.nodes.drug import Drug
from nedrexdb.downloaders import get_latest_chembl_version
from nedrexdb.logger import logger

get_file_location = _get_file_location_factory("chembl")


def get_chembl_drugbank_map():
    path = get_file_location("unichem")
    cd_map = {}
    with _gzip.open(path, "rt") as f:
        next(f)  # Skip header row
        for line in f:
            chembl_id, drugbank_id = line.strip().split()
            cd_map[drugbank_id] = chembl_id

    return cd_map


def decompress_if_necessary():
    version = get_latest_chembl_version()
    url_path = get_file_location("sqlite")

    target_dir = url_path.parents[0] / url_path.name.rsplit(".", 2)[0].format(version)

    if not target_dir.exists():
        target_dir.mkdir(parents=True)

    db_list = [i for i in target_dir.rglob("*") if i.name.endswith(".db")]
    assert len(db_list) <= 1, f"Expected at most one .db file in {target_dir}, found {len(db_list)}"

    if not db_list:
        # unpack
        path = url_path.parents[0] / url_path.name.format(version)
        _sp.call(
            ["tar", "-zxvf", f"{path}", "-C", f"{target_dir.resolve()}", "--strip-components", "1"], cwd=f"{path.parents[0]}"
        )

    db_list = [i for i in target_dir.rglob("*") if i.name.endswith(".db")]
    assert len(db_list) == 1, f"Expected exactly one .db file in {target_dir}, found {len(db_list)}"
    
    return db_list[0]


def parse_chembl():
    logger.info("Parsing ChEMBL")
    cd_map = get_chembl_drugbank_map()

    db = decompress_if_necessary()
    con = sqlite3.connect(f"{db}")
    cur = con.cursor()

    # check overlap between drugbank and chembl
    drugs = {drug["primaryDomainId"].replace("drugbank.", "") for drug in Drug.find(MongoInstance.DB)}
    # print intersection and exclusives
    logger.debug(f"Intersection of DrugBank and ChEMBL drugs : {len(drugs & set(cd_map.keys()))}")
    logger.debug(f"Exclusive to DrugBank: {len(drugs - set(cd_map.keys()))}")
    logger.debug(f"Exclusive to ChEMBL (not added to NeDRex): {len(set(cd_map.keys()) - drugs)})")

    for drugbank_id, chembl_id in cd_map.items():
        result = list(cur.execute("SELECT MAX_PHASE FROM MOLECULE_DICTIONARY WHERE CHEMBL_ID = '%s'" % chembl_id))
        if not result:
            continue
        max_phase = max(i[0] for i in result)

        if max_phase == 4:
            query = {"primaryDomainId": f"drugbank.{drugbank_id}"}
            update = {"$addToSet": {"drugGroups": "approved", "dataSources": "chembl"}}
            MongoInstance.DB[Drug.collection_name].update_one(query, update)
