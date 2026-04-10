# ⚽🏀 Canlı Skor + AI Analiz Uygulaması

Streamlit tabanlı, çoklu AI destekli canlı skor uygulaması.

## 🚀 Kurulum (5 adım)

### 1. Python kütüphanelerini yükle
```bash
pip install -r requirements.txt
```

### 2. `.env` dosyasını düzenle
`.env` dosyasını aç ve key'lerini yaz:
```
API_SPORTS_KEY=senin_api_sports_keyin
GEMINI_API_KEY=senin_gemini_keyin
GROQ_API_KEY=senin_groq_keyin  (opsiyonel)
```

### 3. Uygulamayı başlat
```bash
streamlit run app.py
```

### 4. Tarayıcı otomatik açılır
`http://localhost:8501` adresinde çalışır.

---

## 🔑 API Key'leri Nereden Alınır?

| Servis | Adres | Ücret |
|--------|-------|-------|
| API-Sports | dashboard.api-sports.io → My Access | Ücretsiz |
| Gemini | aistudio.google.com → Get API Key | Ücretsiz |
| Groq | console.groq.com → API Keys | Ücretsiz |

---

## 🎮 Özellikler

- ⚽ Futbol ve 🏀 Basketbol canlı skorlar
- 🔴 Canlı maçlar otomatik öne çıkar
- 🤖 3 farklı AI model: Gemini, Groq, Claude
- 📅 Tarih seçimi
- 🔄 Otomatik yenileme (60sn)
- 🇹🇷 Türkçe AI analizleri

---

## 📱 Mobil Erişim

Aynı WiFi ağındaki telefondan erişmek için:
1. Bilgisayarının IP adresini bul (`ipconfig` / `ifconfig`)
2. Telefon tarayıcısında `http://[IP]:8501` aç
