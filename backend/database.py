import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from pymongo import MongoClient

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "appdb")

client = MongoClient(DATABASE_URL)
db = client[DATABASE_NAME]

def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    data = {**data, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
    result = db[collection_name].insert_one(data)
    inserted = db[collection_name].find_one({"_id": result.inserted_id})
    if inserted and "_id" in inserted:
        inserted["id"] = str(inserted.pop("_id"))
    return inserted or {}


def get_documents(collection_name: str, filter_dict: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
    filter_dict = filter_dict or {}
    docs = list(db[collection_name].find(filter_dict).limit(limit))
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs


def get_document_by_id(collection_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
    from bson import ObjectId
    try:
        obj_id = ObjectId(doc_id)
    except Exception:
        return None
    doc = db[collection_name].find_one({"_id": obj_id})
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc
