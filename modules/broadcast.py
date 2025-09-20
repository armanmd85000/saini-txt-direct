# modules/broadcast.py

import os
import requests
import subprocess

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, PeerIdInvalid, UserIsBlocked, InputUserDeactivated

from modules.vars import OWNER, CREDIT, AUTH_USERS, TOTAL_USERS


def register_broadcast_handlers(bot: Client):
    # Owner-only: broadcast a replied message to all tracked users
    @bot.on_message(filters.command("broadcast") & filters.private)
    async def broadcast_handler(client: Client, message: Message):
        if message.chat.id != OWNER:
            return

        if not message.reply_to_message:
            return await message.reply_text("**Reply to any message (text, photo, video, or file) with /broadcast to send it to all users.**")

        success = 0
        fail = 0

        for user_id in list(set(TOTAL_USERS)):
            try:
                if message.reply_to_message.text:
                    await client.send_message(user_id, message.reply_to_message.text)
                elif message.reply_to_message.photo:
                    await client.send_photo(
                        user_id,
                        photo=message.reply_to_message.photo.file_id,
                        caption=message.reply_to_message.caption or ""
                    )
                elif message.reply_to_message.video:
                    await client.send_video(
                        user_id,
                        video=message.reply_to_message.video.file_id,
                        caption=message.reply_to_message.caption or ""
                    )
                elif message.reply_to_message.document:
                    await client.send_document(
                        user_id,
                        document=message.reply_to_message.document.file_id,
                        caption=message.reply_to_message.caption or ""
                    )
                else:
                    await client.forward_messages(user_id, message.chat.id, message.reply_to_message.message_id)
                success += 1

            except FloodWait as fw:
                # Backoff and retry once after waiting
                try:
                    await asyncio.sleep(fw.value)
                    # Retry simple forward after wait
                    await client.forward_messages(user_id, message.chat.id, message.reply_to_message.message_id)
                    success += 1
                except Exception:
                    fail += 1

            except (PeerIdInvalid, UserIsBlocked, InputUserDeactivated):
                fail += 1

            except Exception:
                fail += 1

        await message.reply_text(f"<b>Broadcast complete!</b>\n<blockquote><b>✅ Success: {success}\n❎ Failed: {fail}</b></blockquote>")

    # Owner-only: list broadcast users
    @bot.on_message(filters.command("broadusers") & filters.private)
    async def broadusers_handler(client: Client, message: Message):
        if message.chat.id != OWNER:
            return

        if not TOTAL_USERS:
            return await message.reply_text("**No Broadcasted User**")

        user_infos = []
        for uid in list(set(TOTAL_USERS)):
            try:
                user = await client.get_users(int(uid))
                fname = user.first_name or ""
                user_infos.append(f"[{user.id}](tg://openmessage?user_id={user.id}) | `{fname}`")
            except Exception:
                user_infos.append(f"`{uid}`")

        total = len(user_infos)
        text = (
            f"<blockquote><b>Total Users: {total}</b></blockquote>\n\n"
            "<b>Users List:</b>\n" + "\n".join(user_infos)
        )
        await message.reply_text(text)
