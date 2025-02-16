from telethon import TelegramClient, Button
from telethon.types import PeerUser, PeerChannel, ChatFull
from telethon.events import NewMessage, CallbackQuery
from telethon.errors import ChatAdminRequiredError, ChannelPrivateError, UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest, GetFullChannelRequest
from typing import Optional


class BotConfigs:

    SESSION_NAME = "Bot"
    API_ID = 123
    API_HASH = "123"
    BOT_TOKEN = ""
    
    START_MEDIA = "https://t.me/c/2258272508/11"

    MEDIAS = {
        "windows": [
            "https://t.me/c/2258272508/11",
            "https://t.me/c/2258272508/11"

        ],
        "android": [
            "https://t.me/c/2258272508/11",

        ],
        "ios": [
            "https://t.me/c/2258272508/11",
        ]
    }

    START_CAPTION = (
        "this\n"
        "is\n"
        "a\n"
        "caption\n"
        "good lock"
    )
    HELP_CAPTION = (
        "this is media caption\n"
        "good lock"
    )

    CHANNELS = [
        2258272508,
    ]
    ADMIN = 2056493966


client = TelegramClient(
    session=BotConfigs.SESSION_NAME,
    api_id=BotConfigs.API_ID,
    api_hash=BotConfigs.API_HASH,
).start(
    bot_token=BotConfigs.BOT_TOKEN
)


async def check_join(user_id: int, send_message: Optional[bool] = False) -> bool:

    if not BotConfigs.CHANNELS:
        return True

    not_joined = []
    not_admin = []

    for channel in BotConfigs.CHANNELS[:]:

        try:

            await client(GetParticipantRequest(PeerChannel(channel), PeerUser(int(user_id))))

        except UserNotParticipantError:

            full_channel = await client(GetFullChannelRequest(PeerChannel(channel_id=channel)))

            if not full_channel:
                continue
            
            not_joined.append(
                (
                    Button.url(text=full_channel.chats[0].title, url=full_channel.full_chat.exported_invite.link),
                )
            )
        
        except (ChatAdminRequiredError, ChannelPrivateError):
            not_admin.append(channel)
            BotConfigs.CHANNELS.remove(channel)

        except Exception as e:
            not_admin.append(channel)
            BotConfigs.CHANNELS.remove(channel)
        
    
    for channel in not_admin:
        try:
            await client.send_message((BotConfigs.ADMIN), message=f"کانال با ایدی {channel} ربات رو از ادمینی دراورد و ربات اونو حذف کرد")
        except Exception as e:
            print(e)
    
    if not not_joined:
        return True

    try:
        if send_message and not_joined:

            not_joined.append(
                (
                    Button.inline(text="✅ بررسی عضویت ✅", data="acc_join"),
                )
            )

            await client.send_message(
                entity=PeerUser(user_id), 
                message="⚠️ برای فعالیت در ربات باید عضو کانال های زیر بشوید", 
                buttons=not_joined
            )

    except Exception as e:
        print("error in send message for join channel : ". e)
    finally:
        return False


@client.on(event=NewMessage(pattern="/start"))
async def text_handler(event) -> None:

    try:

        if not await check_join(event.sender_id, True):
            return

        info = BotConfigs.START_MEDIA.split('/')
        channel_id, post_id = info[-2], info[-1]

        if not channel_id and not post_id:
            await event.respond("❌ مشکلی پیش آمد, این مورد را به پشتیبانی گزارش دهید")
            return

        message = await client.get_messages(PeerChannel(int(channel_id)), ids=int(post_id))

        if message:

            if message.media:

                await client.send_file(event.chat_id, message.media, buttons=(Button.inline(text="🖇 راهنمای اتصال", data="help"),), caption=BotConfigs.START_CAPTION)
            else:

                await event.respond(message)
        
        else:
            await event.respond("❌ مشکلی پیش آمد, این مورد را به پشتیبانی گزارش دهید")
            return

    except Exception as e:
        print("error in send media : ", e)
        await event.edit("❌ مشکلی پیش آمد, این مورد را به پشتیبانی گزارش دهید")


@client.on(event=CallbackQuery())
async def callback_handler(event: CallbackQuery.Event) -> None:

    data = str(event.data.decode())

    if not await check_join(event.sender_id, True):
        if data == "acc_join":
            await event.delete()
        return
    

    match data:

        case "help":
            await event.delete()
            await event.respond(
                "🖥 برای دریافت آموزش, لطفا نوع دستگاه خود را انتخاب کنید.",
                buttons=(
                    (
                        Button.inline(text="💻 Windows", data="windows_help"),
                        Button.inline(text="🤖 Android", data="android_help")
                    ),
                    (
                        Button.inline(text="📱 IOS", data="ios_help"),
                    )
                )
            )

        case "acc_join":

            try:
                info = BotConfigs.START_MEDIA.split('/')
                channel_id, post_id = info[-2], info[-1]

                if not channel_id and not post_id:
                    await event.edit("❌ مشکلی پیش آمد, این مورد را به پشتیبانی گزارش دهید")
                    return

                message = await client.get_messages(PeerChannel(int(channel_id)), ids=int(post_id))

                if message:

                    if message.media:

                        await client.send_file(event.chat_id, message.media, caption=BotConfigs.START_CAPTION, buttons=(Button.inline(text="🖇 راهنمای اتصال", data="help"),))
                    else:

                        await event.respond(message)
                
                else:
                    await event.edit("❌ مشکلی پیش آمد, این مورد را به پشتیبانی گزارش دهید")
                    return

            except Exception as e:
                print("error in send media : ", e)
                await event.edit("❌ مشکلی پیش آمد, این مورد را به پشتیبانی گزارش دهید")

        case data if data.endswith("_help"):

            try:

                opration = data.split("_")[0]

                for media in BotConfigs.MEDIAS.get(opration, []):

                    info = media.split('/')
                    channel_id, post_id = info[-2], info[-1]

                    if not channel_id and not post_id:
                        await event.edit("❌ مشکلی پیش آمد, این مورد را به پشتیبانی گزارش دهید")
                        return

                    message = await client.get_messages(PeerChannel(int(channel_id)), ids=int(post_id))

                    if message:

                        if message.media:

                            await client.send_file(event.chat_id, message.media, caption=BotConfigs.HELP_CAPTION)
                        else:

                            await event.respond(message)
                    
                    else:
                        await event.edit("❌ مشکلی پیش آمد, این مورد را به پشتیبانی گزارش دهید")
                        return

            except Exception as e:
                print("error in send media : ", e)
                await event.edit("❌ مشکلی پیش آمد, این مورد را به پشتیبانی گزارش دهید")
                


if __name__ == "__main__":
    print("bot is run")
    client.run_until_disconnected()

