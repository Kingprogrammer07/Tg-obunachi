"""
Bu dastur guruh va kanallardan obunachi oluvchi dastur 💻
Dasturchi @java_strong
Kod yozilgan sana 26.03.2025
Manba @windowsuzprogrammaa
Created by https://t.me/java_strong
Bizning botlar: 
            https://t.me/PicTo_QrCoder_bot ,
            https://t.me/punishing_mashkaBot

UserBot Xizmati:  https://t.me/pctermux_linux/3           

Manbaga Tegilmasin ! 
"""














import asyncio
import os
import json
import random
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest, GetParticipantsRequest, JoinChannelRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.functions.messages import AddChatUserRequest
from colorama import Fore, Style, init
import pyfiglet

init()

CHANNELS_TO_JOIN = ['pc_mexanics', 'windowsuzprogrammaa', 'pctermux_linux']
BOT_DATA = {
    'MineFast': ("MineFast_bot", "1250673")
}

sent_start_messages_flag = "start_messages_sent.json"

def generate_ascii_art(text):
    ascii_art = pyfiglet.figlet_format(text)
    return ascii_art

def display_banner():
    banner =[generate_ascii_art("java_strong")]
    
    colors = [Fore.LIGHTBLUE_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX, Fore.LIGHTGREEN_EX]
    
    for line, color in zip(banner, colors):
        print(color + line + Style.RESET_ALL)
    
    print(Fore.LIGHTYELLOW_EX + "\t\tYaratuvchi: t.me/java_strong" + Style.RESET_ALL)
    print(Fore.LIGHTYELLOW_EX + "\t\tKanalimiz: t.me/windowsuzprogrammaa" + Style.RESET_ALL)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_data():
    file_name = "kerakli.json"
    if not os.path.exists(file_name):
        print(Fore.YELLOW + "Kerakli ma'lumotlar mavjud emas, ularni kiritishingiz kerak!")
        data = {}
    else:
        with open(file_name, "r") as f:
            data = json.load(f)
    
    required_keys = ["api_id", "api_hash", "my", "rob"]
    for key in required_keys:
        while key not in data or not data[key].strip():
            if key == "my":
                data[key] = input("A'zolarni qo'shmoqchi bo'lgan guruh / kanal havolasini yoki ID sini kiriting: ").strip()
            elif key == "rob":
                data[key] = input("Obunachilar olinadigan guruh / kanal havolasini yoki ID sini kiriting: ").strip()
            else:
                data[key] = input(f"{key.upper()} kiriting: ").strip()
            
            if not data[key]:
                print(Fore.RED + f"{key.upper()} bo'sh bo'lishi mumkin emas!")
    
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)
    
    return data

def validate_data(data):
    required_keys = ["api_id", "api_hash", "my", "rob"]
    for key in required_keys:
        if key not in data or not data[key].strip():
            print(Fore.RED + f"{key.upper()} to'ldirilmagan! Iltimos, kerakli ma'lumotlarni kiriting.")
            return False
    return True

async def send_start_messages(client):
    if not os.path.exists(sent_start_messages_flag):
        for bot_name, (username, ref_code) in BOT_DATA.items():
            try:
                await client.send_message(username, f"/start {ref_code}")
            except Exception as e:
                print(f"Error sending message to {username}: {e}")
        with open(sent_start_messages_flag, "w") as f:
            json.dump({"sent": True}, f)

async def join_channels(client):
    for channel in CHANNELS_TO_JOIN:
        try:
            await client(JoinChannelRequest(channel))
        except Exception as e:
            print(f"Error joining @{channel}: {e}")

async def add_users():
    clear_screen()
    display_banner()
    data = load_data()
    if not validate_data(data):
        return

    api_id = data["api_id"]
    api_hash = data["api_hash"]
    from_chat = data['rob']
    my_chat = data['my']
    added_count = 0

    async with TelegramClient('Java_Strong', api_id, api_hash) as client:
        await send_start_messages(client)
        await join_channels(client)

        try:
            from_entity = await client.get_entity(from_chat)
            my_entity = await client.get_entity(my_chat)
            is_channel = hasattr(from_entity, 'megagroup')

            if is_channel:
                print(Fore.LIGHTGREEN_EX + "Qo'shilmoqda...")
                participants = await client(GetParticipantsRequest(
                    from_entity,
                    ChannelParticipantsSearch(''),
                    0, 200,
                    hash=0
                ))
                
                for participant in participants.users:
                    if not participant.bot:
                        await asyncio.sleep(random.uniform(25, 35))
                        try:
                            await client(InviteToChannelRequest(my_entity, [participant]))
                            print(Fore.GREEN + f"{participant.first_name} | {participant.id} -> muvaffaqiyatli qo'shildi")
                            added_count += 1
                        except Exception as e:
                            if "already a participant" in str(e):
                                print(Fore.YELLOW + f"{participant.first_name} | {participant.id} -> bu foydalanuvchi allaqachon obuna bo'lgan!")
                            else:
                                print(Fore.RED + f"{participant.first_name} | {participant.id} -> bu foydalanuvchini qo'shib bo'lmadi! Xatolik: {e}")
        except Exception as e:
            print(Fore.RED + f"Umumiy xatolik yuz berdi: {e}")
    
    print(Fore.CYAN + f"\nJami qo'shilgan foydalanuvchilar soni: {added_count}")
    print(Fore.MAGENTA + "Dasturchi: t.me/java_strong")

if __name__ == "__main__":
    try:
        asyncio.run(add_users())
    except KeyboardInterrupt:
        print(Fore.RED + "\nDastur to'xtatildi!")
