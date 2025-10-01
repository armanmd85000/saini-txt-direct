import os
from pyrogram import Client, filters
from pyrogram.types import Message

# ================== TEXT → TXT converter ==================
async def text_to_txt(bot: Client, message: Message):
    user_id = str(message.from_user.id)
    # Ask user to send text
    editable = await message.reply_text(
        "<blockquote><b>Welcome to the Text to .txt Converter!\nSend the **text** for convert into a `.txt` file.</b></blockquote>"
    )

    input_message: Message = await bot.listen(message.chat.id)
    if not input_message.text:
        await message.reply_text("**Send valid text data**")
        return

    text_data = input_message.text.strip()
    await input_message.delete()
    
    await editable.edit("**🔄 Send file name or send /d for filename**")
    inputn: Message = await bot.listen(message.chat.id)
    raw_textn = inputn.text
    await inputn.delete()
    await editable.delete()

    if raw_textn == '/d':
        custom_file_name = 'txt_file'
    else:
        custom_file_name = raw_textn

    txt_file = os.path.join("downloads", f'{custom_file_name}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)

    with open(txt_file, 'w') as f:
        f.write(text_data)
        
    await message.reply_document(
        document=txt_file, 
        caption=f"`{custom_file_name}.txt`\n\n<blockquote>You can now download your content! 📥</blockquote>"
    )
    os.remove(txt_file)

# ================== TXT file echo + process ==================
@Client.on_message(filters.document)
async def handle_txt_file(client, message: Message):
    # Only react to TXT files
    if message.document and message.document.mime_type == "text/plain":
        file_path = await message.download()

        # Step 1: Re-send the same TXT file to group/channel
        await client.send_document(
            chat_id=message.chat.id,
            document=file_path,
            caption=f"Here’s your file `{message.document.file_name}` back! ✅\nNow starting processing..."
        )

        # Step 2: Start processing (you can replace this with upload logic)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Example: show first 100 characters in log
        print("Processing started:", content[:100])

        # TODO: Replace with your custom logic (upload, parse, store etc.)

        # Optional: delete local file after use
        os.remove(file_path)

# ================== REGISTER COMMANDS ==================
def register_text_handlers(bot):
    @bot.on_message(filters.command(["t2t"]))
    async def call_text_to_txt(bot: Client, m: Message):
        await text_to_txt(bot, m)
