# 🚀 Continuar Instalação - A Partir do Erro

Você estava no **PASSO 5/7** e teve um erro ao instalar pacotes Python.

## ✅ Resolver Agora (Comando Único)

Na sua Raspberry Pi (`aeroagri@raspberrypi`), execute:

```bash
cd ~/trichogramma-pi && \
sudo apt install -y python3-bluez libbluetooth-dev && \
pip3 install --break-system-packages pybluez RPi.GPIO==0.7.1 PyYAML==6.0.1 psutil==5.9.5 && \
echo "✓ Pacotes instalados com sucesso!"
```

---

## 📋 Próximos Passos (Do PASSO 6 em diante)

### PASSO 6/7: Configurar systemd

```bash
cd ~/trichogramma-pi

# Ajustar o arquivo de serviço para seu usuário
sed -i "s/User=pi/User=aeroagri/g" systemd/trichogramma.service
sed -i "s/Group=pi/Group=aeroagri/g" systemd/trichogramma.service
sed -i "s|/home/pi/trichogramma-pi|$HOME/trichogramma-pi|g" systemd/trichogramma.service

# Copiar e habilitar o serviço
sudo cp systemd/trichogramma.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trichogramma.service

echo "✓ Serviço systemd configurado"
```

### PASSO 7/7: Configurar Bluetooth (Sempre Ativo)

```bash
# Habilitar Bluetooth
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Configurar para sempre detectável e pareável
cd ~/trichogramma-pi
chmod +x scripts/bluetooth_discoverable.sh
sudo cp systemd/bluetooth-discoverable.service /etc/systemd/system/
sudo sed -i "s|/home/aeroagri|$HOME|g" /etc/systemd/system/bluetooth-discoverable.service
sudo systemctl daemon-reload
sudo systemctl enable bluetooth-discoverable.service
sudo systemctl start bluetooth-discoverable.service

echo "✓ Bluetooth configurado: sempre ativo e detectável"
```

**O que foi configurado:**
- ✅ Bluetooth sempre ligado
- ✅ Sempre detectável (qualquer dispositivo pode encontrar)
- ✅ Sempre pareável (aceita conexões automaticamente)
- ✅ Inicia automaticamente no boot

---

## ⚠️ IMPORTANTE: Logout e Login

**Você DEVE fazer logout e login** para aplicar as permissões de grupo:

```bash
exit
# Depois reconecte:
ssh aeroagri@raspberrypi.local
```

---

## 🧪 Testar o Serviço

Após fazer logout e login novamente:

```bash
cd ~/trichogramma-pi/service
python3 main.py
```

Deve aparecer:

```
Trichogramma Pi Service
============================================================
Dispositivo: Raspberry Pi Zero 2 W Rev 1.0
INFO: Servo inicializado no pino GPIO 4 (BCM)
INFO: Servo movido para 90° (duty cycle: 7.50%)
INFO: Servidor Bluetooth aguardando conexões na porta RFCOMM 1
INFO: Serviço 'TrichoPi' anunciado...
```

✅ **Se aparecer isso, está funcionando!**

**Deixe rodando** e vá para o próximo passo.

---

## 📱 Parear o Tablet

**Abra outro terminal SSH** (ou no tablet mesmo):

```bash
ssh aeroagri@raspberrypi.local
sudo bluetoothctl
```

No `bluetoothctl`:

```
power on
agent on
default-agent
discoverable on
pairable on
scan on
```

**No tablet:**
1. Configurações → Bluetooth
2. Ative o Bluetooth
3. Procure "raspberrypi"
4. Toque para parear

**De volta no `bluetoothctl`:**

```bash
# Quando aparecer o MAC do tablet (ex: AA:BB:CC:DD:EE:FF):
trust AA:BB:CC:DD:EE:FF
pair AA:BB:CC:DD:EE:FF
exit
```

---

## 📲 Conectar via App no Tablet

**App recomendado:** Serial Bluetooth Terminal
- [Download](https://play.google.com/store/apps/details?id=de.kai_morich.serial_bluetooth_terminal)

**No app:**
1. Menu → Devices → "TrichoPi"
2. Conectar

**Enviar comandos de teste:**

```
PING
```
Resposta: `PONG` ✅

```
STATUS
```
Resposta: JSON com info do sistema ✅

```
SET_ANGLE:90
```
Resposta: `OK` (servo deve mover) ✅

**Se tudo funcionou**, pressione `Ctrl+C` no terminal onde o serviço está rodando.

---

## 🚀 Habilitar Auto-Start

```bash
sudo systemctl start trichogramma
sudo systemctl status trichogramma
```

Deve mostrar: `Active: active (running)`

**Ver logs em tempo real:**

```bash
sudo journalctl -u trichogramma -f
```

Pressione `Ctrl+C` para sair.

---

## 🔄 Testar Reboot

```bash
sudo reboot
```

Aguarde ~30 segundos.

**Reconecte do tablet:**
1. Abra o app Serial Bluetooth Terminal
2. Conecte ao "TrichoPi"
3. Envie `PING`
4. Deve receber `PONG`

✅ **Funcionando automaticamente!**

---

## 📋 Comandos Úteis

```bash
# Ver status do serviço
sudo systemctl status trichogramma

# Reiniciar serviço
sudo systemctl restart trichogramma

# Parar serviço
sudo systemctl stop trichogramma

# Desabilitar auto-start
sudo systemctl disable trichogramma

# Ver logs
sudo journalctl -u trichogramma -n 50

# Ver logs em tempo real
sudo journalctl -u trichogramma -f
```

---

## 🎉 Pronto!

Seu sistema Trichogramma Pi está rodando e iniciará automaticamente toda vez que ligar a Raspberry Pi!

### 📖 Mais Documentação:

- `BLUETOOTH_TABLET_SETUP.md` - Guia detalhado Bluetooth
- `README.md` - Documentação completa
- `SOLUCAO_ERRO_PIP.md` - Explicação do erro que você teve

---

**Continue de onde parou! O erro está resolvido.** ✅

