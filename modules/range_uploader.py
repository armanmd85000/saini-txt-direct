import asyncio
from typing import Optional

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from modules.vars import OWNER, AUTH_USERS, TXT_SOURCE_CHANNEL, UPLOAD_DEST
from modules import db

def register_range_handlers(bot: Client):
    db.init_db()

    @bot.on_message(filters.command(["range_upload"]) & filters.private)
    async def cmd_range_upload(client: Client, m: Message):
        if m.from_user is None or m.from_user.id not in AUTH_USERS:
            return await m.reply_text("**Not authorized.**")
        if TXT_SOURCE_CHANNEL is None or UPLOAD_DEST is None:
            return await m.reply_text("**Config missing.** Set TXT_SOURCE_CHANNEL and UPLOAD_DEST in env.")
        try:
            # /range_upload <start_msg_id> <end_msg_id>
            _, s, e = m.text.strip().split(maxsplit=2)
            start_id = int(s)
            end_id = int(e)
        except Exception:
            return await m.reply_text("Usage: /range_upload <start_msg_id> <end_msg_id>")

        if start_id <= 0 or end_id <= 0 or end_id < start_id:
            return await m.reply_text("Provide valid positive range: start <= end.")

        active = await db.get_active_job_for_owner(m.from_user.id)
        if active:
            return await m.reply_text("A job is already active/paused. Use /range_status or /range_pause first.")

        job = await db.create_job(
            owner_id=m.from_user.id,
            source_channel_id=TXT_SOURCE_CHANNEL,
            dest_channel_id=UPLOAD_DEST,
            start_msg_id=start_id,
            end_msg_id=end_id
        )
        await m.reply_text(f"Job created. Starting upload {start_id}..{end_id}\nJob ID: `{job['_id']}`")

        asyncio.create_task(_process_job_loop(client, job["_id"]))  # fire and forget

    @bot.on_message(filters.command(["range_status"]) & filters.private)
    async def cmd_range_status(client: Client, m: Message):
        if m.from_user is None or m.from_user.id not in AUTH_USERS:
            return await m.reply_text("**Not authorized.**")
        job = await db.get_active_job_for_owner(m.from_user.id)
        if not job:
            return await m.reply_text("No active/paused job.")
        cur = job.get("current_msg_id", job["start_msg_id"] - 1)
        total = job["end_msg_id"] - job["start_msg_id"] + 1
        done = max(0, cur - job["start_msg_id"] + 1)
        remain = max(0, total - done)
        status = job.get("status", "?")
        last_error = job.get("last_error", "-")
        await m.reply_text(
            f"Job: `{job['_id']}`\n"
            f"Range: {job['start_msg_id']}..{job['end_msg_id']}\n"
            f"Status: {status}\n"
            f"Done: {done}/{total} | Remaining: {remain}\n"
            f"Current msg_id: {cur}\n"
            f"Last error: {last_error}"
        )

    @bot.on_message(filters.command(["range_pause"]) & filters.private)
    async def cmd_range_pause(client: Client, m: Message):
        if m.from_user is None or m.from_user.id not in AUTH_USERS:
            return await m.reply_text("**Not authorized.**")
        job = await db.get_active_job_for_owner(m.from_user.id)
        if not job:
            return await m.reply_text("No active/paused job.")
        await db.set_status(job["_id"], "paused")
        await m.reply_text(f"Job `{job['_id']}` paused.")

    @bot.on_message(filters.command(["range_resume"]) & filters.private)
    async def cmd_range_resume(client: Client, m: Message):
        if m.from_user is None or m.from_user.id not in AUTH_USERS:
            return await m.reply_text("**Not authorized.**")
        job = await db.get_active_job_for_owner(m.from_user.id)
        if not job:
            return await m.reply_text("No active/paused job.")
        await db.set_status(job["_id"], "in_progress")
        await m.reply_text(f"Resuming job `{job['_id']}`.")
        asyncio.create_task(_process_job_loop(client, job["_id"]))

async def _process_job_loop(bot: Client, job_id: str):
    job = await db.get_job(job_id)
    if not job or job.get("status") not in ("in_progress", "paused"):
        return
    source = job["source_channel_id"]
    dest = job["dest_channel_id"]
    start = job["start_msg_id"]
    end = job["end_msg_id"]
    cur = job.get("current_msg_id", start - 1)

    # resume point
    next_id = max(start, cur + 1)

    while True:
        # refresh job document for latest status
        job = await db.get_job(job_id)
        if not job or job.get("status") != "in_progress":
            return  # paused or finished

        if next_id > end:
            await db.set_status(job_id, "done")
            try:
                await bot.send_message(job["owner_id"], f"✅ Range job `{job_id}` completed.")
            except Exception:
                pass
            return

        try:
            msg = await bot.get_messages(source, next_id)
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
            continue
        except Exception as e:
            await db.set_status(job_id, "error", last_error=str(e))
            try:
                await bot.send_message(job["owner_id"], f"Error fetching msg {next_id}: {e}")
            except Exception:
                pass
            return

        # Only process Telegram documents ending with .txt or text messages to be saved as .txt
        try:
            if msg and msg.document and (msg.document.file_name or "").lower().endswith(".txt"):
                # forward or reupload
                try:
                    # forwarding preserves file_id and is faster
                    await bot.forward_messages(dest, source, msg.id)
                except Exception:
                    # fallback: download+send
                    p = await msg.download()
                    await bot.send_document(dest, p, caption=f"`{msg.document.file_name}`")
            elif msg and msg.text:
                # create a .txt on the fly from text message
                content = msg.text
                fname = f"message_{next_id}.txt"
                import os, io, tempfile
                with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as tf:
                    tf.write(content)
                    path = tf.name
                await bot.send_document(dest, path, caption=f"`{fname}`")
                try:
                    os.remove(path)
                except Exception:
                    pass
            else:
                # skip silently if not a txt or text
                pass

            await db.update_progress(job_id, next_id)
            next_id += 1

        except FloodWait as fw:
            await db.update_progress(job_id, next_id)  # persist current id before sleep
            await asyncio.sleep(fw.value)
        except Exception as e:
            # persist and pause so it can be resumed safely
            await db.set_status(job_id, "paused", last_error=str(e))
            try:
                await bot.send_message(job["owner_id"], f"Paused at msg {next_id} due to error: {e}")
            except Exception:
                pass
            return
