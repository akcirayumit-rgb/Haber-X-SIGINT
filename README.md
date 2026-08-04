# Haber-X SIGINT — Sinyal İstihbarat Konsolu

RTL-SDR tabanlı sinyal izleme ve çözümleme konsolu. Electron masaüstü uygulaması olarak paketlenir; arka planda Express + WebSocket sunucusu çalışır ve Python çözücüleri yönetir.

## Kurulum

```bash
npm install
```

Çözücüler için ayrıca `rtl-sdr` araçları gerekir:

```bash
brew install rtl-sdr sox
rtl_test -t   # cihazın bağlı olduğunu doğrula
```

Ses-metin (STT) özelliği için Python tarafında Whisper kurulu olmalıdır.

## Çalıştırma

```bash
npm start     # Electron uygulaması (sunucuyu kendisi başlatır)
npm run dev   # sadece sunucu — tarayıcıdan http://localhost:3001
npm run build # macOS .app/.dmg üretir (dist/)
```

## Portlar

Sunucu **3001** portunda çalışır. Port 3000 ayrı bir projeye (Haber-X Platformu) aittir; SIGINT o portu kullanmamalıdır.

Port değiştirmek için:

```bash
SIGINT_PORT=3005 npm run dev
```

Ön yüzdeki WebSocket adresi `window.location.host` üzerinden türetilir, yani porta sabitlenmemiştir.

## Yapı

| Yol | Görev |
|---|---|
| `main.js` | Electron ana süreci — sunucuyu başlatır, pencereyi açar |
| `server.js` | Express + WebSocket sunucusu, çözücü yönlendirmesi |
| `decoder-manager.js` | Python çözücü süreçlerinin yaşam döngüsü ve JSON ayrıştırma |
| `index.html` | Konsol arayüzünün tamamı |
| `test-decoders/` | Python çözücüler (FM radyo, spektrum, GPS, NOAA, ISS, …) |
| `whisper_service.py` | Ses-metin dönüşümü |

## Notlar

- Paketlenmiş uygulamada sunucu, harici `node` yerine Electron'un kendi ikili dosyasıyla (`ELECTRON_RUN_AS_NODE`) çalıştırılır — Finder'dan açılan `.app`'in PATH'inde Homebrew bulunmaz.
- `dist/` ve `node_modules/` sürüm kontrolüne dahil değildir.
