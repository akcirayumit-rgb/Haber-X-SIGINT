# Haber-X SIGINT — Sinyal İstihbarat Konsolu
## Kapsamlı Kullanım Rehberi ve Video Türetim Dokümanı

---

## GIRIŞ

**Haber-X SIGINT**, HF (Yüksek Frekans) ve komşu bantlarda sinyal istihbaratı (SIGINT) yapabilir Electron tabanlı masaüstü uygulamasıdır. Morse kodu (CW) çözme, uçak takibi (ADS-B), gemi haritalaması (AIS), radyo taraması ve triangulasyon yeteneklerine sahiptir.

**Gerekli donanım:**
- RTL-SDR dongle veya benzer SDR cihazı
- HamItUp +125 MHz up-converter (HF bandı için)
- Bilgisayar mikrofonu veya ses kartı
- İsteğe bağlı: GNSS/GPS alıcı

---

## ANA ARAYÜZ YAPISI

Ekran iki ana bölüme ayrılır:

### **SOL PANEL** (Kaynak Kontrolü ve Ayarlar — 300px genişliği)
Tüm giriş kaynakları, frekans ayarları, ağ bağlantıları, SDR donanım kontrolü ve tarama parametreleri buradan yapılır.

### **SAĞ ALAN** (Sekme Tabanlı Çıktı — Dinamik)
9 farklı sekme aracılığıyla sonuçlar gösterilir: CW Çözme, Gönder, Konum Tespit, ADS-B, ACARS, Geçmiş, Alfabe Referansı, AIS ve Kurulum.

---

## SOL PANEL — AYRINTILAR

### 1️⃣ **KAYNAK KONTROLÜ** (Section: Kaynak Kontrolü)

#### 🎙 MİKROFON BAŞLAT
- **Ne yapar:** Bilgisayarın yerleşik mikrofonunu veya ses giriş cihazını başlatır. Gerçek zamanlı ses akışını analiz eder.
- **Kullanım:** Gerçek HF radyo sinyallerini yakalamak için tıklayın. Elektromanyetik ortamda çalışır.
- **Durum:** Mavi buton = Hazır, Turuncu buton = Çalışıyor.

#### 📁 SES DOSYASI YÜKle
- **Ne yapar:** Daha önce kaydedilmiş .wav, .mp3, .flac gibi ses dosyalarını yükler. Denemeli çalışma veya arşiv analizi için ideal.
- **Dosya Formatları:** WAV, MP3, FLAC, OGG, M4A
- **Kullanım:** "Ses dosyasını aç" diyalog açılır. Seçtikten sonra otomatik olarak çözülmeye başlar.

#### ⏹ DURDUR
- **Ne yapar:** Aktif ses akışını durdurur (mikrofon veya dosya).
- **Durum:** Sadece ses çalışırken aktif olur (enabled).

---

### 2️⃣ **FREKANS DEDEKTÖRÜ** (Section: Frekans Dedektörü)

Hedef CW (Morse) tonunun frekansını belirtir. Yazı-Frekans Analiz Cihazı (FFT) tarafından otomatik olarak algılanabilir.

#### 📊 Frekans Görüntüsü
- **Aralık:** 300 Hz — 1200 Hz
- **Varsayılan:** 700 Hz (standart CW tonu)
- **Açıklama:** Radyo alıcısından gelen demodüle edilmiş ses tonu frekansı.

#### 📈 Eşik (Hassasiyet)
- **Aralık:** %5 — %80
- **Varsayılan:** %30
- **Ne yapar:** Sinyal algılama hassasiyetini kontrol eder. Yüksek = Sadece güçlü sinyaller, Düşük = Hafif sinyalleri de yakalar.
- **Spektrum Kanvas:** Gerçek zamanlı FFT grafiği. Spike'lar (tepe noktaları) sinyal frekansını gösterir.

#### 📶 Sinyal Çubuğu (dB)
- **Renk:** Yeşil → Turuncu (güçlü sinyal)
- **Label:** dB (Desibel) cinsinden sinyal gücü

---

### 3️⃣ **ZAMANLAMA** (Section: Zamanlama)

Morse kodunun hızını otomatik veya manuel olarak ölçer.

#### ⏱ WPM (Words Per Minute)
- **Otomatik:** Kod hızını ölçer (örneğin: 15 WPM)
- **Gösterim:** Nokta başına milisaniye cinsinden

#### 🎚 Manuel WPM Kaydırıcısı
- **Aralık:** 0 — 40 WPM
- **0 = Otomatik:** Sistem algılanan hız kullanır
- **1–40 = Manuel:** Sabit hız ayarı (test için)
- **Kullanım:** Sinyali manuel olarak bildiğiniz hızda çözmek için.

---

### 4️⃣ **ALFABE / DİL SEÇIMI** (Section: 🌍 Alfabe / Dil)

Morse kodunun hangi yazı sistemiyle çözülüp gösterileceğini seçer.

#### 🌐 Dil Seçenekleri
1. **Uluslararası (Latin)** - ITU Standart, EN/FR/DE/ES
2. **Arapça (ITU)** - ITU-R M.1677 Arapça Morse
3. **Türkçe (Özel)** - Türkçe karakterler (Ç, Ğ, İ, Ö, Ş, Ü)
4. **Kürtçe (Kurmanji)** - Latin alfabesi tabanlı Kurmanji
5. **Farsça / Arapça karışık** - Farsi + Arapça karakter desteği

#### 📋 Dil Etiketleri
- Her dil seçildiğinde: "Script Türü", "Kod Sistemi" vs. gösterilir.
- Örnek: "Arap (ITU-R M.1677)"

---

### 5️⃣ **MANUEL GIRIŞ (TEST)** (Section: ✏️ Manuel Giriş)

Kod yazıp neye çevrildiğini test eder.

#### 📝 Giriş Alanı
- **Format:** Morse kodu (boşluk/nokta/tire): `.- -... -.-.`
- **Çıktı:** Çözülen metin (sağda)
- **Diller:** Seçili dile göre çevirisi gösterilir

---

### 6️⃣ **MESH AĞ** (Section: 🌐 Mesh Ağ)

Bir ağ üzerinde birden fazla Haber-X cihazını bağlar (konum tespit ve veri paylaşımı için).

#### 🔗 Bu Cihazın IP'si
- **Gösterim:** Local IP adresi (örneğin: 192.168.1.100)
- **WS Port:** 8765 (WebSocket sunucusu)
- **Açıklama:** Diğer cihazlar bu IP'ye bağlanabilir

#### 🔌 Bağlantı Ayarları
- **Peer URL:** Başka bir Haber-X cihazının adresi (örn: `ws://192.168.1.50:8765`)
- **🔗 Buton:** Ağda başka bir cihaza bağlanır
- **Bağlı Düğümler:** Kaç peer şu anda bağlı olduğunu gösterir

---

### 7️⃣ **FREKANS TARAYICI** (Section: 🔍 Frekans Tarayıcı)

Belirtilen frekans listesini otomatik olarak tarar.

#### ▶ TARA Butonu
- **Başlat/Durdur:** Tarama döngüsünü kontrol eder
- **Mod:** Belirtilen frekanslar arasında geçiş yapar

#### ➕ EKLE Butonu
- **Ne yapar:** Özel bir frekans ve modu tarama listesine ekler

#### 🎚 Bekleme (Squelch) — %5–60
- **Default:** %20
- **Açıklama:** Tarama sırasında sessiz kanalları atlamak için eşik

#### ⏳ Adım Süresi — 1–10 saniye
- **Default:** 2 saniye
- **Açıklama:** Her frekansda kalış süresi

#### 📻 Frekans Listesi
- Taranacak frekanslara ilişkin tablo (mod, açıklama vb.)
- Siyah liste için bir frekanstan sağ tık → kaldır

---

### 8️⃣ **HABER-X ENTEGRASYONU** (Section: ⚡ Haber-X Entegrasyonu)

Bu SIGINT uygulamasını ana Haber-X OSINT platformuna bağlar.

#### 🔗 Bağlantı Durumu
- **Yeşil nokta:** Bağlı
- **Gri nokta:** Bağlı değil
- **Status Metni:** "Bağlı" veya "Bağlı değil"

#### 📍 URL Ayarı
- **Default:** `http://localhost:3000`
- **Açıklama:** Haber-X sunucusu adresi
- **Protokol:** HTTP/HTTPS

#### 📤 TÜM VERİYİ GÖNDER
- **Ne yapar:** Çözülen metin + metaveri (zaman, frekans, WPM) JSON formatında gönderir
- **Format:**
  ```json
  {
    "timestamp": "2026-06-02T10:30:00Z",
    "text": "CQ CQ CQ DE TA3XY",
    "frequency_hz": 700,
    "wpm": 15,
    "signal_db": -45,
    "language": "intl"
  }
  ```

#### 🔄 Durum Mesajı
- Gönderme başarı/hatası hakkında gerçek zamanlı bilgi

---

### 9️⃣ **SDR++ / HAMLIB İNTEGRASYONU** (Section: 📻 SDR++ / Hamlib)

Popüler SDR yazılımı **SDR++** ile sinkronizasyon.

#### 🔄 HamItUp +125 MHz Offset
- **Toggle (Aç/Kapat):** HF up-converter desteği
- **Açıklama:** HamItUp 125 MHz'e kaydırsa da, gösterilen frekans otomatik olarak gerçek RF frekansına düşürülür
- **Örnek:** SDR++ 131.550 MHz gösterirse → Gerçek frekans 6.550 MHz (80m bant)
- **RF Ekran:** Hesaplanan gerçek RF frekansını gösterir

#### 🔌 Rigctl Sunucu Bağlantısı
- **Host:Port:** `localhost:4532` (default)
- **Açıklama:** SDR++'dan frekans değişiklikleri otomatik çekilir
- **Buton:** Rigctl TCP bağlantısını aç/kapat
- **Durum:** "Bağlı" / "Bağlı değil"

#### 📡 Network Sink Ses (SDR++ WebSocket)
- **URL:** `ws://localhost:4444` (default)
- **Açıklama:** VB-Cable yerine SDR++'ın WebSocket ses akışını kullan
- **Format:** Float Mono, 48 kHz
- **Buton:** ▶ başlat/durdur
- **Avantajı:** Sanal ses kablosuna gerek yok, saf ağ bağlantısı

---

## SAĞ ALAN — 9 SEKME

### 🔵 **SEKME 1: CW ÇÖZME** (Default Tab)
En yaygın kullanılan sekme. Gerçek zamanlı Morse kodu çözümü.

#### ▸ Ham Mors Akışı
- **Görüntü:** Nokta (•) ve tireler (—) yaşayan akış
- **Renk:** Nokta = Mavi (#00d4ff), Tire = Yeşil (#00ff88)
- **Açıklama:** Her bir karakterin Morse karşılığını gösterir

#### ▸ Çözülen Metin
- **Font:** Büyük, kalın, yeşil (Accent2 rengi)
- **Satır Yüksekliği:** Metin akan şekilde taşınabilir
- **Kopyalama:** Metni seçip Ctrl+C ile kopyalanabilir

#### 📊 Bilgi Göstergeleri
- **WPM (Words Per Minute):** Algılanan hız (Örneğin: "15 WPM")
- **Sinyal (dB):** SNR (Signal-to-Noise Ratio) desibel cinsinden

#### 🎯 Kontrol Butonları
- **🗑 TEMİZLE:** Mevcut metni siler
- **📋 KOPYALA:** Tüm metni panoya kopyalar

---

### 📡 **SEKME 2: GÖNDER** (TX — Transmission)

Morse kodu çalarak iletkili protokolle sinyali gönderir.

#### ▸ METİN / SES GİRİŞİ

**Text Alanı:**
- **Placeholder:** "Göndermek istediğiniz metni buraya yazın..."
- **Örnek:** `CQ CQ DE TA3XY K`
- **Format:** Serbest İngilizce, Türkçe veya Arapça metin

**🎤 SES GİRİŞİ**
- **Ne yapar:** Konuşulan kelimeyi metne çevirme (speech-to-text)
- **Dil:** Sistem dili (İngilizce, Türkçe)
- **Durum:** Kırmızı = Kaydediliyor

#### PROSIGN Hızlı Butonları
Standart radyo işaret kodları (CQ, DE, K, AR, SK, QRZ, QSL vb.)

**Önemli Prosign'ler:**
- **CQ:** "Herkese çağrı" (Call to All)
- **DE:** "Den" (From)
- **K:** "Kontrol" (Go ahead / your turn)
- **AR:** "End of message"
- **SK:** "Kapanış" (End of contact)
- **73:** "Best regards"
- **88:** "Love and kisses"

#### ▸ TX AYARLARI (2×2 Grid)

| Ayar | Aralık | Default | Açıklama |
|------|--------|---------|----------|
| **TX Hızı (WPM)** | 5–40 | 15 | Morse kodu hızı |
| **CW Ton Frekansı** | 300–1200 Hz | 700 Hz | Çıkış sesi frekansı |
| **Dalga Formu** | Sine/Square/Triangle | Sine | Ses dalgası şekli |
| **Ses Seviyesi** | 0–100% | 80% | Hoparlör/kulaklık çıkış gücü |

#### ▸ MORS KODU ÖNİZLEME
- **Görüntü:** Girilen metin → Morse kodu
- **Dinamik:** Yazarken canlı güncellenir
- **Renk:** Nokta = Mavi, Tire = Yeşil

#### 🎚 KEYER (Aktif Gönderim) Göstergesi
Aktif gönderim sırasında görünür:
- **Keyer Lambası:** Turuncu parlayan daire = Keying on
- **Mevcut Karakter:** Şu an gönderilen harf
- **Morse Kodu:** Keying işleminin Morse gösterimi
- **İlerleme Çubuğu:** Gönderme yüzdesi

#### 🎯 Gönderme Kontrolleri
- **▶ GÖNDER (CW SES):** Metni Morse kodu olarak hoparlörden çalar
- **⏹ DURDUR:** Aktif gönderi durdurur
- **📋 MORS KODU KOPYALA:** Sadece Morse kodunu panoya kopyalar
- **🗑 TEMİZLE:** Metni siler

#### ⚠️ SDR TX Notu
- Hoparlör çıkışını telsizin mikrofon girişine bağlamak gerekir
- VB-Cable veya benzer sanal ses kablosu kullanılabilir
- CAT/VOX modlu telsizler desteklenir

---

### 🎯 **SEKME 3: TRİANGÜLASYON**

Sinyal kaynağını birden fazla alıcı kullanarak konumunu belirler.

#### Sol Panel: Düğüm Yönetimi

**BU CİHAZ (NODE-A)**
- **Konum Giriş:** Enlem / Boylam (GPS veya manuel)
- **Default:** Kuzey Irak (36.191, 44.009)
- **Hassasiyet:** 6 ondalık basamak (~0.1 metre)
- **GPS Buton:** Cihazdan otomatik konumu çekmek (yanılı)

**Askeri Grid (MGRS)**
- **Format:** `38SND 19109 90000` (örnek)
- **ÇEVIR Buton:** MGRS → Lat/Lon
- **MGRS'YE ÇEVIR:** Lat/Lon → MGRS

**Sinyal Yönü (Azimut)**
- **Pusula Halka:** Görsel azimut göstergesi
- **İnput Alanı:** 0–359° (Kuzeyde = 0°)
- **Açıklama:** Sinyalin hangi yönden geldiğini belirtir

**İlave Bilgiler**
- **Sinyal (dBm):** Alınan sinyal gücü
- **Frekans:** Kayıtlı frekans

**📡 BEARING YAYINLA**
- Mesh ağındaki diğer cihazlara bearing gönderi

#### BAĞLI DÜĞÜMLER
- Ağdaki diğer cihazlar için kartlar
- Her kartta: Konum, Azimut, Sinyal

#### Sağ Panel: Harita

**🗺 TRİANGÜLASYON HARİTASI**
- **Harita Kütüphanesi:** Leaflet.js (OpenStreetMap tabanlı)
- **Renkler:**
  - **Mavi:** Bu cihaz
  - **Yeşil:** Peer düğümler
  - **Turuncu:** Bearing hatları
  - **Kırmızı X:** Hesaplanan hedef

**⚡ HESAPLA Buton**
- En az 2 bearing kullanarak trilaterasyon yapar
- Sonuç gösterir (Lat/Lon)

**🎯 HESAPLANAN HEDEF KONUMU**
- **Koordinatlar:** Büyük fontla görüntülenmiş
- **Belirsizlik:** Hata sınırı (±km)
- **Azimut:** Bizzden hedefe açı
- **Mesafe:** Km cinsinden

---

### ✈️ **SEKME 4: ADS-B**

Commercial aircraft radar takibi (çoğu uçak otomatik)

#### 🔗 Bağlantı Ayarları
- **URL:** `http://localhost:8080` (dump1090 HTTP API)
- **BAĞLAN:** Connection test
- **▶ BAŞLAT:** Veri çekme döngüsü

#### 🗺 ADS-B HARİTASI
- **Markers:** Uçak simgeleri harita üzerine
- **Click:** Uçağa tıklayınca detay bilgisi
- **Zoom:** Harita ölçeklendirmesi

#### 📊 İstatistikler
- **Toplam:** Algılanan tüm uçaklar
- **Haritada:** Jeolokasyonlu olanlar
- **Acil:** Squawk 7700 (Mayday)
- **Son Güncelleme:** Zaman damgası

#### 📋 Uçak Tablosu
| Sütun | İçerik |
|-------|--------|
| ICAO | 24-bit aircraft code |
| UÇUŞ | Flight call sign (örn: TK123) |
| İRTİFA (ft) | Feet cinsinden yükseklik |
| HIZ (kt) | Düğüm (knot) cinsinden |
| YÖN | Derece cinsinden kurs |
| LAT/LON | Konumu |
| SQUAWK | 4-digit transponder kodu |
| KAYNAK | Veri kaynağı |

#### ⚠️ ACIL DURUM ALARMı
- Squawk 7700, 7600, 7500 tespit edilirse bildiri
- Kırmızı banner gösterilir

#### 🛠️ Kurulum
```bash
# macOS
brew install dump1090-mutability

# Linux
sudo apt install dump1090-fa

# Çalıştırma (RTL-SDR takılı)
dump1090 --net --net-http-port 8080
```

---

### 📨 **SEKME 5: ACARS**

Uçak haberleşme mesajları (metin protocol)

#### 🔗 Bağlantı
- **URL:** `http://localhost:15555` (acarsdec output)
- **BAĞLAN:** Test bağlantısı
- **TEMİZLE:** Mesajları sil

#### 📥 Mesaj Akışı
- **Format:** Flight/Aircraft ID + Metin mesajı
- **Headerlar:** Zaman, Frequence, ICAO, Message type

#### 🔍 Filtreler
- **Metin Filtresi:** Uçuş/kuyruk/içerik arama
- **Sadece Alarmlar:** Keyword-triggered mesajlar
- **Alarm Kelimeleri:** Sistem tarafından ayarlanan anahtar kelimeler

#### 💾 DIŞA AKTAR
- Mesajları CSV veya JSON olarak indir

#### 🛠️ Kurulum
```bash
acarsdeco2 -A 131.550MHz --output=json:tcp:15555
```

---

### 📋 **SEKME 6: GEÇMİŞ**

Oturum sırasında çözülen tüm mesajların kaydı

#### 📊 Geçmiş Tablosu
| Kolon | İçerik |
|-------|--------|
| Zaman | HH:MM:SS |
| Morse | Kod gösterimi |
| Metin | Çözülen metin |

#### 🗑️ GEÇMİŞİ TEMİZLE
- Tüm kaydı siler

#### 💾 TXT OLARAK DIŞA AKTAR
- Loglanmış metin dosyası indir

---

### 🔤 **SEKME 7: ALFABE**

Seçili dile ait Morse referans tablosu

#### 📚 Alfabe Grid
- **4 sütunlu layout**
- Her hücre:
  - **Sol:** Harf (A, B, C, ...) veya sayı
  - **Sağ:** Morse kodu (.-., -..., -.-.  , ...)
- **Renkler:** Harf=Yeşil, Kod=Mavi

---

### 🚢 **SEKME 8: AIS**

Deniz gemi takibi (Automatic Identification System)

#### 🗺 AIS HARİTASI
- **Gemiler:** Harita üzerine simgeler
- **Hareketler:** Canlı konum güncellemeleri
- **Zoom:** Kıyı bölgelerini yakınlaştır

#### 📊 Gemi İstatistikleri
- **Toplam:** Bölgedeki tüm gemiler
- **Ticari:** Cargo/Tanker şipman
- **Tanker:** Tehlikeli yük gemileri (kırmızı)
- **Askeri/Özel:** Hükümet/Private vessels (yeşil)

#### 📋 Gemi Tablosu
| Sütun | İçerik |
|-------|--------|
| MMSI | Maritime number |
| Gemi Adı | Vessel name |
| Tip | Cargo, Tanker, Passenger... |
| LAT/LON | Konumu |
| Hız (kn) | Knot cinsinden hız |
| Rota | Derece cinsinden kurs |
| Durum | Underway/Moored/At anchor |
| Zaman | Son update |

#### 🔗 Bağlantı
- **URL:** `http://localhost:8090/vessels`
- **▶ İZLE:** Polling başlat
- **TEMİZLE:** Tüm datayı sil

#### 🛠️ Kurulum
```bash
brew install ais-catcher
ais-catcher -H 8090
# OR
rtl_ais
```

---

### ⚙️ **SEKME 9: KURULUM**

Tam kurulum ve bağlantı talimatları

#### 📚 Adım Adım Talimatlar

**Adım 1 — SDR++ Ses Çıkışı**
- SDR++ açılır
- Audio tab → Output Device → "VB-Cable" veya sistem hoparlörü
- Apply

**Adım 2 — Demodülasyon Modu**
- SDR++ Demod dropdown → "CW (USB/LSB)"
- HamItUp açık → 0–30 MHz izlenebilir

**Adım 3 — CW Frekansı**
- SDR++ Audio out frekansı genellikle 500–900 Hz
- Bu uygulama sol panelden "Frekans Dedektörü" slaideri ayarla

**Adım 3b — SDR++ Network Sink (VB-Cable Alternatifi)**
- SDR++ Module Manager → Network Sink ekle
- WebSocket port: 4444
- Format: Float Mono
- Bu uygulama "Network Sink Ses" URL'sine `ws://localhost:4444` gir

**Adım 3c — Rigctl Frekans Senkronizasyonu**
- SDR++ Rigctl Server module (port 4532)
- Bu uygulama "Rigctl Sunucu" → `localhost:4532` gir
- Bağlan

**Adım 4 — Bölge Frekansları (Kuzey Irak)**
```
3.5–4.0 MHz   → 80m bandı (gece TS)
7.0–7.2 MHz   → 40m bandı (bölgesel)
14.0–14.35 MHz → 20m bandı (DX)
21.0–21.45 MHz → 15m bandı (gündüz)
28–30 MHz     → 10m bandı (VHF prep)
131.550 MHz   → ACARS (uçak)
161.975/162.025 → AIS (gemi)
1090 MHz      → ADS-B (uçak radar)
```

**HamItUp Offset**
- Fiziksel: +125 MHz (VFO 0–30 MHz → 125–155 MHz)
- Bu uygulama toggle: "HamItUp +125 MHz Offset" aç
- Gösterilen frekanslar otomatik düşürülür

**Haber-X Entegrasyonu**
- KOPYALA → Haber-X OSINT platformuna yapıştır
- Veya "TÜM VERİYİ GÖNDER" ile otomatik JSON POST

---

## HEADER (Başlık Çubuğu)

### Status Dot
- **Yeşil (Parlayan):** Sistem aktif
- **Gri:** Idle
- **Kırmızı (Titreyen):** Hata veya kritik alarm

### HABER-X SIGINT Badge
- **Titel:** Uluslararası tanıtım
- **Alt-Badge:** "SDR / SİNYAL İSTİHBARATI"
- **Yer Badge:** "KUZEY IRAK / KRG"

### Tone Indicator
- **Yeşil daire:** Ses algılandı
- **Etiket:** "SESE BAŞLANDI" veya "SES YOK"

---

## TEMEL WORKFLOW'LAR

### 📡 Morse (CW) Çözme Akışı
1. Sol panel: 🎙 **MİKROFON BAŞLAT** tıkla
2. SDR++'dan CW sinyali gelmesi bekle
3. Sol panel: **Frekans Dedektörü** kaydırıcısını CW tonuna ayarla
4. Sağ panel: **CW ÇÖZME** sekmesi otomatik açılır
5. Çözülen metin görüntülenir (canlı)
6. 📋 **KOPYALA** ile metin panoya alınır

### 🗣️ Morse Gönder (TX)
1. **GÖNDER** sekmesine git
2. Metin alanına mesajı yaz (örn: "CQ CQ DE TA3XY K")
3. TX WPM, Frekans, Ses Seviyesi ayarla
4. 📋 **KOPYALA MORS KODU** ile test et
5. ▶ **GÖNDER** tıkla
6. Hoparlör çıkışını telsizin microphone'una bağla
7. PTT (Push-to-Talk) bas ve telsiz frekansında yayın yap

### 🎯 Konum Tespit (Multi-Node)
1. **TRİANGÜL** sekmesine git
2. Sol panelde: Bu cihazın konumunu (enlem/boylam) gir
3. Sinyal yönü (azimut) inputunu doldur (0–359°)
4. 📡 **BEARING YAYINLA** tıkla
5. Diğer cihazlar ağda bağlanırsa otomatik görünür
6. 2+ bearing alındığında ⚡ **HESAPLA** tıkla
7. Hedef konum (kırmızı X) haritada görünür

### ✈️ Uçak Takip (ADS-B)
1. dump1090 başlat (RTL-SDR 1090 MHz'de)
   ```bash
   dump1090 --net --net-http-port 8080
   ```
2. **ADS-B** sekmesine git
3. 📍 **BAĞLAN** tıkla (localhost:8080 test)
4. ▶ **BAŞLAT** tıkla
5. Harita canlı uçakları gösterir

### 🚢 Gemi Takip (AIS)
1. ais-catcher başlat
   ```bash
   ais-catcher -H 8090
   ```
2. **AIS** sekmesine git
3. ▶ **İZLE** tıkla
4. Kıyı bölgesindeki gemiler haritada görünür

---

## KESTIRME TUŞLAR (Uygulamada)

| Tuş | İşlev |
|-----|-------|
| Ctrl+C (Çözme) | Metin kopyala |
| Ctrl+C (Gönder) | Morse kodunu kopyala |
| Delete | Geçmiş temizle |
| Ctrl+L | Dil değiştir (select'e focus) |

---

## TEKNIK REFERANSlar

### Frekans Bantları (Bölge — KRG/Kuzey Irak)
- **80m:** 3.5–4.0 MHz (CW, SSB, RTTY)
- **40m:** 7.0–7.2 MHz (Bölge popüler)
- **20m:** 14.0–14.35 MHz (DX frekansı)
- **15m:** 21.0–21.45 MHz (Gündüz DX)
- **10m:** 28–30 MHz (Contest)

### SDR Donanımı
- **RTL-SDR:** Düşük maliyet, VHF-UHF
- **HackRF One:** TX capable, geniş bant
- **LimeSDR:** Düşük maliyetli TX

### Demodülasyon Modları
- **CW (USB/LSB):** Morse kodu (dar bant)
- **AM:** Amplitude Modulation (geniş bant)
- **FM:** Frequency Modulation (2-way radio)
- **SSB:** Single Sideband (verimli)

---

## YAYGIN SORUNLAR VE ÇÖZÜMLER

### ❌ Frekans Algılanmıyor
- **Kontrol:** Ses kartı cihaza bağlı mı?
- **Çözüm:** Sol panel "Eşik" slider'ını düşür (daha duyarlı)
- **Test:** Manuel Giriş sekmesinde kodu yapıştır

### ❌ "Bağlı değil" (HABER-X)
- **Kontrol:** Haber-X sunucusu `http://localhost:3000` çalışıyor mu?
- **Çözüm:** Haber-X uygulamasını başlat veya URL düzelt

### ❌ Mesh Ağ: Peer görünmüyor
- **Kontrol:** Firewall port 8765'i engellemiyor mu?
- **Çözüm:** Yazılım firewall'ı devre dış bırak veya 8765'e izin ver
- **Test:** Peer URL'sini manuel yapıştır ve bağlan

### ❌ ADS-B: dump1090 bağlanmıyor
- **Kontrol:** `http://localhost:8080` tarayıcıda açılıyor mu?
- **Çözüm:** dump1090 tam komutu: `dump1090 --net --net-http-port 8080`
- **RTL-SDR:** USB cihazı takılı mı?

---

## ÖZET

**Haber-X SIGINT**, gerçek zamanlı Morse çözümü, uçak/gemi takibi, ve konum tespita dayalı SIGINT konsolu sunar. Profesyonel radyo operatörleri, harita üzerinde sinyal kaynakları bulabilir ve multilingual Morse tabloları kullanabilirler.

**Ana Yeterlilikleri:**
- ✅ CW (Morse) Çözme & Gönderme
- ✅ ADS-B Uçak Takibi
- ✅ ACARS Haberleşme Tutanakları
- ✅ AIS Gemi Takibi
- ✅ Sinyal Konum Tespitu (Multi-node)
- ✅ Mesh Ağ (Çok cihaz koordinasyonu)
- ✅ Frekans Taraması
- ✅ Haber-X OSINT Entegrasyonu

---

**Video Derlemeleri İçin İdeal Başlıklar:**
1. "Haber-X SIGINT'e Hoş Geldiniz — Kurulum ve İlk Başlangıç"
2. "Morse Kodu Çözme — Gerçek Zaman Analizi"
3. "SDR++ ile HF Band Dinleme ve Frekans Taraması"
4. "Uçak Takibi (ADS-B) — Radar Konsolu"
5. "Gemi Takibi (AIS) — Deniz Güvenliği"
6. "Sinyal Konum Tespitu — Multi-Node Lokasyon Bulma"
7. "Mesh Ağ Kurulumu — Uzun Mesafe Koordinasyon"
8. "Morse Gönder (TX) — Radyo Haberleşme"
9. "Haber-X OSINT ile Entegrasyon — Veri Aktarımı"

---

**Son Güncelleme:** Haziran 2, 2026
**Platform:** Electron Desktop (macOS, Windows, Linux)
**Dil:** Turkish (Türkçe)
**Versiyon:** Haber-X SIGINT v1.0
