"""
Telegram Guruh A'zo Qo'shuvchi (Obunachi) 📡

Guruh va kanallardan a'zolarni boshqa guruh/kanalga ko'chiruvchi dastur.
Bitta fayl — hamma narsa shu yerda: auto-install, disclaimer, sozlamalar.

Ishlaydi: Windows, Linux, Termux, Pydroid 3, va boshqa Python muhitlarda.
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════════════════
# 1-QADAM: KUTUBXONALARNI AVTOMATIK O'RNATISH
# ═══════════════════════════════════════════════════════════════════════════════

import subprocess
import sys
import os

def _install_package(package_name: str, import_name: str | None = None) -> bool:
    """Kutubxonani pip orqali o'rnatadi.

    Args:
        package_name: pip dagi paket nomi (masalan 'telethon').
        import_name: import qilinadigan nom (agar paket nomidan farq qilsa).

    Returns:
        True agar muvaffaqiyatli o'rnatilsa.
    """
    name = import_name or package_name
    try:
        __import__(name)
        return True
    except ImportError:
        pass

    print(f"\n⏳ '{package_name}' kutubxonasi o'rnatilmoqda...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package_name, "--quiet"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"✅ '{package_name}' muvaffaqiyatli o'rnatildi!")
        return True
    except subprocess.CalledProcessError:
        # --user bilan urinib ko'rish (ba'zi muhitlarda kerak)
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--user", package_name, "--quiet"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"✅ '{package_name}' muvaffaqiyatli o'rnatildi!")
            return True
        except Exception:
            pass
    except FileNotFoundError:
        pass

    print(f"❌ '{package_name}' ni o'rnatib bo'lmadi!")
    print(f"   Qo'lda o'rnating: pip install {package_name}")
    return False


# Kerakli kutubxonalar
_REQUIRED = [
    ("telethon", "telethon"),
    ("rich", "rich"),
    ("pyfiglet", "pyfiglet"),
]

_all_ok = True
for _pkg, _imp in _REQUIRED:
    if not _install_package(_pkg, _imp):
        _all_ok = False

if not _all_ok:
    print("\n❌ Ba'zi kutubxonalar o'rnatilmadi. Dastur ishlay olmaydi.")
    print("Qo'lda o'rnating: pip install telethon rich pyfiglet")
    input("\nChiqish uchun Enter bosing...")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# 2-QADAM: IMPORTLAR
# ═══════════════════════════════════════════════════════════════════════════════

import asyncio
import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any

from telethon import TelegramClient
from telethon.errors import (
    ChatAdminRequiredError,
    FloodWaitError,
    InputUserDeactivatedError,
    PeerFloodError,
    UserAlreadyParticipantError,
    UserBannedInChannelError,
    UserKickedError,
    UserNotMutualContactError,
    UserPrivacyRestrictedError,
)
from telethon.tl.functions.channels import (
    GetParticipantsRequest,
    InviteToChannelRequest,
)
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.types import (
    Channel,
    ChannelParticipantsSearch,
    Chat,
    User,
)

import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
from rich.text import Text
from rich import box


# ═══════════════════════════════════════════════════════════════════════════════
# 3-QADAM: SOZLAMALAR VA KONSTANTALAR
# ═══════════════════════════════════════════════════════════════════════════════

CONFIG_FILE = "kerakli.json"
LOG_FILE = "adder.log"
PARTICIPANTS_PER_PAGE = 200

# Standart tezlik sozlamalari (foydalanuvchi o'zgartirishi mumkin)
DEFAULT_DELAY_MIN = 25
DEFAULT_DELAY_MAX = 35

# ─── Logger ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")],
)
logger = logging.getLogger(__name__)

# ─── Console ─────────────────────────────────────────────────────────────────

console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# 4-QADAM: YORDAMCHI FUNKSIYALAR
# ═══════════════════════════════════════════════════════════════════════════════


def clear_screen() -> None:
    """Terminalni tozalaydi (Windows, Linux, Termux, Pydroid uchun)."""
    if os.name == "nt":
        os.system("cls")
    else:
        # Termux, Linux, macOS, Pydroid
        try:
            os.system("clear")
        except Exception:
            # Agar hech biri ishlamasa — 50 ta bo'sh qator
            print("\n" * 50)


def display_banner() -> None:
    """Dastur bannerini chiroyli ko'rinishda chiqaradi."""
    try:
        ascii_art = pyfiglet.figlet_format("Obunachi", font="slant")
        console.print(Text(ascii_art, style="bold cyan"))
    except Exception:
        # pyfiglet shriftni topa olmasa
        console.print("[bold cyan]═══ OBUNACHI ═══[/]\n")

    console.print(
        Panel(
            "[bold yellow]Telegram Guruh A'zo Qo'shuvchi[/]\n"
            "[dim]Guruh/kanaldan a'zolarni boshqa guruhga ko'chiradi[/]",
            border_style="blue",
            padding=(0, 2),
        )
    )
    console.print()


# ═══════════════════════════════════════════════════════════════════════════════
# 5-QADAM: RISK DISCLAIMER (JAVOBGARLIK OGOHLANTIRISHI)
# ═══════════════════════════════════════════════════════════════════════════════


def _load_json(path: Path) -> dict[str, Any]:
    """JSON faylni xavfsiz yuklaydi."""
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_json(path: Path, data: dict[str, Any]) -> None:
    """JSON faylni xavfsiz saqlaydi."""
    try:
        path.write_text(
            json.dumps(data, indent=4, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as e:
        console.print(f"[red]⚠ Faylni saqlashda xatolik: {e}[/]")


def check_disclaimer() -> bool:
    """Foydalanuvchi risklarni qabul qilganini tekshiradi.

    Rozilik ma'lumoti kerakli.json ichida saqlanadi (alohida fayl kerak emas).

    Returns:
        True agar foydalanuvchi rozilik bergan bo'lsa.
    """
    config = _load_json(Path(CONFIG_FILE))

    # Oldin qabul qilganmi?
    if config.get("disclaimer_accepted") is True:
        return True

    # Ogohlantirish paneli
    console.print(
        Panel(
            "[bold red]⚠️  MUHIM OGOHLANTIRISH — DIQQAT BILAN O'QING![/]\n"
            "\n"
            "[bold yellow]Ushbu dastur Telegram API orqali boshqa foydalanuvchilarni\n"
            "guruh/kanalga qo'shish uchun mo'ljallangan.[/]\n"
            "\n"
            "[white]Dasturdan foydalanish bilan siz quyidagilarni tan olasiz:[/]\n"
            "\n"
            "  [red]1.[/] Telegram ToS (Foydalanish Shartlari) buzilishi mumkin.\n"
            "     [dim]Akkauntingiz vaqtincha yoki doimiy bloklanishi mumkin.[/]\n"
            "\n"
            "  [red]2.[/] Boshqa foydalanuvchilarni ruxsatisiz qo'shish ularning\n"
            "     shaxsiy hayotiga tajovuz hisoblanishi mumkin.\n"
            "\n"
            "  [red]3.[/] Telegram akkauntingizga FloodWait, PeerFlood yoki\n"
            "     doimiy cheklovlar qo'yishi mumkin.\n"
            "\n"
            "  [red]4.[/] Ba'zi mamlakatlarda spam yoki ruxsatsiz xabar yuborish\n"
            "     qonunga zid bo'lishi mumkin.\n"
            "\n"
            "  [red]5.[/] Dastur yaratuvchilari hech qanday javobgarlik\n"
            "     o'z zimmasiga olmaydi. Barcha risklar sizning bo'yningizda.\n"
            "\n"
            "[bold]Davom etish uchun [green]ROZIMAN[/] deb yozing.\n"
            "Bekor qilish uchun boshqa narsa yozing yoki Ctrl+C bosing.[/]",
            title="[bold red]📜 JAVOBGARLIK HAQIDA OGOHLANTIRISH[/]",
            border_style="red",
            padding=(1, 3),
        )
    )

    console.print()
    answer = Prompt.ask("  [bold]Javobingiz[/]").strip()

    if answer == "ROZIMAN":
        config["disclaimer_accepted"] = True
        config["disclaimer_date"] = datetime.now().isoformat()
        _save_json(Path(CONFIG_FILE), config)
        console.print("  [green]✔ Rozilik qabul qilindi. Dastur davom etadi.[/]\n")
        logger.info("Foydalanuvchi risk disclaimerini qabul qildi")
        return True

    console.print("  [red]✘ Rozilik berilmadi. Dastur tugatildi.[/]\n")
    logger.info("Foydalanuvchi risk disclaimerini rad etdi")
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# 6-QADAM: KONFIGURATSIYA BOSHQARUVI
# ═══════════════════════════════════════════════════════════════════════════════


def load_config() -> dict[str, Any]:
    """Konfiguratsiya faylini yuklaydi va etishmagan maydonlarni so'raydi.

    Returns:
        To'liq konfiguratsiya lug'ati.
    """
    config = _load_json(Path(CONFIG_FILE))

    fields = {
        "api_id": "🔑 API_ID kiriting (raqam)",
        "api_hash": "🔐 API_HASH kiriting",
        "manba": "📥 A'zolar olinadigan guruh/kanal (havola yoki username)",
        "maqsad": "📤 A'zolar qo'shiladigan guruh/kanal (havola yoki username)",
    }

    for key, prompt_text in fields.items():
        while key not in config or not str(config[key]).strip():
            value = Prompt.ask(f"  {prompt_text}").strip()
            if not value:
                console.print("  [red]✘ Bu maydon bo'sh bo'lishi mumkin emas![/]")
                continue
            if key == "api_id":
                if not value.isdigit():
                    console.print("  [red]✘ API_ID faqat raqam bo'lishi kerak![/]")
                    continue
            config[key] = value

    # Tezlik sozlamalari (standart qiymatlar)
    if "delay_min" not in config:
        config["delay_min"] = DEFAULT_DELAY_MIN
    if "delay_max" not in config:
        config["delay_max"] = DEFAULT_DELAY_MAX

    _save_json(Path(CONFIG_FILE), config)
    return config


def edit_config(config: dict[str, Any]) -> dict[str, Any]:
    """Konfiguratsiyani interaktiv tarzda tahrirlash.

    Args:
        config: Joriy konfiguratsiya.

    Returns:
        Yangilangan konfiguratsiya.
    """
    console.print("\n[bold]⚙️  Sozlamalarni Tahrirlash[/]\n")

    labels = {
        "api_id": "API_ID",
        "api_hash": "API_HASH",
        "manba": "Manba guruh/kanal",
        "maqsad": "Maqsad guruh/kanal",
    }

    table = Table(title="Joriy Sozlamalar", box=box.ROUNDED)
    table.add_column("#", style="dim", width=3)
    table.add_column("Parametr", style="cyan")
    table.add_column("Qiymat", style="green")

    keys = list(labels.keys())
    for i, key in enumerate(keys, 1):
        val = str(config.get(key, "[yo'q]"))
        if key == "api_hash" and len(val) > 8:
            val = val[:4] + "..." + val[-4:]
        table.add_row(str(i), labels[key], val)

    console.print(table)
    console.print()

    choice = Prompt.ask(
        "O'zgartirmoqchi bo'lgan parametr raqami (yoki [bold]0[/] — ortga)",
        default="0",
    )

    if choice == "0":
        return config

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(keys):
            key = keys[idx]
            new_val = Prompt.ask(f"  Yangi qiymat ({labels[key]})").strip()
            if new_val:
                if key == "api_id" and not new_val.isdigit():
                    console.print("  [red]✘ API_ID faqat raqam bo'lishi kerak![/]")
                else:
                    config[key] = new_val
                    _save_json(Path(CONFIG_FILE), config)
                    console.print(f"  [green]✔ {labels[key]} yangilandi![/]")
            else:
                console.print("  [yellow]⚠ Bo'sh qiymat — o'zgarish bekor qilindi.[/]")
        else:
            console.print("  [red]✘ Noto'g'ri raqam![/]")
    except ValueError:
        console.print("  [red]✘ Raqam kiriting![/]")

    return config


def edit_speed(config: dict[str, Any]) -> dict[str, Any]:
    """Qo'shish tezligini sozlash.

    Args:
        config: Joriy konfiguratsiya.

    Returns:
        Yangilangan konfiguratsiya.
    """
    console.print("\n[bold]⏱️  Qo'shish Tezligini Sozlash[/]\n")

    current_min = config.get("delay_min", DEFAULT_DELAY_MIN)
    current_max = config.get("delay_max", DEFAULT_DELAY_MAX)

    console.print(
        Panel(
            f"[white]Hozirgi sozlama:[/] har bir a'zo orasida "
            f"[bold cyan]{current_min}[/] — [bold cyan]{current_max}[/] sekund kutiladi.\n"
            "\n"
            "[bold yellow]⚡ Tezroq[/] = ko'proq a'zo, lekin [red]ban xavfi yuqori[/]\n"
            "[bold green]🐢 Sekinroq[/] = kamroq a'zo, lekin [green]xavfsizroq[/]\n"
            "\n"
            "[dim]Tavsiya: kamida 20 sekund. 10 sekunddan kam — ban xavfi juda yuqori![/]",
            title="[bold]Tezlik Sozlamalari[/]",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    presets = Table(box=box.SIMPLE, show_header=True)
    presets.add_column("#", style="dim", width=3)
    presets.add_column("Rejim", style="bold")
    presets.add_column("Kutish", style="cyan")
    presets.add_column("Xavf", justify="center")

    presets.add_row("1", "🐢 Xavfsiz",   "30-45 sek", "[green]■[/][dim]■■■■[/]")
    presets.add_row("2", "📗 Tavsiya",    "20-35 sek", "[green]■■[/][dim]■■■[/]")
    presets.add_row("3", "⚡ Tez",        "12-20 sek", "[yellow]■■■[/][dim]■■[/]")
    presets.add_row("4", "🔥 Juda tez",   "5-12 sek",  "[red]■■■■[/][dim]■[/]")
    presets.add_row("5", "✏️  Qo'lda",    "o'zim belgilayman", "[dim]—[/]")

    console.print(presets)
    console.print()

    choice = Prompt.ask(
        "  Rejim tanlang (yoki [bold]0[/] — ortga)",
        choices=["0", "1", "2", "3", "4", "5"],
        default="0",
    )

    speed_map = {
        "1": (30, 45),
        "2": (20, 35),
        "3": (12, 20),
        "4": (5, 12),
    }

    if choice == "0":
        return config

    if choice in speed_map:
        config["delay_min"], config["delay_max"] = speed_map[choice]
    elif choice == "5":
        try:
            new_min = IntPrompt.ask("  Minimal kutish (sekund)", default=current_min)
            new_max = IntPrompt.ask("  Maksimal kutish (sekund)", default=current_max)
            if new_min < 1:
                new_min = 1
            if new_max < new_min:
                new_max = new_min + 1
            config["delay_min"] = new_min
            config["delay_max"] = new_max
        except Exception:
            console.print("  [red]✘ Noto'g'ri qiymat![/]")
            return config

    _save_json(Path(CONFIG_FILE), config)

    console.print(
        f"\n  [green]✔ Tezlik sozlandi:[/] "
        f"[bold]{config['delay_min']}[/] — [bold]{config['delay_max']}[/] sekund\n"
    )
    return config


# ═══════════════════════════════════════════════════════════════════════════════
# 7-QADAM: A'ZOLARNI OLISH (PAGINATION)
# ═══════════════════════════════════════════════════════════════════════════════


async def get_all_participants(
    client: TelegramClient, entity: Channel
) -> list[User]:
    """Kanal/guruhdan barcha a'zolarni pagination bilan oladi.

    Args:
        client: Telegram client.
        entity: Kanal yoki megagroup entity.

    Returns:
        Botlardan va o'chirilganlardan tashqari barcha foydalanuvchilar.
    """
    all_users: list[User] = []
    offset = 0

    console.print("  [cyan]⏳ A'zolar ro'yxati yuklanmoqda...[/]")

    while True:
        try:
            result = await client(
                GetParticipantsRequest(
                    channel=entity,
                    filter=ChannelParticipantsSearch(""),
                    offset=offset,
                    limit=PARTICIPANTS_PER_PAGE,
                    hash=0,
                )
            )
        except ChatAdminRequiredError:
            console.print(
                "  [red]✘ A'zolar ro'yxatini olish uchun admin huquqi kerak![/]"
            )
            logger.error("A'zolar ro'yxatini olishda admin huquqi yo'q")
            break
        except FloodWaitError as e:
            console.print(
                f"  [yellow]⏳ Telegram cheklovi — {e.seconds} sek kutilmoqda...[/]"
            )
            logger.warning("FloodWait (participants): %d sek", e.seconds)
            await asyncio.sleep(e.seconds + 1)
            continue
        except Exception as e:
            console.print(f"  [red]✘ A'zolarni olishda xatolik: {e}[/]")
            logger.error("A'zolarni olishda xatolik: %s", e)
            break

        if not result.users:
            break

        for user in result.users:
            if not user.bot and not user.deleted:
                all_users.append(user)

        offset += len(result.users)

        if len(result.users) < PARTICIPANTS_PER_PAGE:
            break

    console.print(f"  [green]✔ Jami {len(all_users)} ta a'zo topildi[/]")
    logger.info("Jami %d ta a'zo topildi", len(all_users))
    return all_users


# ═══════════════════════════════════════════════════════════════════════════════
# 8-QADAM: A'ZOLARNI QO'SHISH (ASOSIY FUNKSIYA)
# ═══════════════════════════════════════════════════════════════════════════════


async def add_users_to_target(
    client: TelegramClient,
    users: list[User],
    target_entity: Channel | Chat,
    is_megagroup_or_channel: bool,
    delay_min: int,
    delay_max: int,
) -> dict[str, int]:
    """Foydalanuvchilarni maqsad guruh/kanalga qo'shadi.

    Args:
        client: Telegram client.
        users: Qo'shiladigan foydalanuvchilar.
        target_entity: Maqsad guruh/kanal.
        is_megagroup_or_channel: True agar supergroup/kanal.
        delay_min: Minimal kutish (sekund).
        delay_max: Maksimal kutish (sekund).

    Returns:
        Statistika lug'ati.
    """
    stats = {"added": 0, "skipped": 0, "failed": 0, "flood_waited": 0}
    stop_requested = False

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=25),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        console=console,
    )

    with progress:
        task = progress.add_task("[cyan]A'zo qo'shilmoqda...", total=len(users))

        for i, user in enumerate(users):
            if stop_requested:
                break

            display_name = user.first_name or user.username or str(user.id)

            try:
                if is_megagroup_or_channel:
                    await client(InviteToChannelRequest(target_entity, [user]))
                else:
                    await client(
                        AddChatUserRequest(
                            chat_id=target_entity.id,
                            user_id=user,
                            fwd_limit=10,
                        )
                    )

                stats["added"] += 1
                progress.update(task, description=f"[green]✔ {display_name}", advance=1)
                logger.info("Qo'shildi: %s (ID: %d)", display_name, user.id)

            except UserAlreadyParticipantError:
                stats["skipped"] += 1
                progress.update(task, description=f"[yellow]⊘ {display_name} (a'zo)", advance=1)
                logger.info("O'tkazildi: %s (allaqachon a'zo)", display_name)
                continue

            except UserPrivacyRestrictedError:
                stats["failed"] += 1
                progress.update(task, description=f"[dim]🔒 {display_name}", advance=1)
                logger.info("Rad: %s (privacy)", display_name)

            except UserNotMutualContactError:
                stats["failed"] += 1
                progress.update(task, description=f"[dim]📵 {display_name}", advance=1)
                logger.info("Rad: %s (kontakt emas)", display_name)

            except (UserKickedError, UserBannedInChannelError):
                stats["failed"] += 1
                progress.update(task, description=f"[red]🚫 {display_name}", advance=1)
                logger.info("Rad: %s (ban/kick)", display_name)

            except InputUserDeactivatedError:
                stats["failed"] += 1
                progress.update(task, description=f"[dim]💀 {display_name}", advance=1)
                logger.info("Rad: %s (deaktiv)", display_name)

            except FloodWaitError as e:
                stats["flood_waited"] += 1
                wait_secs = e.seconds + random.randint(1, 5)
                progress.update(task, description=f"[yellow]⏳ FloodWait {wait_secs}s...")
                logger.warning("FloodWait: %d sek (%s)", wait_secs, display_name)
                await asyncio.sleep(wait_secs)
                # Qayta urinish
                try:
                    if is_megagroup_or_channel:
                        await client(InviteToChannelRequest(target_entity, [user]))
                    else:
                        await client(AddChatUserRequest(chat_id=target_entity.id, user_id=user, fwd_limit=10))
                    stats["added"] += 1
                    progress.update(task, advance=1)
                    logger.info("Qo'shildi (retry): %s", display_name)
                except Exception as retry_err:
                    stats["failed"] += 1
                    progress.update(task, advance=1)
                    logger.error("Retry xatolik (%s): %s", display_name, retry_err)

            except PeerFloodError:
                console.print("\n  [bold red]🚨 Akkaunt vaqtincha cheklandi (PeerFlood)![/]")
                console.print("  [yellow]Bir necha soatdan keyin urinib ko'ring.[/]")
                logger.error("PeerFloodError — to'xtatildi")
                stop_requested = True
                progress.update(task, advance=1)
                continue

            except ChatAdminRequiredError:
                console.print("\n  [bold red]🚨 Admin huquqi kerak![/]")
                logger.error("ChatAdminRequiredError — to'xtatildi")
                stop_requested = True
                progress.update(task, advance=1)
                continue

            except Exception as e:
                stats["failed"] += 1
                progress.update(task, description=f"[red]✘ {display_name}", advance=1)
                logger.error("Xatolik (%s): %s", display_name, e)

            # Keyingi foydalanuvchiga o'tishdan oldin kutish
            if i < len(users) - 1 and not stop_requested:
                delay = random.uniform(delay_min, delay_max)
                await asyncio.sleep(delay)

    return stats


def display_stats(stats: dict[str, int]) -> None:
    """Natija statistikasini jadval ko'rinishida chiqaradi."""
    table = Table(title="📊 Natijalar", box=box.ROUNDED, title_style="bold magenta")
    table.add_column("Ko'rsatkich", style="cyan")
    table.add_column("Soni", justify="right", style="bold")

    rows = [
        ("✅ Qo'shildi", str(stats["added"]), "green"),
        ("⊘ O'tkazildi (allaqachon a'zo)", str(stats["skipped"]), "yellow"),
        ("❌ Rad etildi / xatolik", str(stats["failed"]), "red"),
        ("⏳ FloodWait kutishlar", str(stats["flood_waited"]), "yellow"),
    ]
    for label, count, color in rows:
        table.add_row(label, f"[{color}]{count}[/]")

    console.print()
    console.print(table)
    console.print()


# ═══════════════════════════════════════════════════════════════════════════════
# 9-QADAM: ASOSIY OQIM
# ═══════════════════════════════════════════════════════════════════════════════


async def run_adder(config: dict[str, Any]) -> None:
    """A'zo qo'shish jarayonini boshqaradi."""
    api_id = int(config["api_id"])
    api_hash = config["api_hash"]
    source_chat = config["manba"]
    target_chat = config["maqsad"]
    delay_min = config.get("delay_min", DEFAULT_DELAY_MIN)
    delay_max = config.get("delay_max", DEFAULT_DELAY_MAX)

    session_name = f"session_{api_id}"

    async with TelegramClient(session_name, api_id, api_hash) as client:
        console.print("\n  [green]✔ Telegram ga ulanildi![/]\n")
        logger.info("Telegram ga ulanildi (api_id: %d)", api_id)

        # Manba va maqsadni olish
        try:
            source_entity = await client.get_entity(source_chat)
            target_entity = await client.get_entity(target_chat)
        except ValueError as e:
            console.print(f"  [red]✘ Guruh/kanal topilmadi: {e}[/]")
            console.print("  [dim]Havola/username to'g'ri ekanligini tekshiring.[/]")
            logger.error("Entity topilmadi: %s", e)
            return
        except Exception as e:
            console.print(f"  [red]✘ Ulanishda xatolik: {e}[/]")
            logger.error("Entity olishda xatolik: %s", e)
            return

        is_source_channel = isinstance(source_entity, Channel)
        is_target_channel = isinstance(target_entity, Channel)

        if not is_source_channel:
            console.print(
                "  [red]✘ Manba oddiy guruh — faqat supergroup/kanaldan olish mumkin![/]"
            )
            console.print("  [dim]Guruhni superguruhga aylantiring yoki boshqa manba tanlang.[/]")
            logger.error("Manba oddiy guruh")
            return

        # Ma'lumotni ko'rsatish
        source_title = getattr(source_entity, "title", source_chat)
        target_title = getattr(target_entity, "title", target_chat)

        info_table = Table(box=box.SIMPLE)
        info_table.add_column("", style="dim")
        info_table.add_column("", style="bold")
        info_table.add_row("📥 Manba", source_title)
        info_table.add_row("📤 Maqsad", target_title)
        info_table.add_row("🎯 Turi", "Supergroup/Kanal" if is_target_channel else "Oddiy guruh")
        info_table.add_row("⏱️  Tezlik", f"{delay_min}-{delay_max} sek")
        console.print(Panel(info_table, title="[bold]Operatsiya Tafsilotlari[/]"))

        # A'zolarni olish
        users = await get_all_participants(client, source_entity)
        if not users:
            console.print("  [yellow]⚠ Qo'shiladigan a'zo topilmadi![/]")
            return

        # Taxminiy vaqt
        avg_delay = (delay_min + delay_max) / 2
        est_minutes = int(len(users) * avg_delay / 60)
        console.print(f"\n  [bold]{len(users)}[/] ta a'zo topildi.")
        console.print(f"  [dim]Taxminiy vaqt: ~{est_minutes} daqiqa ({delay_min}-{delay_max} sek/a'zo)[/]")

        if not Confirm.ask("\n  Davom etasizmi?", default=True):
            console.print("  [yellow]Bekor qilindi.[/]")
            return

        console.print()
        logger.info("Qo'shish boshlandi: %s -> %s (%d a'zo)", source_title, target_title, len(users))

        stats = await add_users_to_target(
            client=client,
            users=users,
            target_entity=target_entity,
            is_megagroup_or_channel=is_target_channel,
            delay_min=delay_min,
            delay_max=delay_max,
        )

        display_stats(stats)
        logger.info(
            "Tugadi — qo'shildi: %d, o'tkazildi: %d, xatolik: %d",
            stats["added"], stats["skipped"], stats["failed"],
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 10-QADAM: INTERAKTIV MENYU
# ═══════════════════════════════════════════════════════════════════════════════


async def main() -> None:
    """Dasturning asosiy interaktiv menyu sikli."""
    clear_screen()
    display_banner()

    # Risk disclaimer — rozilik bo'lmasa dastur ishlamaydi
    if not check_disclaimer():
        return

    config = load_config()

    while True:
        delay_min = config.get("delay_min", DEFAULT_DELAY_MIN)
        delay_max = config.get("delay_max", DEFAULT_DELAY_MAX)

        console.print(
            Panel(
                "[bold]1[/] 👥  A'zo qo'shishni boshlash\n"
                "[bold]2[/] ⚙️   Sozlamalarni o'zgartirish\n"
                f"[bold]3[/] ⏱️   Tezlikni sozlash  [dim]({delay_min}-{delay_max} sek)[/]\n"
                "[bold]4[/] 📋  Joriy sozlamalarni ko'rish\n"
                "[bold]5[/] 🚪  Chiqish",
                title="[bold blue]📋 Menyu[/]",
                border_style="blue",
                padding=(1, 3),
            )
        )

        choice = Prompt.ask(
            "  Tanlovingiz",
            choices=["1", "2", "3", "4", "5"],
            default="1",
        )

        if choice == "1":
            await run_adder(config)
            console.print("\n  [dim]Menyuga qaytish uchun Enter bosing...[/]")
            input()
            clear_screen()
            display_banner()

        elif choice == "2":
            config = edit_config(config)
            console.print()

        elif choice == "3":
            config = edit_speed(config)

        elif choice == "4":
            table = Table(title="Joriy Sozlamalar", box=box.ROUNDED, title_style="bold cyan")
            table.add_column("Parametr", style="cyan")
            table.add_column("Qiymat", style="green")

            display_config = {
                "API_ID": config.get("api_id", "[yo'q]"),
                "API_HASH": config.get("api_hash", "[yo'q]"),
                "Manba": config.get("manba", "[yo'q]"),
                "Maqsad": config.get("maqsad", "[yo'q]"),
                "Tezlik (min)": f"{config.get('delay_min', DEFAULT_DELAY_MIN)} sek",
                "Tezlik (max)": f"{config.get('delay_max', DEFAULT_DELAY_MAX)} sek",
            }
            for k, v in display_config.items():
                v = str(v)
                if k == "API_HASH" and len(v) > 8:
                    v = v[:4] + "..." + v[-4:]
                table.add_row(k, v)

            console.print(table)
            console.print()

        elif choice == "5":
            console.print("  [bold green]👋 Xayr! Dastur tugatildi.[/]\n")
            break


# ═══════════════════════════════════════════════════════════════════════════════
# ISHGA TUSHIRISH
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n  [bold red]⛔ Dastur to'xtatildi (Ctrl+C)[/]")
        logger.info("Dastur to'xtatildi (Ctrl+C)")
        sys.exit(0)
