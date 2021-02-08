from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from wbb import OWNER_ID, SUDO_USER_ID, app
from wbb.utils import cust_filter
from wbb.utils.botinfo import BOT_ID
from pyrogram.types import (
    CallbackQuery,
    Chat,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    User,
)
from wbb.modules.admin import kick, ban

import wbb.sql.warns_sql as sql

no_input_reply = (
    "I don't know who you're talking about, you're going to need to specify a user...!"
)
userid_not_valid = "can't get that user!"
user_is_admin = "Sorry! I can't warn an Admeme"
owner_or_sudo = "I can't Ban My Owner and Sudo"
permission_denied = "You Don't have the permission to do it !"
warn_removed = "✅ Warn Removed"
warn_removed_caption = "✅ Warn removed by {} !"
no_warns_msg = "{} doesn't have any warns."
total_warns_msg = "{} has {}/{} warnings.\n**Reasons** are:"
purge_warns = "{} reset {} warns of {} in {}!"
banned_text = "Warnings has been exceeded! {} has been {}!"


@app.on_message(cust_filter.command(commands=("warn")))
async def warnercat(_, message: Message):
    warn_user_id, reason = message.extract_user_and_text
    if not warn_user_id:
        return await message.err(no_input_reply, del_in=3)

    warned_user = await message.client.get_users(warn_user_id)
    
    
    if await admin_check(message.chat, warned_user.id):
        return await message.err(user_is_admin, del_in=3)
    
    if warned_user.id in Config.OWNER_ID or warned_user.id in Config.SUDO_USERS:
        return await message.err(owner_or_sudo, del_in=3)
    
    num_warns, reasons = sql.warn_user(
        warn_user_id, message.chat.id, reason
    )
    if num_warns >= limit:
        sql.reset_warns(warn_user_id, message.chat.id)
        if sql.get_warn_strength(message.chat.id) == "kick":
            try:
                if (await app.get_chat_member(
                    message.chat.id, message.from_user.id)).status == 'creator' \
                    or (await app.get_chat_member(
                        message.chat.id, message.from_user.id)).can_restrict_members \
                        is True or message.from_user.id in SUDO:

                    if len(message.command) == 2:
                        username = (message.text.split(None, 1)[1])
                        if (await app.get_users(username)).id in SUDO:
                            await message.reply_text("You Wanna Ban The Elevated One?")
                        else:
                            if (await app.get_users(username)).id in \
                                    await list_members(message.chat.id):
                                await message.chat.kick_member(username)
                                await message.reply_text(f"Banned! {username}")
                            else:
                                await message.reply_text("This user isn't here,"
                                                         " consider banning yourself.")

                    if len(message.command) == 1 and message.reply_to_message:
                        if message.reply_to_message.from_user.id in SUDO:
                            await message.reply_text("You Wanna Ban The Elevated One?")
                        else:
                            if message.reply_to_message.from_user.id in \
                                    await list_members(message.chat.id):
                                user_id = message.reply_to_message.from_user.id
                                await message.reply_to_message.chat.kick_member(user_id)
                                await message.reply_text("Banned!")
                            else:
                                await message.reply_text("This user isn't here.")
            except Exception as e:
                await message.reply_text(str(e))
        if sql.get_warn_strength(message.chat.id) == "ban":
            try:
                if (await app.get_chat_member(
                    message.chat.id, message.from_user.id)).status == 'creator' \
                    or (await app.get_chat_member(
                        message.chat.id, message.from_user.id)).can_restrict_members \
                        is True or message.from_user.id in SUDO:

                    if len(message.command) == 2:
                        username = (message.text.split(None, 1)[1])
                        if (await app.get_users(username)).id in SUDO:
                            await message.reply_text("You Wanna Ban The Elevated One?")
                        else:
                            if (await app.get_users(username)).id in \
                                    await list_members(message.chat.id):
                                await message.chat.kick_member(username)
                                await message.reply_text(f"Banned! {username}")
                            else:
                                await message.reply_text("This user isn't here,"
                                                         " consider banning yourself.")

                    if len(message.command) == 1 and message.reply_to_message:
                        if message.reply_to_message.from_user.id in SUDO:
                            await message.reply_text("You Wanna Ban The Elevated One?")
                        else:
                            if message.reply_to_message.from_user.id in \
                                    await list_members(message.chat.id):
                                user_id = message.reply_to_message.from_user.id
                                await message.reply_to_message.chat.kick_member(user_id)
                                await message.reply_text("Banned!")
                            else:
                                await message.reply_text("This user isn't here.")
            except Exception as e:
                await message.reply_text(str(e))
        if sql.get_warn_strength(message.chat.id) == "mute":
            try:
                chat_id = message.chat.id
                from_user_id = message.from_user.id
                if not message.reply_to_message:
                    await message.reply_text("Reply To A User's Message!")
                    return

                if (await app.get_chat_member(chat_id,
                                              from_user_id)).can_restrict_members \
                    or (await app.get_chat_member(chat_id, from_user_id)).status \
                    == 'creator' \
                        or message.from_user.id in SUDO:
                    victim = message.reply_to_message.from_user.id
                    await message.chat.restrict_member(victim,
                                                       permissions=ChatPermissions())
                    await message.reply_text("Muted!")
                else:
                    await message.reply_text("Get Yourself An Admin Tag!")
            except Exception as e:
                await message.reply_text(str(e))
    else:
        reply = "<u><a href='tg://user?id={}'>user</a></u> has {}/{} warnings... watch out!".format(
            warn_user_id, num_warns, limit
        )
        if warn_reason:
            reply += "\nReason: {}".format(html.escape(reason))
        btn_row = [
            InlineKeyboardButton(
                "⚠️  Remove Warn", callback_data=f"remove_warn_{warn_id}"
            )
        ]
        await app.send_message(
            message.chat.id,
            warn_text,
            disable_web_page_preview=True,
            reply_markup=buttons,
            reply_to_message_id=reply_id,
        )
