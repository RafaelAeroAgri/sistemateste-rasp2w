# 📡 WiFi Hotspot - Solução Definitiva

Sistema WiFi Hotspot para uso em campo sem internet. Muito mais confiável que Bluetooth!

## 🎯 Como Funciona

```
Raspberry Pi liga
  ↓
Cria WiFi "TrichoPi" (senha: tricho2025)
  ↓
Tablet conecta no WiFi
  ↓
App acessa http://192.168.4.1:8080
  ↓
Controla servo via HTTP REST
```

---

## ⚡ Instalação Rápida

**Na Raspberry Pi:**

```bash
cd ~/trichogramma-pi
chmod +x setup_wifi_hotspot.sh
sudo ./setup_wifi_hotspot.sh
```

Aguarde instalação (~2 minutos) e depois:

```bash
sudo reboot
```

---

## 📱 Como Usar

### 1. Conectar ao WiFi

**No tablet:**
1. Configurações → WiFi
2. Procure: **TrichoPi**
3. Senha: **tricho2025**
4. Conecte

### 2. Abrir o App

Abra o app Trichogramma e vá em **"Conectar Dispenser"**

O app vai conectar automaticamente em `http://192.168.4.1:8080`

### 3. Controlar o Servo

- Toque em **"CALIBRAR SERVO"** (botão vermelho grande)
- Use o **slider** para mover o servo
- Toque nos **botões de ângulo** (0°, 45°, 90°, 135°, 180°)

---

## 🔧 Configuração do Serviço HTTP

```bash
# Copiar serviço
sudo cp ~/trichogramma-pi/systemd/trichogramma-http.service /etc/systemd/system/

# Ajustar usuário
sudo sed -i "s|/home/aeroagri|$HOME|g" /etc/systemd/system/trichogramma-http.service

# Habilitar
sudo systemctl daemon-reload
sudo systemctl enable trichogramma-http
sudo systemctl start trichogramma-http

# Ver status
sudo systemctl status trichogramma-http

# Ver logs
sudo journalctl -u trichogramma-http -f
```

---

## 📊 Endpoints HTTP

| Método | Endpoint | Descrição | Body |
|--------|----------|-----------|------|
| GET | `/ping` | Teste | - |
| GET | `/status` | Status | - |
| GET | `/angle` | Ângulo atual | - |
| POST | `/calibrate` | Calibrar | - |
| POST | `/angle` | Definir ângulo | `{"angle": 90}` |
| POST | `/stop` | Parar | - |

---

## ✅ Vantagens sobre Bluetooth

- ✅ **Sem problemas de pareamento**
- ✅ **Mais rápido** (HTTP vs SPP)
- ✅ **Mais confiável** (TCP vs Bluetooth)
- ✅ **Funciona em campo** (sem internet necessária)
- ✅ **Múltiplos dispositivos** podem conectar
- ✅ **Debug fácil** (pode testar no navegador)

---

## 🧪 Testar Manualmente

No navegador ou terminal:

```bash
# PING
curl http://192.168.4.1:8080/ping

# STATUS
curl http://192.168.4.1:8080/status

# CALIBRAR
curl -X POST http://192.168.4.1:8080/calibrate

# DEFINIR ÂNGULO
curl -X POST http://192.168.4.1:8080/angle -H "Content-Type: application/json" -d '{"angle": 90}'
```

---

## 🔐 Segurança

**Configuração Atual:**
- WiFi com senha WPA2
- HTTP sem autenticação (rede privada)

**Para Produção (opcional):**
- Adicionar autenticação HTTP Basic
- Usar HTTPS
- Filtrar por MAC address

---

## 🐛 Troubleshooting

### WiFi não aparece

```bash
sudo systemctl status hostapd
sudo journalctl -u hostapd -n 50
```

### Não consegue conectar

```bash
# Verificar IP
ip addr show wlan0
# Deve mostrar: 192.168.4.1

# Verificar serviço HTTP
sudo systemctl status trichogramma-http
```

### Alterar senha WiFi

```bash
sudo nano /etc/hostapd/hostapd.conf
# Altere: wpa_passphrase=SUASENHA
sudo systemctl restart hostapd
```

---

**Sistema WiFi muito mais confiável que Bluetooth!** 🚀

