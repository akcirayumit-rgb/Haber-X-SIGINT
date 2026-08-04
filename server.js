const express = require('express')
const path = require('path')
const os = require('os')
const fs = require('fs')
const { spawn } = require('child_process')
const WebSocket = require('ws')
const http = require('http')
const axios = require('axios')
const multer = require('multer')
const { DecoderManager } = require('./decoder-manager')

const upload = multer({ dest: os.tmpdir() })
const decoderManager = new DecoderManager()

// ── DeepL Çeviri ────────────────────────────────────────────
// Free key ':fx' suffix → api-free subdomain
const DEEPL_API_KEY  = process.env.DEEPL_API_KEY || ''
const DEEPL_ENDPOINT = DEEPL_API_KEY.endsWith(':fx')
    ? 'https://api-free.deepl.com/v2/translate'
    : 'https://api.deepl.com/v2/translate'

async function deeplTranslate(text, from = 'auto', to = 'TR') {
    // Kürtçe / Farsça → MyMemory fallback (DeepL desteklemiyor)
    if (['ku','fa'].includes(from) || ['ku','fa'].includes(to)) {
        const langpair = `${from === 'auto' ? 'en' : from}|${to.toLowerCase()}`
        const r = await axios.get('https://api.mymemory.translated.net/get', {
            params: { q: text.substring(0, 500), langpair }, timeout: 7000
        })
        return r.data?.responseData?.translatedText || text
    }
    const body = { text: [text.substring(0, 5000)], target_lang: to.toUpperCase() }
    if (from !== 'auto') body.source_lang = from.toUpperCase()
    const r = await axios.post(DEEPL_ENDPOINT, body, {
        headers: { 'Authorization': `DeepL-Auth-Key ${DEEPL_API_KEY}`, 'Content-Type': 'application/json' },
        timeout: 8000
    })
    return r.data?.translations?.[0]?.text || text
}

const app = express()
// 3000 ana Haber-X sunucusuna ait; SIGINT kendi portunda çalışır
const PORT = Number(process.env.SIGINT_PORT) || 3001

let voiceProcess = null
let sttProcess = null
let wss = null
let httpServer = null

// ── Middleware ──────────────────────────────────────────────
app.use(express.static(__dirname))
app.use(express.json({ limit: '50mb' }))
app.use(express.raw({ type: 'application/octet-stream', limit: '50mb' }))

// ── Local IP discovery ──────────────────────────────────────
function getLocalIPs() {
  const results = []
  const ifaces = os.networkInterfaces()
  for (const name of Object.keys(ifaces)) {
    for (const iface of ifaces[name]) {
      if (iface.family === 'IPv4' && !iface.internal) {
        results.push({ name, address: iface.address })
      }
    }
  }
  return results
}

// ── Voice Recognition (Whisper) ───────────────────────────────
function startVoiceRecognition() {
  if (voiceProcess) return

  console.log('[Voice] Whisper process başlatılıyor...')
  voiceProcess = spawn('python3', [
    path.join(__dirname, 'whisper_service.py')
  ], {
    stdio: ['pipe', 'pipe', 'pipe']
  })

  voiceProcess.stdout.on('data', (data) => {
    try {
      const lines = data.toString().split('\n').filter(l => l.trim())
      for (const line of lines) {
        const message = JSON.parse(line)
        // Broadcast to all connected WebSocket clients
        if (wss) {
          wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
              client.send(JSON.stringify({ type: 'voice-recognition', data: message }))
            }
          })
        }
      }
    } catch (e) {
      console.error('[Voice] Parse error:', e.message)
    }
  })

  voiceProcess.stderr.on('data', (data) => {
    console.error('[Voice stderr]', data.toString())
  })

  voiceProcess.on('error', (e) => {
    console.error('[Voice] Process error:', e.message)
    voiceProcess = null
  })

  voiceProcess.on('exit', () => {
    voiceProcess = null
  })
}

function stopVoiceRecognition() {
  if (voiceProcess) {
    try {
      voiceProcess.stdin.end()
    } catch (e) {}
    voiceProcess.kill()
    voiceProcess = null
  }
}

// ── STT (Whisper) ─────────────────────────────────────────
function startStt(language) {
  if (sttProcess) return

  const args = [path.join(__dirname, 'whisper_service.py')]
  if (language) args.push('--language', language)

  console.log('[STT] Whisper başlatılıyor...')
  sttProcess = spawn('python3', args, {
    stdio: ['pipe', 'pipe', 'pipe']
  })

  sttProcess.stdout.on('data', (data) => {
    try {
      const lines = data.toString().split('\n').filter(l => l.trim())
      for (const line of lines) {
        const msg = JSON.parse(line)
        if (wss) {
          wss.clients.forEach(client => {
            if (client.readyState === 1) {
              client.send(JSON.stringify({ type: 'stt-result', data: msg }))
            }
          })
        }
      }
    } catch (e) {}
  })

  sttProcess.stderr.on('data', (data) => {
    console.error('[STT stderr]', data.toString())
  })

  sttProcess.on('error', (e) => {
    console.error('[STT] Hata:', e.message)
    sttProcess = null
  })

  sttProcess.on('exit', () => { sttProcess = null })
}

function stopStt() {
  if (sttProcess) {
    try { sttProcess.stdin.end() } catch (e) {}
    sttProcess.kill()
    sttProcess = null
  }
}

// ── WebSocket Server ────────────────────────────────────────
function startWsServer(server) {
  wss = new WebSocket.Server({ server })

  wss.on('connection', (ws, req) => {
    const ip = req.socket.remoteAddress
    console.log(`[WS] Yeni düğüm bağlandı: ${ip}`)

    // Subscribe to decoder messages
    ws.subscriptions = new Set()

    ws.on('message', (raw) => {
      try {
        const msg = JSON.parse(raw.toString())

        // Handle subscriptions
        if (msg.type === 'subscribe') {
          ws.subscriptions.add(msg.channel)
          decoderManager.subscribe(ws, msg.channel)
          console.log(`[WS] ${ip} → ${msg.channel} subscribe`)
          ws.send(JSON.stringify({ type: 'subscribed', channel: msg.channel }))
        } else if (msg.type === 'unsubscribe') {
          ws.subscriptions.delete(msg.channel)
          decoderManager.unsubscribe(ws, msg.channel)
          console.log(`[WS] ${ip} → ${msg.channel} unsubscribe`)
        } else {
          // Broadcast to all clients (legacy support)
          wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
              client.send(raw.toString())
            }
          })
        }
      } catch (e) {
        console.error('[WS] Parse hatası:', e.message)
      }
    })

    ws.on('close', () => {
      console.log(`[WS] Düğüm ayrıldı: ${ip}`)
      for (const subscription of ws.subscriptions) {
        decoderManager.unsubscribe(ws, subscription)
      }
    })

    ws.on('error', (e) => console.error('[WS] Hata:', e.message))
  })

  wss.on('error', (e) => {
    console.error(`[WS Server] WebSocket error:`, e.message)
  })

  console.log(`[WS] WebSocket server açıldı`)
}

// ── HTTP Routes ─────────────────────────────────────────────

// Serve index.html
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'))
})

// Get local IPs
app.get('/api/local-ips', (req, res) => {
  res.json(getLocalIPs())
})

// Get WS port (WebSocket on same port as HTTP)
app.get('/api/ws-port', (req, res) => {
  res.json({ port: PORT })
})

// Get connected node count
app.get('/api/node-count', (req, res) => {
  const count = wss ? wss.clients.size : 0
  res.json({ count })
})

// Broadcast to all nodes
app.post('/api/broadcast', (req, res) => {
  if (!wss) {
    res.status(400).json({ error: 'WebSocket server not running' })
    return
  }
  const raw = JSON.stringify(req.body)
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(raw)
    }
  })
  res.json({ ok: true })
})

// Voice recognition: start
app.post('/api/voice/start', (req, res) => {
  startVoiceRecognition()
  res.json({ ok: true })
})

// Voice recognition: stop
app.post('/api/voice/stop', (req, res) => {
  stopVoiceRecognition()
  res.json({ ok: true })
})

// Voice audio data (binary)
app.post('/api/voice/audio', (req, res) => {
  if (!voiceProcess || !voiceProcess.stdin) {
    return res.status(400).json({ error: 'Voice process not running' })
  }

  try {
    const buffer = Buffer.isBuffer(req.body) ? req.body : Buffer.from(req.body)
    voiceProcess.stdin.write(buffer, (err) => {
      if (err) {
        console.error('[Voice] Write error:', err.message)
        return res.status(500).json({ error: err.message })
      }
      res.json({ ok: true })
    })
  } catch (e) {
    console.error('[Voice] Write error:', e.message)
    res.status(500).json({ error: e.message })
  }
})

// STT: start
app.post('/api/stt/start', (req, res) => {
  const { language } = req.body || {}
  startStt(language || null)
  res.json({ ok: true })
})

// STT: stop
app.post('/api/stt/stop', (req, res) => {
  stopStt()
  res.json({ ok: true })
})

// STT: audio chunk
app.post('/api/stt/audio', (req, res) => {
  if (!sttProcess || !sttProcess.stdin) {
    return res.status(400).json({ error: 'STT process not running' })
  }
  try {
    const buffer = Buffer.isBuffer(req.body) ? req.body : Buffer.from(req.body)
    sttProcess.stdin.write(buffer, (err) => {
      if (err) return res.status(500).json({ error: err.message })
      res.json({ ok: true })
    })
  } catch (e) {
    res.status(500).json({ error: e.message })
  }
})

// STT: ses dosyasını Whisper ile transkribe et
app.post('/api/stt/transcribe-file', upload.single('audio'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'Dosya yok' })

  const filePath = req.file.path
  const language = req.body.language || null
  const args = [path.join(__dirname, 'whisper_service_file.py'), filePath]
  if (language) args.push('--language', language)

  const proc = spawn('python3', args, { stdio: ['pipe', 'pipe', 'pipe'] })
  let out = ''
  proc.stdout.on('data', d => { out += d.toString() })
  proc.stderr.on('data', d => console.error('[STT-FILE]', d.toString()))
  proc.on('close', () => {
    try { fs.unlinkSync(filePath) } catch(e) {}
    try {
      const last = out.trim().split('\n').filter(l => l.trim()).pop()
      const msg = JSON.parse(last)
      res.json({ text: msg.text || '', language: msg.language || '' })
    } catch(e) {
      res.status(500).json({ error: 'Transkripsiyon başarısız: ' + e.message })
    }
  })
  proc.on('error', e => res.status(500).json({ error: e.message }))
})

// Save WAV file
app.post('/api/save-wav', (req, res) => {
  try {
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    const filePath = path.join(os.homedir(), 'Desktop', `morse-${timestamp}.wav`)

    const buffer = Buffer.from(req.body)
    fs.writeFileSync(filePath, buffer)

    res.json({ filePath })
  } catch (e) {
    console.error('[API] WAV save hatası:', e.message)
    res.status(500).json({ error: e.message })
  }
})

// RX ses kaydı kaydet
app.post('/api/rx-record', (req, res) => {
  try {
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    const filePath = path.join(os.homedir(), 'Desktop', `rx-recording-${timestamp}.wav`)

    const buffer = Buffer.from(req.file?.buffer || req.body)
    fs.writeFileSync(filePath, buffer)

    console.log('[RX] Kayıt kaydedildi:', filePath)
    res.json({ filePath, status: 'saved' })
  } catch (e) {
    console.error('[RX] Kayıt save hatası:', e.message)
    res.status(500).json({ error: e.message })
  }
})

// ── Çeviri endpoint ─────────────────────────────────────────
app.get('/translate', async (req, res) => {
    const text = (req.query.text || '').trim()
    const from = req.query.from || 'auto'
    const to   = req.query.to   || 'TR'
    if (!text) return res.json({ translation: '' })
    try {
        const translation = await deeplTranslate(text, from, to)
        res.json({ translation })
    } catch (e) {
        console.error('[/translate]', e.message)
        res.status(500).json({ error: e.message })
    }
})

// ── Decoder Manager API ─────────────────────────────────────
app.post('/api/decoder/:type/start', async (req, res) => {
  try {
    const result = await decoderManager.start(req.params.type, req.body)
    res.json(result)
  } catch (e) {
    console.error('[Decoder Start]', e.message)
    res.status(400).json({ error: e.message })
  }
})

app.post('/api/decoder/:type/stop', async (req, res) => {
  try {
    const result = await decoderManager.stop(req.params.type)
    res.json(result)
  } catch (e) {
    console.error('[Decoder Stop]', e.message)
    res.status(400).json({ error: e.message })
  }
})

app.get('/api/decoder/status', (req, res) => {
  res.json(decoderManager.getStatus())
})

app.post('/api/decoder/:type/input', (req, res) => {
  try {
    const { data } = req.body
    decoderManager.sendInput(req.params.type, data)
    res.json({ ok: true })
  } catch (e) {
    console.error('[Decoder Input]', e.message)
    res.status(400).json({ error: e.message })
  }
})

// ── Decoder Registration ────────────────────────────────────
const testDecodersPath = path.join(__dirname, 'test-decoders')

// Register test decoders
decoderManager.register('fm_radio', path.join(testDecodersPath, 'fm_radio_decoder.py'))
decoderManager.register('spectrum', path.join(testDecodersPath, 'spectrum_analyzer.py'))
decoderManager.register('gps', path.join(testDecodersPath, 'gps_decoder.py'))
decoderManager.register('iss', path.join(testDecodersPath, 'iss_monitor.py'))
decoderManager.register('shortwave', path.join(testDecodersPath, 'shortwave_monitor.py'))
decoderManager.register('ham-cq', path.join(testDecodersPath, 'ham_cq_monitor.py'))
decoderManager.register('dab', path.join(testDecodersPath, 'dab_monitor.py'))
decoderManager.register('weatherfax', path.join(testDecodersPath, 'weatherfax_monitor.py'))
decoderManager.register('mdt', path.join(testDecodersPath, 'mdt_monitor.py'))
decoderManager.register('ssb', path.join(testDecodersPath, 'ssb_monitor.py'))
decoderManager.register('digital', path.join(testDecodersPath, 'digital_monitor.py'))
decoderManager.register('gps-nav', path.join(testDecodersPath, 'gps_nav_monitor.py'))
decoderManager.register('noaa', path.join(testDecodersPath, 'noaa_monitor.py'))
decoderManager.register('meteor', path.join(testDecodersPath, 'meteor_scatter_monitor.py'))
decoderManager.register('oth', path.join(testDecodersPath, 'oth_radar_monitor.py'))
decoderManager.register('radio-astro', path.join(testDecodersPath, 'radio_astro_monitor.py'))
decoderManager.register('solar', path.join(testDecodersPath, 'solar_activity_monitor.py'))
decoderManager.register('inmarsat', path.join(testDecodersPath, 'inmarsat_monitor.py'))
decoderManager.register('triangulation', path.join(testDecodersPath, 'triangulation_monitor.py'))
decoderManager.register('drone', path.join(testDecodersPath, 'drone_monitor.py'))

console.log('[Decoder Manager] 20 test decoder kaydedildi')

// ── Server startup ──────────────────────────────────────────
httpServer = http.createServer(app)

httpServer.listen(PORT, () => {
  console.log(`[HTTP] Sunucu http://localhost:${PORT}`)
  startWsServer(httpServer)
})

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n[Server] Kapatılıyor...')
  stopVoiceRecognition()
  stopStt()
  await decoderManager.stopAll()
  if (wss) wss.close()
  if (httpServer) httpServer.close()
  process.exit(0)
})
