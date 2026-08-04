const { app, BrowserWindow, session } = require('electron');
const { spawn } = require('child_process');
const http = require('http');
const path = require('path');

// Ana Haber-X 3000'i kullanıyor; SIGINT kendi portunda çalışır
const PORT = Number(process.env.SIGINT_PORT) || 3001;

let mainWindow;
let serverProcess;

function getResourcesPath() {
  // Paketlenmiş .app içinde process.resourcesPath, dev'de __dirname
  return app.isPackaged ? process.resourcesPath : __dirname;
}

// Sunucu ayakta mı? (başka bir örnek zaten çalışıyor olabilir)
function isServerUp() {
  return new Promise((resolve) => {
    const req = http.get({ host: '127.0.0.1', port: PORT, path: '/', timeout: 800 }, (res) => {
      res.resume();
      resolve(true);
    });
    req.on('error', () => resolve(false));
    req.on('timeout', () => { req.destroy(); resolve(false); });
  });
}

async function startServer() {
  if (await isServerUp()) {
    console.log(`[Server] ${PORT} portunda zaten çalışıyor, yeniden başlatılmadı`);
    return;
  }

  const resourcesPath = getResourcesPath();
  const serverPath = path.join(resourcesPath, 'server.js');

  // 'node' PATH'te olmayabilir (Finder'dan açılan .app minimal PATH alır);
  // Electron'un kendi binary'sini Node olarak çalıştır.
  const env = { ...process.env, ELECTRON_RUN_AS_NODE: '1', SIGINT_PORT: String(PORT) };

  // Paketliyken server.js asar'ın dışında ama node_modules içinde kalıyor;
  // çözümleyiciye asar içindeki node_modules'ü göster.
  if (app.isPackaged) {
    env.NODE_PATH = path.join(resourcesPath, 'app.asar', 'node_modules');
  }

  serverProcess = spawn(process.execPath, [serverPath], {
    cwd: resourcesPath,
    env,
    stdio: 'inherit'
  });

  serverProcess.on('error', (e) => {
    console.error('[Server] Başlatma hatası:', e.message);
  });
  serverProcess.on('exit', (code, signal) => {
    if (code !== 0) console.error(`[Server] Beklenmedik çıkış: code=${code} signal=${signal}`);
  });
}

// Sabit gecikme yerine sunucu gerçekten hazır olana kadar bekle
async function waitForServer(timeoutMs = 20000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (await isServerUp()) return true;
    await new Promise((r) => setTimeout(r, 300));
  }
  return false;
}

app.on('ready', async () => {
  // Mikrofon iznini otomatik ver
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    if (permission === 'media') {
      callback(true);
    } else {
      callback(false);
    }
  });

  await startServer();

  const ready = await waitForServer();
  if (!ready) {
    console.error(`[Server] ${PORT} portu ${20}s içinde yanıt vermedi; pencere yine de açılıyor`);
  }
  createWindow();
});

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1100,
    minHeight: 700,
    title: 'Haber X-SIGINT',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: false,
      sandbox: false
    }
  });

  // Sessiz boş pencere yerine hatayı görünür kıl
  mainWindow.webContents.on('did-fail-load', (_e, errCode, errDesc, url) => {
    console.error(`[Pencere] Yükleme başarısız: ${errDesc} (${errCode}) — ${url}`);
  });

  mainWindow.loadURL(`http://localhost:${PORT}`);
  mainWindow.on('closed', () => { mainWindow = null; });
}

app.on('before-quit', () => {
  if (serverProcess) serverProcess.kill();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (mainWindow === null) createWindow();
});
