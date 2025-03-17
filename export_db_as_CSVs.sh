#!/bin/bash

CONTAINER_NAME="licensed_nedrex_live"
DBNAME="nedrex"

echo "Collection Fields for Database: $DBNAME"

# Get all available collections
collections=$(docker exec -it $CONTAINER_NAME mongo $DBNAME --eval "db.getCollectionNames();" --quiet)

echo "Collections: $collections"

collectionArray=$(echo "$collections" | tr -d '[],"' | tr -s '[:space:]' '\n')


# loop over all collections
for collection in $(echo $collectionArray); do
    echo "Starting with collection: $collection"
    
    # Skip collection "_collections"
    if [ "$collection" == "_collections" ]; then
        echo "Skipping collection: $collection"
        continue
    fi

    # get the fields of the collection
    keys=$(docker exec -it $CONTAINER_NAME mongo $DBNAME --eval "
        var keys = [];
        var doc = db.${collection}.findOne();
        for (var key in doc) { keys.push(key); }
        keys.join(\",\");
    " --quiet)
    
    echo "Exporting collection: $collection with fields: $keys"
    # use mongoexport
    mongoexport --uri="mongodb://localhost:27018" --db=$DBNAME --collection=$collection --type=csv --out="db_dump/${collection}.csv" --fields "$keys"
done
