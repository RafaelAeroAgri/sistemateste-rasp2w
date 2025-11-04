# 🚀 Instalação Rápida - Uma Linha de Comando

Instale o Trichogramma Pi Service automaticamente com **um único comando**!

---

## ⚡ Instalação Automática

Na sua Raspberry Pi Zero 2 W, conectado via SSH, execute:

```bash
bash <(curl -sL https://raw.githubusercontent.com/RafaelAeroAgri/sistemateste-rasp2w/main/setup_from_git.sh)
```

**Isso vai:**
- ✅ Atualizar o sistema
- ✅ Instalar todas as dependências
- ✅ Baixar o código do Git
- ✅ Configurar permissões
- ✅ Instalar pacotes Python
- ✅ Configurar para rodar automaticamente no boot

**Tempo estimado**: 5-10 minutos

---

## 📋 Após a Instalação

### 1️⃣ LOGOUT e LOGIN (Obrigatório)

```bash
exit
# Reconecte via SSH
ssh aeroagri@raspberrypi.local
```

### 2️⃣ Testar Manualmente

```bash
cd ~/trichogramma-pi/service
python3 main.py
```

Deve aparecer:
```
INFO: Servidor Bluetooth aguardando conexões...
```

**Deixe rodando** e vá para o próximo passo.

### 3️⃣ Parear Tablet

**Em outro terminal SSH** (ou no tablet):

```bash
ssh aeroagri@raspberrypi.local
sudo bluetoothctl
```

No bluetoothctl:
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
2. Pareie "raspberrypi"

**De volta ao bluetoothctl:**
```bash
trust [MAC_DO_TABLET]
pair [MAC_DO_TABLET]
exit
```

### 4️⃣ Testar Conexão

**No app do tablet** (Serial Bluetooth Terminal):
1. Conecte ao "TrichoPi"
2. Envie: `PING`
3. Deve receber: `PONG`

**Teste o servo:**
```
SET_ANGLE:90
```

Se funcionou, pressione `Ctrl+C` no terminal onde o serviço está rodando.

### 5️⃣ Habilitar Auto-Start

```bash
sudo systemctl start trichogramma
sudo systemctl status trichogramma
```

Deve mostrar: `Active: active (running)`

### 6️⃣ Testar Reboot

```bash
sudo reboot
```

Aguarde 30 segundos, reconecte do tablet → Deve funcionar automaticamente!

---

## 📱 App Recomendado para Tablet

**Serial Bluetooth Terminal**
- 🔗 [Play Store](https://play.google.com/store/apps/details?id=de.kai_morich.serial_bluetooth_terminal)
- ✅ Gratuito
- ✅ Fácil de usar

---

## 🔧 Comandos Bluetooth Disponíveis

| Comando | Descrição |
|---------|-----------|
| `PING` | Testa conexão |
| `STATUS` | Info do sistema (JSON) |
| `SET_ANGLE:90` | Move servo para 90° |
| `GET_ANGLE` | Retorna ângulo atual |
| `CALIBRAR` | Sweep completo (0→180→90) |
| `STOP` | Para movimento |

---

## 📖 Documentação Completa

- **Guia Bluetooth Tablet**: `BLUETOOTH_TABLET_SETUP.md`
- **README Completo**: `README.md`
- **Testes Manuais**: `tests/manual_test_instructions.md`

---

## 🐛 Problemas?

```bash
# Ver logs
sudo journalctl -u trichogramma -f

# Reiniciar serviço
sudo systemctl restart trichogramma

# Parar serviço
sudo systemctl stop trichogramma
```

---

## ⚙️ Configuração do Servo

O servo está configurado para **GPIO 4 (pino físico 7)**.

**Conexões:**
- Vermelho (VCC) → Pino 2 (5V)
- Preto (GND) → Pino 6 (GND)
- Sinal → GPIO 4 (Pino físico 7) ✅

Para alterar o pino, edite: `~/trichogramma-pi/config.yaml`

---

**Pronto! Sistema funcionando automaticamente no boot!** 🎉

