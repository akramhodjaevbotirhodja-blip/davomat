# Davomat — xodimlar kelish-ketish nazorati

QR-kod orqali ishlaydigan davomat tizimi. Proyektor/televizorda har 30 soniyada
yangilanadigan QR kod turadi, xodimlar telefon kamerasi bilan skanerlab
ismini bosadi — kelish va ketish vaqti avtomatik yoziladi.

---

## 1. Ishga tushirish

**`ISHGA TUSHIRISH.bat`** faylini ikki marta bosing.

Ochilgan qora oynada manzillar chiqadi:

```
============================================================
  DAVOMAT TIZIMI ishga tushdi
  Proyektor ekrani : http://192.168.x.x:8000/projector
  Admin panel      : http://192.168.x.x:8000/admin
============================================================
```

> ⚠️ **Bu oynani yopmang** — server shu yerda ishlaydi. Yopsangiz tizim to'xtaydi.

| Sahifa | Manzil | Kim ochadi |
|---|---|---|
| Proyektor ekrani | `/projector` | Ofis kompyuteri → proyektor/TV |
| Admin panel | `/admin` | Rahbar / kadrlar bo'limi |
| Xodim sahifasi | QR orqali avtomatik | Xodim telefoni |

Boshlang'ich admin paroli: **`admin`** — birinchi kirishdanoq
*Sozlamalar* bo'limida o'zgartiring.

---

## 2. Birinchi sozlash (bir marta)

1. `/admin` ga kiring, parol: `admin`
2. **Sozlamalar** → kompaniya nomi, ish boshlanish vaqti (masalan `09:00`),
   kechikish chegarasi (masalan `5` daqiqa), yangi parol
3. **Xodimlar** → barcha xodimlarni qo'shing (F.I.Sh. majburiy, qolgani ixtiyoriy)
4. **Proyektor** tugmasi → ochilgan sahifani proyektorga chiqaring va `F11`
   bilan to'liq ekranga o'tkazing

---

## 3. Kundalik ishlash tartibi

**Ertalab:** proyektor ekrani yoqiladi. Xodim kiradi → telefon kamerasini QR-ga
qaratadi → ochilgan ro'yxatdan ismini bosadi → «Xush kelibsiz» yozuvi chiqadi.

**Kechqurun:** xuddi shu QR-ni skanerlaydi, endi ismining yonida «Ketdim»
tugmasi turadi. Ishlagan vaqt avtomatik hisoblanadi.

**Rahbar:** `/admin` → *Bugun* bo'limida kim keldi, kim kechikdi, kim kelmadi —
jonli ko'rinadi.

---

## 4. Nima uchun QR har 30 soniyada yangilanadi

QR koddagi manzil maxfiy kalit bilan imzolanadi va faqat **90 soniya** amal qiladi.
Ya'ni xodim QR-ni rasmga olib uydagi hamkasbiga yuborsa ham foyda bermaydi —
kod allaqachon eskirgan bo'ladi.

Bundan tashqari server **lokal tarmoqda** ishlaydi: telefon ofis Wi-Fi'ga
ulangan bo'lishi shart. Uydan turib belgilash imkonsiz.

Xodimlar faqat ismini tanlaydi (PIN yo'q), shuning uchun qo'shimcha himoya bor:
agar **bitta telefondan** bir soat ichida bir nechta xodim belgilansa, o'sha
yozuvlar admin panelda **⚠** belgisi bilan chiqadi. Chegarani *Sozlamalar*da
o'zgartirasiz.

---

## 5. Admin panel bo'limlari

### Bugun
Kunlik jadval: holat, kelgan/ketgan vaqt, kechikish, ishlangan soat.
- `← Oldingi` / `Keyingi →` — boshqa kunlarni ko'rish
- **Tahrirlash** — vaqtni qo'lda tuzatish (telefoni o'chib qolgan xodim uchun).
  Kelish vaqtini bo'sh qoldirib saqlasangiz — kun yozuvi o'chadi.
- **⚠** — bitta telefondan ko'p odam belgilangan, tekshirish kerak
- **✎** — yozuv qo'lda kiritilgan

### Hisobot
Istalgan davr uchun ikki xil ko'rinish:
- **Yig'ma** — har bir xodim bo'yicha: necha kun keldi, kechikdi, kelmadi,
  jami kechikish daqiqalari, jami ishlangan soat
- **Kunlik jadval** — rangli katakcha jadvali (yashil — o'z vaqtida,
  sariq — kechikdi, qizil — kelmadi, ko'k — sababli)

`⬇ Excel` tugmasi ikki varaqli `.xlsx` fayl beradi — oylik hisobot yoki
oylik maosh hisoblash uchun.

### Xodimlar
Qo'shish, tahrirlash, faol/nofaol qilish.

> Ishdan bo'shagan xodimni **o'chirmang** — **nofaol** qiling. O'chirish uning
> barcha eski davomat yozuvlarini ham yo'q qiladi.

### Yo'qliklar
Ta'til, kasallik, komandirovka, boshqa sabab. Belgilangan kunlarda xodim
«kelmadi» emas, tanlangan sabab bilan chiqadi va hisobotda alohida hisoblanadi.

---

## 6. Telefonlar ulanmayapti?

Odatda sabab — **Windows xavfsizlik devori** 8000-portni to'sib qo'ygan.

PowerShell'ni **administrator** nomidan oching va bir marta bajaring:

```powershell
New-NetFirewallRule -DisplayName "Davomat" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Private
```

Boshqa tekshiruvlar:
- Telefon va kompyuter **bitta Wi-Fi**da bo'lsin
- Kompyuter IP manzili o'zgargan bo'lishi mumkin. Qora oynadagi manzilni
  *Sozlamalar → QR koddagi manzil* maydoniga yozing.
- Router'da "Client isolation" / "AP isolation" o'chirilgan bo'lsin

**Maslahat:** kompyuterga routerda doimiy IP (DHCP reservation) biriktiring —
shunda manzil hech qachon o'zgarmaydi.

---

## 7. Ma'lumotlar qayerda saqlanadi

Hammasi bitta faylda: **`data/davomat.db`**

Zaxira nusxa olish — shu faylni ko'chirib qo'yish kifoya. Serverni to'xtatib
`data` papkasini butunlay ko'chiring (`davomat.db` yonidagi `-wal` va `-shm`
fayllari bilan birga).

Agar tizimni noldan boshlamoqchi bo'lsangiz: serverni to'xtating va `data`
papkasidagi fayllarni o'chiring — keyingi ishga tushishda bo'sh baza yaratiladi.

---

## 8. Texnik ma'lumot

- Python 3.12 + FastAPI + SQLite, tashqi xizmatlarga bog'liq emas
- Internet talab qilinmaydi, oylik to'lov yo'q
- Kutubxonalarni qayta o'rnatish kerak bo'lsa: `pip install -r requirements.txt`

Fayllar:

```
app/main.py        — barcha sahifalar va mantiq
app/db.py          — baza sxemasi
app/security.py    — QR token imzolash (HMAC)
app/config.py      — vaqt zonasi, QR yangilanish davri, statuslar
app/templates/     — sahifalar
app/static/        — dizayn
data/davomat.db    — ma'lumotlar bazasi
```

Keyinchalik tizimni internetga chiqarmoqchi bo'lsangiz — kod o'zgarmaydi,
faqat `/admin → Sozlamalar → QR koddagi manzil` ni tashqi domenga
almashtirasiz (va HTTPS orqasiga qo'yasiz).
