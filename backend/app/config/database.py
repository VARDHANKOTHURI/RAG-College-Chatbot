import os
import json
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from .settings import settings
import logging

logger = logging.getLogger("college_chatbot.database")

# In-memory / file-backed JSON database fallback for zero-dependency local runs
class LocalJsonCollection:
    def __init__(self, name: str, db_file: str):
        self.name = name
        self.db_file = db_file
        self.lock = asyncio.Lock()
        self._load()

    def _load(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load fallback DB file {self.db_file}: {e}")
                self.data = {}
        else:
            self.data = {}

    def _save(self):
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, default=str, indent=2)

    def _matches(self, doc: dict, query: dict) -> bool:
        for k, v in query.items():
            if k == "$or":
                if not any(self._matches(doc, q) for q in v):
                    return False
                continue
            if k not in doc:
                return False
            if isinstance(v, dict):
                if "$regex" in v:
                    pattern = v["$regex"]
                    ignore_case = "i" in v.get("$options", "")
                    target = str(doc.get(k, ""))
                    if ignore_case:
                        if pattern.lower() not in target.lower():
                            return False
                    else:
                        if pattern not in target:
                            return False
                elif "$in" in v:
                    if doc.get(k) not in v["$in"]:
                        return False
                elif "$gte" in v:
                    if doc.get(k) < v["$gte"]:
                        return False
                elif "$lte" in v:
                    if doc.get(k) > v["$lte"]:
                        return False
            elif doc[k] != v:
                return False
        return True

    async def find_one(self, filter: dict = None, query: dict = None) -> Optional[dict]:
        f = filter if filter is not None else (query or {})
        async with self.lock:
            for doc in self.data.values():
                if self._matches(doc, f):
                    return doc.copy()
            return None

    async def find(self, filter: dict = None, sort: list = None, limit: int = 0, query: dict = None) -> List[dict]:
        f = filter if filter is not None else (query or {})
        async with self.lock:
            results = []
            for doc in self.data.values():
                if self._matches(doc, f):
                    results.append(doc.copy())
            
            if sort:
                for field, order in reversed(sort):
                    results.sort(key=lambda x: str(x.get(field, "")), reverse=(order == -1))
            
            if limit > 0:
                results = results[:limit]
            return results

    async def insert_one(self, doc: dict):
        async with self.lock:
            if "_id" not in doc:
                doc["_id"] = str(uuid.uuid4())
            self.data[str(doc["_id"])] = doc.copy()
            self._save()
            class InsertResult:
                def __init__(self, inserted_id):
                    self.inserted_id = inserted_id
            return InsertResult(doc["_id"])

    async def update_one(self, filter: dict, update: dict, query: dict = None):
        f = filter if filter is not None else (query or {})
        async with self.lock:
            for doc_id, doc in self.data.items():
                if self._matches(doc, f):
                    if "$set" in update:
                        doc.update(update["$set"])
                    if "$inc" in update:
                        for k, inc_val in update["$inc"].items():
                            doc[k] = doc.get(k, 0) + inc_val
                    doc["updatedAt"] = datetime.utcnow().isoformat()
                    self._save()
                    class UpdateResult:
                        matched_count = 1
                        modified_count = 1
                    return UpdateResult()
            class UpdateResult:
                matched_count = 0
                modified_count = 0
            return UpdateResult()

    async def delete_one(self, filter: dict = None, query: dict = None):
        f = filter if filter is not None else (query or {})
        async with self.lock:
            target_id = None
            for doc_id, doc in self.data.items():
                if self._matches(doc, f):
                    target_id = doc_id
                    break
            if target_id:
                del self.data[target_id]
                self._save()
                class DeleteResult:
                    deleted_count = 1
                return DeleteResult()
            class DeleteResult:
                deleted_count = 0
            return DeleteResult()

    async def delete_many(self, filter: dict = None, query: dict = None):
        f = filter if filter is not None else (query or {})
        async with self.lock:
            to_delete = [doc_id for doc_id, doc in self.data.items() if self._matches(doc, f)]
            for doc_id in to_delete:
                del self.data[doc_id]
            if to_delete:
                self._save()
            class DeleteResult:
                def __init__(self, count):
                    self.deleted_count = count
            return DeleteResult(len(to_delete))

    async def count_documents(self, filter: dict = None, query: dict = None) -> int:
        f = filter if filter is not None else (query or {})
        async with self.lock:
            count = sum(1 for doc in self.data.values() if self._matches(doc, f))
            return count


# Unified wrapper for MongoDB Motor collections
class AsyncMongoCollectionWrapper:
    def __init__(self, motor_collection):
        self._col = motor_collection

    async def find_one(self, filter: dict = None, query: dict = None) -> Optional[dict]:
        f = filter if filter is not None else (query or {})
        return await self._col.find_one(f)

    async def find(self, filter: dict = None, sort: list = None, limit: int = 0, query: dict = None) -> List[dict]:
        f = filter if filter is not None else (query or {})
        cursor = self._col.find(f)
        if sort:
            cursor = cursor.sort(sort)
        if limit > 0:
            cursor = cursor.limit(limit)
        return await cursor.to_list(length=limit if limit > 0 else 1000)

    async def insert_one(self, doc: dict):
        if "_id" not in doc:
            doc["_id"] = str(uuid.uuid4())
        return await self._col.insert_one(doc)

    async def update_one(self, filter: dict, update: dict, query: dict = None):
        f = filter if filter is not None else (query or {})
        return await self._col.update_one(f, update)

    async def delete_one(self, filter: dict = None, query: dict = None):
        f = filter if filter is not None else (query or {})
        return await self._col.delete_one(f)

    async def delete_many(self, filter: dict = None, query: dict = None):
        f = filter if filter is not None else (query or {})
        return await self._col.delete_many(f)

    async def count_documents(self, filter: dict = None, query: dict = None) -> int:
        f = filter if filter is not None else (query or {})
        return await self._col.count_documents(f)


class Database:
    def __init__(self):
        self.is_connected = False
        self.is_fallback = True
        self.db = None
        self._collections: Dict[str, Any] = {}
        self.storage_dir = "./data/local_db"

    async def connect(self):
        if settings.MONGODB_URI:
            try:
                from motor.motor_asyncio import AsyncIOMotorClient
                client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
                await client.admin.command('ping')
                self.db = client[settings.DATABASE_NAME]
                self.is_connected = True
                self.is_fallback = False
                logger.info(f"Successfully connected to MongoDB Atlas database: '{settings.DATABASE_NAME}'")
                return
            except Exception as e:
                logger.warning(f"MongoDB connection failed ({e}). Falling back to embedded local storage.")

        self.is_connected = True
        self.is_fallback = True
        os.makedirs(self.storage_dir, exist_ok=True)
        logger.info("Using embedded local database storage.")

    def get_collection(self, name: str):
        if not self.is_fallback and self.db is not None:
            if name not in self._collections:
                self._collections[name] = AsyncMongoCollectionWrapper(self.db[name])
            return self._collections[name]
        
        if name not in self._collections:
            db_file = os.path.join(self.storage_dir, f"{name}.json")
            self._collections[name] = LocalJsonCollection(name, db_file)
        return self._collections[name]

db_manager = Database()

def get_db():
    return db_manager
