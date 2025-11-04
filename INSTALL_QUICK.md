# Instalação Rápida - Trichogramma Pi

Guia rápido para instalar o serviço na Raspberry Pi Zero 2 W.

## 🚀 Instalação em 5 Minutos

### 1. Preparar Sistema (uma única vez)

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3-pip bluetooth bluez libbluetooth-dev git

# Adicionar permissões
sudo usermod -a -G bluetooth pi
sudo usermod -a -G gpio pi

# IMPORTANTE: Logout e login novamente
exit
```

### 2. Instalar Serviço

```bash
# Clonar ou transferir projeto para /home/pi/trichogramma-pi

# Instalar dependências Python
cd ~/trichogramma-pi
pip3 install -r requirements.txt

# Criar diretório de log
sudo mkdir -p /var/log
sudo touch /var/log/trichogramma-service.log
sudo chown pi:pi /var/log/trichogramma-service.log
```

### 3. Configurar

```bash
# Editar config.yaml e definir o pino do servo
nano config.yaml

# Altere a linha:
# pwm_pin: 18  # <-- SEU PINO BCM AQUI
```

### 4. Testar (Recomendado)

```bash
cd ~/trichogramma-pi/service
python3 main.py

# Deve aparecer:
# "INFO: Servidor Bluetooth aguardando conexões..."
# 
# Conecte via Bluetooth e envie: PING
# Deve receber: PONG
#
# Ctrl+C para parar
```

### 5. Habilitar Auto-Start

```bash
sudo cp ~/trichogramma-pi/systemd/trichogramma.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trichogramma
sudo systemctl start trichogramma
```

### 6. Verificar

```bash
# Ver status
sudo systemctl status trichogramma

# Ver logs em tempo real
sudo journalctl -u trichogramma -f

# Testar reboot
sudo reboot
# Aguarde ~30s e conecte via Bluetooth
```

## ✅ Pronto!

O serviço agora inicia automaticamente toda vez que a Pi ligar.

## 🔧 Comandos Úteis

```bash
# Parar serviço
sudo systemctl stop trichogramma

# Reiniciar serviço
sudo systemctl restart trichogramma

# Ver logs
sudo journalctl -u trichogramma -n 100

# Desabilitar auto-start
sudo systemctl disable trichogramma
```

## 📡 Comandos Bluetooth

Conecte via app Bluetooth e envie:

- `PING` - Testa conexão
- `STATUS` - Status do sistema
- `SET_ANGLE:90` - Move servo para 90°
- `CALIBRAR` - Executa calibração completa

**Documentação completa**: Ver [README.md](README.md)

