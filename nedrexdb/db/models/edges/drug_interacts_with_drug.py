import datetime as _datetime

from pydantic import BaseModel as _BaseModel, StrictStr as _StrictStr, Field as _Field
from pymongo import UpdateOne as _UpdateOne

from nedrexdb.db import models


class DrugInteractsWithDrugBase(models.MongoMixin):
    edge_type: str = "DrugInteractsWithDrug"
    collection_name: str = "drug_interacts_with_drug"

    @classmethod
    def set_indexes(cls, db):
        db[cls.collection_name].create_index("memberOne")
        db[cls.collection_name].create_index("memberTwo")
        db[cls.collection_name].create_index([("memberOne", 1), ("memberTwo", 1)], unique=True)


class DrugInteractsWithDrug(_BaseModel, DrugInteractsWithDrugBase):
    class Config:
        validate_assignment = True

    memberOne: _StrictStr = ""
    memberTwo: _StrictStr = ""
    description: _StrictStr = ""
    dataSources: list[str] = _Field(default_factory=list)

    def generate_update(self):
        tnow = _datetime.datetime.utcnow()

        m1, m2 = sorted([self.memberOne, self.memberTwo])

        query = {"memberOne": m1, "memberTwo": m2}

        update = {
            "$set": {
                "updated": tnow,
                "type": self.edge_type,
                "description": self.description,
            },
            "$setOnInsert": {
                "created": tnow,
            },
            "$addToSet": {
                "dataSources": {"$each": self.dataSources},
            },
        }

        return _UpdateOne(query, update, upsert=True)
