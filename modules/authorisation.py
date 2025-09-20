# modules/authorisation.py

import os
import requests
import subprocess

from pyrogram import Client, filters
from pyrogram.types import Message

from modules.vars import OWNER, CREDIT, AUTH_USERS, TOTAL_USERS


def register_authorisation_handlers(bot: Client):
    # Add an authorized user (owner-only)
    @bot.on_message(filters.command("addauth") & filters.private)
    async def add_auth_user(client: Client, message: Message):
        if message.chat.id != OWNER:
            return
        try:
            new_user_id = int(message.command[1])
        except (IndexError, ValueError):
            return await message.reply_text("**Please provide a valid user ID.**")

        if new_user_id in AUTH_USERS:
            await message.reply_text("**User ID is already authorized.**")
            return

        AUTH_USERS.append(new_user_id)
        await message.reply_text(f"**User ID `{new_user_id}` added to authorized users.**")
        try:
            await client.send_message(chat_id=new_user_id, text="<b>Great! You are added in Premium Membership!</b>")
        except Exception:
            pass

    # List authorized users (owner-only)
    @bot.on_message(filters.command("users") & filters.private)
    async def list_auth_users(client: Client, message: Message):
        if message.chat.id != OWNER:
            return
        if not AUTH_USERS:
            return await message.reply_text("**No authorized users found.**")
        user_list = "\n".join(map(str, AUTH_USERS))
        await message.reply_text(f"**Authorized Users:**\n{user_list}")

    # Remove an authorized user (owner-only)
    @bot.on_message(filters.command("rmauth") & filters.private)
    async def remove_auth_user(client: Client, message: Message):
        if message.chat.id != OWNER:
            return
        try:
            user_id_to_remove = int(message.command[1])
        except (IndexError, ValueError):
            return await message.reply_text("**Please provide a valid user ID.**")

        if user_id_to_remove not in AUTH_USERS:
            return await message.reply_text("**User ID is not in the authorized users list.**")

        AUTH_USERS.remove(user_id_to_remove)
        await message.reply_text(f"**User ID `{user_id_to_remove}` removed from authorized users.**")
        try:
            await client.send_message(chat_id=user_id_to_remove, text="<b>Oops! You are removed from Premium Membership!</b>")
        except Exception:
            pass
