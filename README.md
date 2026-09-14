# 📡 Tg-obunachi — Telegram Guruh A'zo Qo'shuvchi

Telegram guruh va kanallardan a'zolarni boshqa guruh/kanalga ko'chiruvchi dastur.

## ⚡ Xususiyatlari

- 🔄 Guruh/kanaldan barcha a'zolarni olish (pagination bilan)
- 👥 A'zolarni boshqa guruh/kanalga qo'shish
- 📊 Real-time progress bar
- 🛡️ FloodWait va Telegram limitlarini avtomatik boshqarish
- 📝 Barcha harakatlar log faylga yoziladi
- 🎨 Chiroyli terminal interfeys (rich kutubxonasi)
- ⚙️ Interaktiv menyu orqali oson boshqarish

## 📦 O'rnatish

### 1. Repo ni klonlash
```bash
git clone https://github.com/Kingprogrammer07/Tg-obunachi.git
cd Tg-obunachi
```

### 2. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3. Telegram API ma'lumotlarini olish
1. [my.telegram.org](https://my.telegram.org) saytiga kiring
2. **API Development Tools** bo'limiga o'ting
3. `API_ID` va `API_HASH` ni ko'chirib oling

## 🚀 Ishlatish

```bash
python group_adder.py
```

### Menyu
1. **👥 A'zo qo'shishni boshlash** — manba guruhdan maqsad guruhga a'zo ko'chirish
2. **⚙️ Sozlamalarni o'zgartirish** — API yoki guruh ma'lumotlarini yangilash
3. **📊 Statistika** — oldingi operatsiyalar haqida ma'lumot
4. **🚪 Chiqish** — dasturdan chiqish

### Birinchi ishga tushirish
Dastur sizdan quyidagi ma'lumotlarni so'raydi:
- `API_ID` — Telegram API ID (raqam)
- `API_HASH` — Telegram API Hash
- **Manba guruh** — a'zolarni olish uchun guruh/kanal havolasi
- **Maqsad guruh** — a'zolarni qo'shish uchun guruh/kanal havolasi

## ⚠️ Muhim Eslatmalar

- Telegram qo'shish limitlari bor — kuniga ~20-50 ta foydalanuvchi
- `FloodWait` xatoligi bo'lsa dastur avtomatik kutadi
- Privacy sozlamalari tufayli ba'zi foydalanuvchilarni qo'shib bo'lmaydi
- `Ctrl+C` bosilganda dastur xavfsiz tarzda to'xtaydi

## 📁 Fayl Tuzilmasi

```
Tg_obunachi/
├── group_adder.py      # Asosiy dastur
├── requirements.txt    # Kutubxonalar ro'yxati
├── .gitignore          # Git ignore qoidalari
├── README.md           # Hujjat (siz o'qiyapsiz)
├── kerakli.json        # Sozlamalar (avtomatik yaratiladi)
└── adder.log           # Log fayl (avtomatik yaratiladi)
```

## 📜 Litsenziya

Ochiq manba. Erkin foydalanishingiz mumkin.
