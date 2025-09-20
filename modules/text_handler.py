# modules/text_handler.py

import os
import requests
import subprocess

from pyrogram import Client, filters
from pyrogram.types import Message


async def text_to_txt(bot: Client, message: Message):
    # Ask for the text content
    editable = await message.reply_text(
        "<blockquote><b>Welcome to the Text to .txt Converter!\nSend the text to convert into a .txt file.</b></blockquote>"
    )
    input_message: Message = await bot.listen(message.chat.id)
    if not input_message.text:
        await message.reply_text("**Send valid text data**")
        return

    text_data = input_message.text.strip()
    try:
        await input_message.delete()
    except Exception:
        pass

    await editable.edit("**🔄 Send file name or send /d for default filename**")
    inputn: Message = await bot.listen(message.chat.id)
    raw_textn = inputn.text.strip() if inputn.text else "/d"
    try:
        await inputn.delete()
    except Exception:
        pass

    try:
        await editable.delete()
    except Exception:
        pass

    custom_file_name = "txt_file" if raw_textn == "/d" else raw_textn
    txt_file = os.path.join("downloads", f"{custom_file_name}.txt")
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)

    with open(txt_file, "w") as f:
        f.write(text_data)

    await message.reply_document(
        document=txt_file,
        caption=f"`{custom_file_name}.txt`\n\n<blockquote>You can now download your content! 📥</blockquote>"
    )

    try:
        os.remove(txt_file)
    except Exception:
        pass


def register_text_handlers(bot: Client):
    @bot.on_message(filters.command(["t2t"]))
    async def call_text_to_txt(bot: Client, m: Message):
        await text_to_txt(bot, m)
