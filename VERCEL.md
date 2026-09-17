# Vercel'ga chiqarish

Tizim ikki rejimda ishlaydi va **bitta kod** bilan:

| | Lokal (ofis kompyuteri) | Bulut (Vercel) |
|---|---|---|
| Baza | `data/davomat.db` (SQLite) | Neon PostgreSQL |
| Belgilash sharti | ofis Wi-Fi'ida bo'lish | GPS — ofis hududida bo'lish |
| Ishga tushirish | `ISHGA TUSHIRISH.bat` | doim ishlab turadi |

Farqni `DATABASE_URL` muhit o'zgaruvchisi hal qiladi: bor bo'lsa — Postgres,
yo'q bo'lsa — SQLite. Ya'ni bulutga chiqargandan keyin ham ofis varianti
ishlayveradi.

---

## 1-qadam. Neon'da baza yaratish (5 daqiqa)

1. [neon.com](https://neon.com) → **Sign up** (GitHub akkaunti bilan kirish mumkin)
2. **Create project** → nom: `davomat`, region: **Europe (Frankfurt)** yoki
   **AWS eu-central-1** (Toshkentga eng yaqini)
3. Ochilgan oynada **Connection string** ko'rinadi. Muhim: ro'yxatdan
   **`Pooled connection`** variantini tanlang — manzil ichida `-pooler` so'zi
   bo'lishi shart:

   ```
   postgresql://neondb_owner:PAROL@ep-xxxx-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require
   ```

   > Nega pooled? Vercel har so'rovga alohida ulanadi. Oddiy manzilda ulanishlar
   > soni tez tugaydi, pooled manzil esa shuning uchun qilingan.

4. Bu manzilni nusxalab qo'ying — keyingi qadamda kerak bo'ladi.

---

## 2-qadam. Kodni GitHub'ga yuklash — ✅ bajarildi

Repozitoriy tayyor: **https://github.com/akramhodjaevbotirhodja-blip/davomat**

Keyinchalik kodni o'zgartirsangiz, yangilash uchun:

```bash
git add -A; git commit -m "o'zgarish izohi"; git push
```

---

## 3-qadam. Vercel'ga ulash (5 daqiqa)

1. [vercel.com](https://vercel.com) → **Sign up with GitHub**
2. **Add New → Project** → ro'yxatdan `davomat` repozitoriysini tanlang → **Import**
3. **Environment Variables** bo'limiga ikkita qiymat qo'shing:

   | Nomi | Qiymati |
   |---|---|
   | `DATABASE_URL` | Neon'dan olingan **pooled** manzil |
   | `ADMIN_PASSWORD` | o'zingiz o'ylab topgan kuchli parol |

   > `ADMIN_PASSWORD` faqat **birinchi ishga tushishda** ishlaydi — bazaga
   > boshlang'ich parol sifatida yoziladi. Keyin parol admin panelidan
   > o'zgartiriladi va bu o'zgaruvchi e'tiborga olinmaydi.

4. **Framework Preset**: Vercel `FastAPI` ni o'zi aniqlaydi — o'zgartirmang
5. **Deploy** tugmasini bosing. 1–2 daqiqada `https://davomat-xxxx.vercel.app`
   ko'rinishidagi manzil beriladi.

Jadvallar birinchi so'rovda avtomatik yaratiladi — qo'lda SQL yozish kerak emas.

---

## 4-qadam. Birinchi sozlash

1. `https://SIZNING-MANZIL.vercel.app/admin` → `ADMIN_PASSWORD` bilan kiring
2. **Sozlamalar**:
   - kompaniya nomi, ish vaqti, kechikish chegarasi
   - **📍 Joylashuv tekshiruvi** — belgilab qo'ying
   - **ofisda turib** telefondan yoki noutbukdan «📍 Shu yerdan olish» tugmasini
     bosing → koordinata avtomatik to'ladi
   - radius: **100–300 metr** (telefon GPS'i har doim aniq emas, 50 metr qilsangiz
     halol xodimlar ham belgilay olmay qoladi)
   - «QR koddagi manzil» — **bo'sh qoldiring**, tizim domenni o'zi aniqlaydi
3. **Xodimlar** → hammasini qo'shing
4. **Proyektor** → `F11` bilan to'liq ekran

---

## 5-qadam. Keyingi o'zgarishlar

GitHub'ga har `git push` qilganingizda Vercel avtomatik qayta deploy qiladi.
Ma'lumotlar Neon'da turgani uchun deploy paytida hech narsa yo'qolmaydi.

---

## Bilib qo'yish kerak bo'lgan narsalar

**Lokal variantdagi himoya yo'qoladi.** Ofis Wi-Fi'i endi shart emas — shuning
uchun GPS tekshiruvini **albatta yoqing**. Usiz xodim uydan turib belgilay oladi:
QR har 30 soniyada yangilansa ham, hamkasbiga screenshot yuborishga 90 soniya
yetadi.

**Birinchi so'rov sekin bo'lishi mumkin.** Neon bepul tarifda bir necha daqiqa
harakatsizlikdan keyin bazani uxlatib qo'yadi. Ertalabki birinchi ochilish
1–3 soniya davom etadi, keyingilari tez.

**Vercel bepul tarifi yetadi.** Proyektor ekrani serverga soatiga ~60 marta
murojaat qiladi (QR'lar oldindan paketlab olinadi va brauzerning o'zi
almashtiradi), xodimlar esa kuniga 2 martadan. 50 kishilik ofis uchun oyiga
~20 000 chaqiruv — Hobby tarifi chegarasidan ancha past.

**Ma'lumotlar Neon'da.** Zaxira nusxa: Neon panelida *Backups* bo'limi bor,
bepul tarifda ham ma'lum muddatga saqlanadi. Qo'lda olish uchun Neon'ning
SQL Editor'idan jadvallarni CSV ga eksport qilish mumkin.

**Vaqt zonasi** kodda Toshkent (`Asia/Tashkent`) qilib qo'yilgan —
`app/config.py` faylida. Vercel serveri qayerda turishidan qat'i nazar vaqt
to'g'ri hisoblanadi.

**Baza o'zgaruvchisining nomi muhim emas.** Vercel'ning Neon integratsiyasi
o'zgaruvchilarga baza nomidan prefiks qo'shadi — masalan `checkin` deb nom
bersangiz, manzil `CHECKIN_DATABASE_URL` ichida bo'ladi. Tizim nomning
oxiriga qarab o'zi topadi, qo'lda hech narsa ko'chirish shart emas.
Ulanish hovuzli (pooled) variant avtomatik afzal ko'riladi.

**Konfiguratsiya fayli yo'q va kerak emas.** Vercel FastAPI ilovasini o'zi
topadi: `app/main.py` ichidagi `app` o'zgaruvchisi uning standart qidiruv
ro'yxatida. `public/` papkasidagi fayllar CDN orqali tarqatiladi
(`public/static/style.css` → `/static/style.css`), Python versiyasi esa
`.python-version` faylida ko'rsatilgan. `vercel.json` qo'shish shart emas —
aksincha, unda yozilgan ortiqcha sozlama build'ni buzishi mumkin.

---

## Ofis varianti ham kerakmi?

Ikkalasini bir vaqtda ishlatmang — ular alohida bazalarda ishlaydi va
ma'lumotlar bir-biriga qo'shilmaydi.

Agar ofis kompyuterini ham **o'sha bulut bazasiga** ulamoqchi bo'lsangiz:
loyiha papkasida `.env` fayli yarating (`.env.example` dan nusxa oling) va
ichiga Neon manzilini yozing. Shunda `ISHGA TUSHIRISH.bat` ham bulut bazasi
bilan ishlaydi — ya'ni bitta umumiy ma'lumot bazasi bo'ladi.
