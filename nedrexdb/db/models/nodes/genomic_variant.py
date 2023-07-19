import datetime as _datetime
from typing import List as _List

from pydantic import BaseModel as _BaseModel, Field as _Field, StrictStr as _StrictStr
from pymongo import UpdateOne as _UpdateOne

from nedrexdb.db import models


class GenomicVariantBase(models.MongoMixin):
    node_type: str = "GenomicVariant"
    collection_name: str = "genomic_variant"

    @classmethod
    def set_indexes(cls, db):
        db[cls.collection_name].create_index("primaryDomainId", unique=True)


class GenomicVariant(_BaseModel, GenomicVariantBase):
    class Config:
        validate_assignment = True

    primaryDomainId: _StrictStr = ""
    domainIds: _List[str] = _Field(default_factory=list)
    dataSources: list[str] = _Field(default_factory=list)

    chromosome: str = ""
    position: int = -1

    referenceSequence: str = ""
    alternativeSequence: str = ""
    variantType: str = ""

    def generate_update(self):
        tnow = _datetime.datetime.utcnow()

        query = {"primaryDomainId": self.primaryDomainId}
        update = {
            "$addToSet": {"domainIds": {"$each": self.domainIds}, "dataSources": {"$each": self.dataSources}},
            "$set": {
                "updated": tnow,
                "chromosome": self.chromosome,
                "position": self.position,
                "referenceSequence": self.referenceSequence,
                "alternativeSequence": self.alternativeSequence,
                "variantType": self.variantType,
            },
            "$setOnInsert": {
                "created": tnow,
                "type": self.node_type,
            },
        }

        return _UpdateOne(query, update, upsert=True)
