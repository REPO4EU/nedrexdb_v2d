import datetime as _datetime
from typing import Optional as _Optional

from pydantic import (
    BaseModel as _BaseModel,
    Field as _Field,
    StrictStr as _StrictStr,
)
from pymongo import UpdateOne as _UpdateOne

from nedrexdb.db import models


class DrugBase(models.MongoMixin):
    collection_name: str = "drug"

    @classmethod
    def set_indexes(cls, db):
        db[cls.collection_name].create_index("primaryDomainId", unique=True)


class Drug(_BaseModel, DrugBase):
    primaryDomainId: _StrictStr = ""
    domainIds: list[str] = _Field(default_factory=list)

    dataSources: list[str] = _Field(default_factory=list)

    displayName: _StrictStr = ""
    synonyms: list[str] = _Field(default_factory=list)
    description: _StrictStr = ""

    drugCategories: list[str] = _Field(default_factory=list)
    drugGroups: list[str] = _Field(default_factory=list)
    casNumber: _StrictStr = ""
    indication: _StrictStr = ""

    def generate_update(self):
        tnow = _datetime.datetime.utcnow()
        query = {"primaryDomainId": self.primaryDomainId}
        update = {
            "$addToSet": {
                "domainIds": {"$each": self.domainIds},
                "synonyms": {"$each": self.synonyms},
                "drugCategories": {"$each": self.drugCategories},
                "drugGroups": {"$each": self.drugGroups},
                "dataSources": {"$each": self.dataSources},
            },
            "$setOnInsert": {"created": tnow},
            "$set": {
                "updated": tnow,
                "displayName": self.displayName,
                "description": self.description,
                "casNumber": self.casNumber,
                "indication": self.indication,
                "type": "Drug",
            },
        }

        # Changed to upsert=True to move towards a unified Drug model
        return _UpdateOne(query, update, upsert=True)


class BiotechDrug(Drug):
    node_type: _StrictStr = "BiotechDrug"

    sequence: _Optional[list[str]] = None

    def generate_update(self):
        tnow = _datetime.datetime.utcnow()

        query = {"primaryDomainId": self.primaryDomainId}
        update = {
            "$addToSet": {
                "domainIds": {"$each": self.domainIds},
                "dataSources": {"$each": self.dataSources},
                "synonyms": {"$each": self.synonyms},
                "drugCategories": {"$each": self.drugCategories},
                "drugGroups": {"$each": self.drugGroups},
            },
            "$set": {
                "displayName": self.displayName,
                "description": self.description,
                "casNumber": self.casNumber,
                "indication": self.indication,
                "sequence": self.sequence,
                "type": self.node_type,
                "updated": tnow,
            },
            "$setOnInsert": {"created": tnow},
        }

        return _UpdateOne(query, update, upsert=True)


class SmallMoleculeDrug(Drug):
    node_type: _StrictStr = "SmallMoleculeDrug"

    iupacName: _Optional[_StrictStr] = None
    smiles: _Optional[_StrictStr] = None
    inchi: _Optional[_StrictStr] = None
    molecularFormula: _Optional[_StrictStr] = None

    def generate_update(self):
        tnow = _datetime.datetime.utcnow()

        query = {"primaryDomainId": self.primaryDomainId}
        update = {
            "$addToSet": {
                "domainIds": {"$each": self.domainIds},
                "dataSources": {"$each": self.dataSources},
                "synonyms": {"$each": self.synonyms},
                "drugCategories": {"$each": self.drugCategories},
                "drugGroups": {"$each": self.drugGroups},
            },
            "$set": {
                "displayName": self.displayName,
                "description": self.description,
                "casNumber": self.casNumber,
                "indication": self.indication,
                "iupacName": self.iupacName,
                "smiles": self.smiles,
                "inchi": self.inchi,
                "molecularFormula": self.molecularFormula,
                "type": self.node_type,
                "updated": tnow,
            },
            "$setOnInsert": {"created": tnow},
        }

        return _UpdateOne(query, update, upsert=True)
