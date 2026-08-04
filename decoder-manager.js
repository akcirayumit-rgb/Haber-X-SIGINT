/**
 * Decoder Manager — SDR dekoderlerinin yaşam döngüsünü yönet
 * Process spawn/kill, I/O handling, error recovery
 */

const { spawn } = require('child_process');
const path = require('path');
const EventEmitter = require('events');

class Decoder extends EventEmitter {
  constructor(name, scriptPath, args = []) {
    super();
    this.name = name;
    this.scriptPath = scriptPath;
    this.args = args;
    this.process = null;
    this.isRunning = false;
    this.lastError = null;
  }

  start(params = {}) {
    return new Promise((resolve, reject) => {
      if (this.isRunning) {
        return reject(new Error(`${this.name} zaten çalışıyor`));
      }

      try {
        const args = [this.scriptPath, ...this.args];
        if (params.frequency) args.push('--freq', params.frequency);
        if (params.language) args.push('--lang', params.language);
        if (params.gain) args.push('--gain', params.gain);

        // RADYO (FM/AM/HF/DAB) specific parameters for RTL-SDR
        if (this.name === 'fm_radio') {
          if (params.band) args.push('--band', params.band);
          if (params.sample_rate) args.push('--sample-rate', params.sample_rate);
          if (params.bandwidth) args.push('--bandwidth', params.bandwidth);
          if (params.ppm !== undefined) args.push('--ppm', params.ppm);
          if (params.demod_type) args.push('--demod', params.demod_type);
          if (params.scan_start) args.push('--scan-start', params.scan_start);
          if (params.scan_stop) args.push('--scan-stop', params.scan_stop);
          if (params.scan_step) args.push('--scan-step', params.scan_step);
          // Ses işleme zinciri (preamp / filtre / gürültü kesme)
          if (params.preamp_db) args.push('--preamp-db', params.preamp_db);
          if (params.filter_type) args.push('--filter-type', params.filter_type);
          if (params.noise_cancel) args.push('--noise-cancel');
          if (params.noise_mode) args.push('--noise-mode', params.noise_mode);
        }

        console.log(`[Decoder] ${this.name} başlatılıyor:`, args.join(' '));

        this.process = spawn('python3', args, {
          stdio: ['pipe', 'pipe', 'pipe'],
          timeout: 30000
        });

        let buffer = '';

        this.process.stdout.on('data', (data) => {
          buffer += data.toString();
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.trim()) {
              try {
                const msg = JSON.parse(line);
                this.emit('data', msg);
              } catch (e) {
                console.error(`[${this.name}] Parse error:`, e.message);
              }
            }
          }
        });

        this.process.stderr.on('data', (data) => {
          const msg = data.toString();
          console.error(`[${this.name}]`, msg);
          this.lastError = msg;

          // Parse JSON from stderr lines marked with [JSON]: prefix
          // Handle multi-line stderr data by processing each line
          const lines = msg.split('\n');
          for (const line of lines) {
            if (line.includes('[JSON]:')) {
              try {
                const jsonStr = line.split('[JSON]:')[1].trim();
                if (jsonStr) {
                  const decoded = JSON.parse(jsonStr);
                  console.log(`[${this.name}] ✓ JSON → broadcast`);
                  this.emit('data', decoded);
                }
              } catch (e) {
                console.error(`[${this.name}] Parse error:`, e.message);
              }
            }
          }

          this.emit('error', msg);
        });

        this.process.on('error', (err) => {
          console.error(`[${this.name}] Process error:`, err.message);
          this.lastError = err.message;
          this.isRunning = false;
          this.emit('error', err.message);
          reject(err);
        });

        this.process.on('exit', (code, signal) => {
          console.log(`[${this.name}] çıkış: code=${code}, signal=${signal}`);

          // Flush remaining buffer (last incomplete line)
          if (buffer.trim()) {
            try {
              const msg = JSON.parse(buffer);
              this.emit('data', msg);
              console.log(`[${this.name}] Flushed buffered JSON on exit`);
            } catch (e) {
              console.error(`[${this.name}] Final buffer parse error:`, e.message);
            }
          }

          this.isRunning = false;
          this.emit('exit', { code, signal });
        });

        this.isRunning = true;
        resolve({ status: 'started', decoder: this.name });
      } catch (err) {
        reject(err);
      }
    });
  }

  stop() {
    return new Promise((resolve) => {
      if (!this.process) {
        return resolve({ status: 'not_running' });
      }

      console.log(`[Decoder] ${this.name} durduruluyur...`);

      const timeout = setTimeout(() => {
        if (this.process) {
          this.process.kill('SIGKILL');
        }
        resolve({ status: 'killed' });
      }, 5000);

      this.process.on('exit', () => {
        clearTimeout(timeout);
        this.isRunning = false;
        resolve({ status: 'stopped', decoder: this.name });
      });

      try {
        this.process.stdin.end();
      } catch (e) {}
      this.process.kill('SIGTERM');
    });
  }

  sendInput(data) {
    if (!this.process || !this.isRunning) {
      throw new Error(`${this.name} çalışmıyor`);
    }
    this.process.stdin.write(data);
  }

  getStatus() {
    return {
      name: this.name,
      running: this.isRunning,
      lastError: this.lastError
    };
  }
}

class DecoderManager {
  constructor() {
    this.decoders = new Map();
    this.listeners = new Map(); // WebSocket listeners by type
  }

  register(name, scriptPath, args = []) {
    if (this.decoders.has(name)) {
      throw new Error(`${name} zaten kayıtlı`);
    }

    const decoder = new Decoder(name, scriptPath, args);

    // Decoder output → WebSocket broadcast
    decoder.on('data', (data) => {
      this.broadcast(`decoder:${name}`, data);
    });

    decoder.on('error', (error) => {
      this.broadcast(`decoder:${name}:error`, { error });
    });

    this.decoders.set(name, decoder);
    console.log(`[DecoderManager] ${name} kaydedildi`);
    return decoder;
  }

  async start(name, params = {}) {
    const decoder = this.decoders.get(name);
    if (!decoder) {
      throw new Error(`${name} decoder bulunamadı`);
    }
    return decoder.start(params);
  }

  async stop(name) {
    const decoder = this.decoders.get(name);
    if (!decoder) {
      throw new Error(`${name} decoder bulunamadı`);
    }
    return decoder.stop();
  }

  sendInput(name, data) {
    const decoder = this.decoders.get(name);
    if (!decoder) {
      throw new Error(`${name} decoder bulunamadı`);
    }
    decoder.sendInput(data);
  }

  getStatus() {
    const status = {};
    for (const [name, decoder] of this.decoders) {
      status[name] = decoder.getStatus();
    }
    return status;
  }

  // WebSocket integration
  subscribe(listener, type) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    this.listeners.get(type).add(listener);
  }

  unsubscribe(listener, type) {
    const listeners = this.listeners.get(type);
    if (listeners) {
      listeners.delete(listener);
    }
  }

  broadcast(type, data) {
    const listeners = this.listeners.get(type) || new Set();
    const message = JSON.stringify({ type, data, timestamp: new Date().toISOString() });

    if (type.includes('fm_radio') && listeners.size > 0) {
      console.log(`[DecoderManager] Broadcasting ${type}: ${listeners.size} listeners, msg length: ${message.length}`);
    }

    for (const listener of listeners) {
      try {
        if (listener.readyState === 1) { // OPEN
          listener.send(message);
        }
      } catch (e) {
        console.error(`[DecoderManager] Broadcast error:`, e.message);
      }
    }
  }

  async stopAll() {
    console.log('[DecoderManager] Tüm dekoderler durduruluyur...');
    const promises = [];
    for (const [name, decoder] of this.decoders) {
      promises.push(decoder.stop());
    }
    await Promise.all(promises);
  }
}

module.exports = { DecoderManager, Decoder };
