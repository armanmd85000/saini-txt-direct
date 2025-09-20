# modules/db.py

import asyncio
import datetime
from typing import Optional, Dict, Any

from motor.motor_asyncio import AsyncIOMotorClient
from modules.vars import MONGO_URI

_client = None
_db = None
_jobs = None


def _now():
    return datetime.datetime.utcnow()


def init_db():
    global _client, _db, _jobs
    if not MONGO_URI:
        return
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URI)
        _db = _client["saini_bot"]
        _jobs = _db["range_jobs"]


def is_ready() -> bool:
    return _jobs is not None


async def _ensure_ready():
    if _jobs is None:
        init_db()
    if _jobs is None:
        raise RuntimeError("MongoDB is not initialized. Set MONGO_URI and call init_db().")


async def create_job(owner_id: int, source_channel_id: int, dest_channel_id: int,
                     start_msg_id: int, end_msg_id: int) -> Dict[str, Any]:
    await _ensure_ready()
    doc = {
        "owner_id": owner_id,
        "source_channel_id": source_channel_id,
        "dest_channel_id": dest_channel_id,
        "start_msg_id": start_msg_id,
        "end_msg_id": end_msg_id,
        "current_msg_id": start_msg_id - 1,  # nothing processed yet
        "status": "in_progress",  # in_progress | paused | done | error
        "created_at": _now(),
        "updated_at": _now(),
        "last_error": None,
    }
    res = await _jobs.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


async def get_job(job_id) -> Optional[Dict[str, Any]]:
    await _ensure_ready()
    from bson import ObjectId
    try:
        oid = ObjectId(str(job_id))
    except Exception:
        return None
    return await _jobs.find_one({"_id": oid})


async def update_progress(job_id, current_msg_id: int):
    await _ensure_ready()
    from bson import ObjectId
    await _jobs.update_one(
        {"_id": ObjectId(str(job_id))},
        {"$set": {"current_msg_id": current_msg_id, "updated_at": _now()}}
    )


async def set_status(job_id, status: str, last_error: Optional[str] = None):
    await _ensure_ready()
    from bson import ObjectId
    upd = {"status": status, "updated_at": _now()}
    if last_error is not None:
        upd["last_error"] = last_error
    await _jobs.update_one({"_id": ObjectId(str(job_id))}, {"$set": upd})


async def get_incomplete_jobs() -> list:
    await _ensure_ready()
    cursor = _jobs.find({"status": {"$in": ["in_progress", "paused"]}})
    return await cursor.to_list(length=1000)


async def get_active_job_for_owner(owner_id: int) -> Optional[Dict[str, Any]]:
    await _ensure_ready()
    return await _jobs.find_one({
        "owner_id": owner_id,
        "status": {"$in": ["in_progress", "paused"]}
    })
