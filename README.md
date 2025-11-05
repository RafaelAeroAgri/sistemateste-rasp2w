# 🚁 Trichogramma Pi - Sistema de Controle de Servo

Sistema para controlar servo motor via WiFi em Raspberry Pi Zero 2 W.

---

## 📋 Visão Geral

- **Hardware**: Raspberry Pi Zero 2 W
- **Comunicação**: WiFi Hotspot (TrichoPi)
- **Controle**: Servo motor via GPIO 4 (BCM)
- **Interface**: API HTTP REST (porta 8080)
- **PWM**: pigpio (hardware, sem jitter)

---

## ⚡ Instalação Rápida

### 1. Clonar repositório

```bash
cd ~
git clone https://github.com/RafaelAeroAgri/sistemateste-rasp2w.git trichogramma-pi
cd trichogramma-pi
```

### 2. Executar instalação completa

```bash
chmod +x install.sh
./install.sh
```

O script instala:
- ✅ RaspAP (gerenciamento WiFi)
- ✅ pigpio (controle PWM)
- ✅ Serviço HTTP
- ✅ Configurações automáticas

### 3. Configurar hotspot

Após instalação, configure o hotspot:

**Opção A: Via interface web RaspAP**
1. Acesse: `http://raspberrypi.local` (conectado na mesma rede)
2. Login: `admin` / `secret`
3. **Hotspot** → Configurar:
   - SSID: `TrichoPi`
   - Senha: `tricho2025`
   - Channel: `6`
4. **DHCP Server** → Interface `uap0`:
   - Router IP: `10.3.141.1`
   - Starting IP: `10.3.141.50`
   - Ending IP: `10.3.141.254`
5. **System** → Reboot

**Opção B: Via linha de comando**

Execute no terminal da Pi:

```bash
# 1. Criar serviço que configura uap0
sudo tee /etc/systemd/system/create-uap0.service > /dev/null <<'EOF'
[Unit]
Description=Create uap0 virtual interface
Before=hostapd.service
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/bin/create-uap0.sh

[Install]
WantedBy=multi-user.target
RequiredBy=hostapd.service
EOF

# 2. Criar script de criação do uap0
sudo tee /usr/local/bin/create-uap0.sh > /dev/null <<'EOF'
#!/bin/bash
systemctl stop wpa_supplicant@wlan0 2>/dev/null || true
if ! ip link show uap0 2>/dev/null | grep -q uap0; then
    ip link set wlan0 down
    iw dev wlan0 interface add uap0 type __ap
fi
ip link set uap0 up
ip addr flush dev uap0
ip addr add 10.3.141.1/24 dev uap0
ip link set wlan0 up
EOF

sudo chmod +x /usr/local/bin/create-uap0.sh

# 3. Configurar hostapd para aguardar uap0
sudo mkdir -p /etc/systemd/system/hostapd.service.d
sudo tee /etc/systemd/system/hostapd.service.d/after-uap0.conf > /dev/null <<'EOF'
[Unit]
After=create-uap0.service
Requires=create-uap0.service
EOF

# 4. Habilitar serviços
sudo systemctl daemon-reload
sudo systemctl enable create-uap0
sudo systemctl start create-uap0

# 5. Reiniciar serviços
sudo systemctl restart hostapd
sudo systemctl restart dnsmasq

# 6. Reboot
sudo reboot
```

---

## 🔧 Configuração do Servo

O servo está conectado no **GPIO 4 (pino físico 7)**.

Para alterar, edite `config.yaml`:

```yaml
servo:
  pwm_pin: 4  # GPIO BCM
  frequency: 50
  min_duty: 2.5
  max_duty: 12.5
```

Após alterar, reinicie o serviço:

```bash
sudo systemctl restart trichogramma-http
```

---

## 📡 API HTTP

### Endpoints

**1. Ping**
```bash
GET /ping
# Resposta: {"status": "ok", "message": "PONG"}
```

**2. Status**
```bash
GET /status
# Resposta: {"servo_pin": 4, "current_angle": 90, "is_sweeping": false}
```

**3. Calibrar (sweep 0° → 180° → 90°)**
```bash
POST /calibrate
# Resposta: {"status": "ok", "message": "Calibração iniciada"}
```

**4. Definir ângulo**
```bash
POST /angle
Content-Type: application/json
{"angle": 90}
# Resposta: {"status": "ok", "angle": 90}
```

**5. Obter ângulo atual**
```bash
GET /angle
# Resposta: {"angle": 90}
```

**6. Parar movimento**
```bash
POST /stop
# Resposta: {"status": "ok", "message": "Movimento parado"}
```

---

## 🧪 Testar

```bash
# Conectar no WiFi TrichoPi (senha: tricho2025)

# Ping
curl http://10.3.141.1:8080/ping

# Status
curl http://10.3.141.1:8080/status

# Mover para 90°
curl -X POST http://10.3.141.1:8080/angle -H "Content-Type: application/json" -d '{"angle": 90}'

# Calibrar
curl -X POST http://10.3.141.1:8080/calibrate
```

---

## 📂 Estrutura do Projeto

```
trichogramma-pi/
├── config.yaml                      # Configuração
├── requirements.txt                 # Dependências Python
├── install.sh                       # Instalação completa
├── instalar_pigpio.sh              # Atualizar para pigpio
├── README.md                        # Este arquivo
├── INSTALACAO_RASPAP.md            # Guia RaspAP
├── ATUALIZAR_PIGPIO.md             # Guia pigpio
├── CORRIGIR_UAP0_BOOT.md           # Guia uap0
├── service/
│   ├── http_server.py              # Servidor HTTP
│   ├── servo_control.py            # Controle do servo
│   ├── logger.py                   # Logger
│   └── utils.py                    # Utilitários
├── systemd/
│   └── trichogramma-http.service   # Serviço systemd
└── tests/
    ├── client_console.py           # Cliente de teste
    └── manual_test_instructions.md # Testes manuais
```

---

## 🐛 Solução de Problemas

### Hotspot não aparece após reboot

Ver guia: `CORRIGIR_UAP0_BOOT.md`

### Servo com jitter/flickering

Ver guia: `ATUALIZAR_PIGPIO.md`

### Verificar logs

```bash
# Logs do serviço HTTP
sudo journalctl -u trichogramma-http -f

# Logs do hotspot
sudo journalctl -u hostapd -f

# Logs do pigpiod
sudo journalctl -u pigpiod -f
```

### Reiniciar serviços

```bash
sudo systemctl restart trichogramma-http
sudo systemctl restart hostapd
sudo systemctl restart dnsmasq
```

---

## 📝 Licença

MIT
