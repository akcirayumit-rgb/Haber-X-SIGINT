# 🔧 SES GİRİŞİ DEBUG

## Adım 1: Mikrofon Test Sayfası
```bash
npm start
```
Sonra tarayıcı açılsın (dock'ta Haber X SIGINT icon), açılan uygulamada:
- **Adres çubuğuna yaz:** `file:///Users/akciray/twitter-risk-analyzer/haber-x-sigint/test-microphone.html`
- **Enter'a bas**

## Adım 2: Butonları Sırasıyla Tıkla

### 1️⃣ Mikrofon İzni Test
- Eğer `✓ Mikrofon başarıyla erişildi` yazarsa → **mikrofon tamam**
- Eğer `✗ NotAllowedError` yazarsa → **System Preferences → Security & Privacy → Microphone** kısmına git, Terminal'i ekle

### 2️⃣ AudioContext Test  
- `✓ AudioContext oluşturuldu` yazmalı

### 3️⃣ Dinlemeyi Başlat
- Butona tıkla ve **KONUŞ**
- `📊 1000 sample işlendi` gibi mesajlar görmeli

## Adım 3: Main Uygulama Test
Test sayfası çalışıyorsa:

1. **npm start** ile uygulamayı aç
2. **MORS GÖNDER** sekmesine git
3. **🎤 SES GİRİŞİ** butonuna tıkla
4. **KONUŞ**
5. **DevTools aç:** F12
6. **Console** sekmesinde şunları ara:
   - `[Voice] Mikrofon isteniyor...` ← mikrofonaç çalışmadı mı?
   - `[Voice] Mikrofon izni alındı` ← başarılı mı?
   - `[Voice] Vosk servisi başlandı` ← Vosk başlattı mı?
   - `[Voice] Audio chunk #10 işleniyor...` ← ses capture oluyor mu?

## Olası Sorunlar

| Hata | Çözüm |
|------|-------|
| `NotAllowedError` | System Preferences → Security & Privacy → Microphone → Terminal ekle |
| `Vosk servisi başlamadı` | Terminal'i kapat, `npm start` tekrar aç |
| Chunk sayısı artmıyor | Mikrofon kapı, hoparlör açık mı? Çok sessiz konuşuyor musun? |
| "not allowed" yazıyor | Console'da tam hatayı gör (F12) ve yaz |

## Son Çare: Manuel Test

```bash
# Terminal'de çalıştır
python3 /Users/akciray/twitter-risk-analyzer/haber-x-sigint/vosk_service.py << EOF
<speak into microphone - this won't work in pipe, just checking if service starts>
EOF
```

Bunları yap ve bana ne olduğunu söyle!
