import os
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import START_MSG, CHANNELS, ADMINS, AUTH_CHANNEL
from utils import Media, get_file_details
from pyrogram.errors import UserNotParticipant
logger = logging.getLogger(__name__)

@Client.on_message(filters.command("start"))
async def start(bot, cmd):
    usr_cmdall1 = cmd.text
    if usr_cmdall1.startswith("/start NickxFury"):
        if AUTH_CHANNEL:
            invite_link = await bot.create_chat_invite_link(int(AUTH_CHANNEL))
            try:
                user = await bot.get_chat_member(int(AUTH_CHANNEL), cmd.from_user.id)
                if user.status == "kicked":
                    await bot.send_message(
                        chat_id=cmd.from_user.id,
                        text="You are Banned to use me.Byee 🖐️",
                        parse_mode="markdown",
                        disable_web_page_preview=True
                    )
                    return
            except UserNotParticipant:
                ident, file_id = cmd.text.split("_-_-_-_")
                await bot.send_message(
                    chat_id=cmd.from_user.id,
                    text="♦️ READ THIS INSTRUCTION ♦️\n\n<i>🗣 In Order To Get The Movie/Series Requested By You.\nYou Will Have To Join Our Official Channel First. After That, Try Accessing Again.</i>\n\n<b>👇 JOIN THE CHANNEL BY CLICKING THE BELOW BUTTON 👇</b>",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("😎 Join Our Official Channel 😎", url=invite_link.invite_link)
                            ],
                            [
                                InlineKeyboardButton(" 🔄 Try Again", callback_data=f"checksub#{file_id}")
                            ]
                        ]
                    ),
                    parse_mode="markdown"
                )
                return
            except Exception:
                await bot.send_message(
                    chat_id=cmd.from_user.id,
                    text="Something went Wrong.",
                    parse_mode="markdown",
                    disable_web_page_preview=True
                )
                return
        try:
            ident, file_id = cmd.text.split("_-_-_-_")
            filedetails = await get_file_details(file_id)
            for files in filedetails:
                file_caption = files.caption
                buttons = [
                    [
                        InlineKeyboardButton('🔎 Search again', switch_inline_query_current_chat=''),
                        InlineKeyboardButton('Request Movies 🎟', url='https://t.me/MOVIECLUB_CHAT')
                    ]
                    ]
                await bot.send_cached_media(
                    chat_id=cmd.from_user.id,
                    file_id=file_id,
                    caption=f'<code>{files.file_name}</code>\n\n<i>© Powered by @MovieClubOfficiall</i>',
                    reply_markup=InlineKeyboardMarkup(buttons)
                    )
        except Exception as err:
            await cmd.reply_text(f"Something went wrong!\n\n**Error:** `{err}`")
    elif len(cmd.command) > 1 and cmd.command[1] == 'subscribe':
        invite_link = await bot.create_chat_invite_link(int(AUTH_CHANNEL))
        await bot.send_message(
            chat_id=cmd.from_user.id,
            text="♦️ READ THIS INSTRUCTION ♦️\n\n<i>🗣 In Order To Get The Movie/Series Requested By You.\nYou Will Have To Join Our Official Channel First. After That, Try Accessing Again.</i>\n\n<b>👇 JOIN THE CHANNEL BY CLICKING THE BELOW BUTTON 👇</b>",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("😎 Join Our Official Channel 😎", url=invite_link.invite_link)
                    ]
                ]
            )
        )
    else:
        await cmd.reply_text(
            START_MSG,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔎 Search Here", switch_inline_query_current_chat=''),
                        InlineKeyboardButton("Request Movies 🎟", url="https://t.me/MOVIECLUB_CHAT")
                    ],
                    [
                        InlineKeyboardButton("👩‍💻 Owner", url="http://t.me/NickxFury_bot"),
                        InlineKeyboardButton("About 😎", callback_data="about")
                    ],
                    [
                        InlineKeyboardButton("📝 FeedBack 📝", url="http://t.me/MC_HelperBot")
                    ]
                ]
            )
        )


@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('total') & filters.user(ADMINS))
async def total(bot, message):
    """Show total files in database"""
    msg = await message.reply("Adding New Files To Database... 🧾", quote=True)
    try:
        total = await Media.count_documents()
        await msg.edit(f'📁 Total Saved files: {total}')
    except Exception as e:
        logger.exception('Failed to check total files')
        await msg.edit(f'Error: {e}')


@Client.on_message(filters.command('logger') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))


@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Deleting That File...🗞️", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not supported file format 😶')
        return

    result = await Media.collection.delete_one({
        'file_name': media.file_name,
        'file_size': media.file_size,
        'mime_type': media.mime_type,
        'caption': reply.caption
    })
    if result.deleted_count:
        await msg.edit('File is successfully deleted from database 😔')
    else:
        await msg.edit('File not found in database')
@Client.on_message(filters.command('about'))
async def bot_info(bot, message):
    buttons = [
        [
            InlineKeyboardButton('🎟 Request Movies 🎟', url='https://t.me/MOVIECLUB_CHAT'),
            InlineKeyboardButton('🥶 Source Code 🥶', url='https://t.me/AdhavaaBiriyaniKittiyalo')
        ]
        ]
    await query.message.edit(text="""🙋🏻‍♂️ Hellooo <code> {} 😎</code>

<b>✴️ Owner :</b> <a href='https://t.me/NickxFury_bot'>Nick Fury</a>

<b>✴️ Language :</b> <code>Python3</code>

<b>✴️ Library :</b> <a href='https://docs.pyrogram.org/'>Pyrogram asyncio</a></b>

<b>✴️ Source Code :</b> <a href='https://t.me/AdhavaaBiriyaniKittiyalo'>Click here</a>

<b>✴️ Request Movies :</b> <a href='https://t.me/MOVIECLUB_CHAT'>Movie Club</a>

</b>📜 Quote :</b> <code>ആരും പേടിക്കണ്ട എല്ലാവർക്കും കിട്ടും™️</code>""".format(query.from_user.mention))
