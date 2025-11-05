# 🔵 Configurar Bluetooth Sempre Ativo e Detectável

Este guia configura o Bluetooth para ficar **sempre ativo, detectável e aceitar conexões de qualquer dispositivo**.

---

## ⚡ Instalação Rápida (Comando Único)

Na Raspberry Pi, execute:

```bash
cd ~/trichogramma-pi && \
chmod +x scripts/bluetooth_discoverable.sh && \
sudo cp systemd/bluetooth-discoverable.service /etc/systemd/system/ && \
sudo sed -i "s|/home/aeroagri|$HOME|g" /etc/systemd/system/bluetooth-discoverable.service && \
sudo systemctl daemon-reload && \
sudo systemctl enable bluetooth-discoverable.service && \
sudo systemctl start bluetooth-discoverable.service && \
echo "" && echo "✅ Bluetooth configurado para sempre ativo!" && echo ""
```

---

## 📋 O Que Foi Feito

1. ✅ Script criado: `scripts/bluetooth_discoverable.sh`
   - Torna o Bluetooth sempre detectável
   - Ativa modo pareável automático
   - Configura agent para aceitar conexões sem confirmação

2. ✅ Serviço systemd: `bluetooth-discoverable.service`
   - Inicia automaticamente no boot
   - Executa após o bluetooth.service
   - Reinicia automaticamente se falhar

---

## 🧪 Verificar Status

```bash
# Ver se o serviço está ativo
sudo systemctl status bluetooth-discoverable

# Ver logs
sudo journalctl -u bluetooth-discoverable -n 20

# Ver status do Bluetooth
bluetoothctl show
```

**Deve mostrar:**
```
Discoverable: yes
Pairable: yes
Powered: yes
```

---

## 📱 Testar do Tablet/Celular

1. Abra **Configurações** → **Bluetooth**
2. Procure por dispositivos
3. Deve aparecer: **"raspberrypi"** ou **"trichopi"**
4. Toque para parear
5. Deve parear automaticamente (sem precisar confirmar código)

---

## 🔧 Comandos Úteis

### Verificar Bluetooth Manualmente

```bash
# Entrar no bluetoothctl
sudo bluetoothctl

# Comandos dentro:
show                    # Ver status
discoverable on         # Ativar detectável
pairable on            # Ativar pareável
devices                # Listar dispositivos pareados
exit                   # Sair
```

### Reiniciar Serviços Bluetooth

```bash
# Reiniciar Bluetooth base
sudo systemctl restart bluetooth

# Reiniciar serviço de descoberta
sudo systemctl restart bluetooth-discoverable

# Ver status de ambos
sudo systemctl status bluetooth
sudo systemctl status bluetooth-discoverable
```

### Listar Dispositivos Pareados

```bash
# Via bluetoothctl
bluetoothctl devices

# Ou
bluetoothctl paired-devices
```

### Remover Dispositivo Pareado

```bash
sudo bluetoothctl
remove AA:BB:CC:DD:EE:FF
exit
```

---

## 🔐 Segurança

### ⚠️ Modo Atual: Aberto

Configuração atual aceita **qualquer dispositivo** sem confirmação.

**Vantagens:**
- ✅ Fácil de conectar
- ✅ Não precisa acesso físico à Pi
- ✅ Ideal para desenvolvimento/teste

**Desvantagens:**
- ⚠️ Qualquer pessoa próxima pode parear
- ⚠️ Menos seguro para produção

### 🔒 Aumentar Segurança (Opcional)

Se quiser exigir confirmação de pareamento:

```bash
# Editar o script
nano ~/trichogramma-pi/scripts/bluetooth_discoverable.sh

# Alterar esta linha:
agent NoInputNoOutput

# Para:
agent DisplayYesNo
# ou
agent KeyboardDisplay

# Reiniciar serviço
sudo systemctl restart bluetooth-discoverable
```

**Com `DisplayYesNo`:**
- Você verá solicitações de pareamento nos logs
- Pode aceitar via `bluetoothctl` conectado

**Com `KeyboardDisplay`:**
- Mostra PIN nos logs
- Usuário deve digitar o PIN no dispositivo

### 🛡️ Filtrar por MAC Address (Avançado)

Para aceitar apenas dispositivos específicos, edite o serviço principal:

```bash
nano ~/trichogramma-pi/service/bluetooth_server.py

# Adicione filtro na função accept_connection():
if self.client_address[0] not in ALLOWED_MACS:
    self.logger.warning(f"Conexão negada de {self.client_address}")
    self.client_sock.close()
    return False
```

---

## 🔄 Testar Auto-Start

```bash
# Reiniciar a Pi
sudo reboot

# Aguarde 30-40 segundos

# Do tablet/celular:
# 1. Abra Bluetooth
# 2. Procure dispositivos
# 3. Deve aparecer "raspberrypi" automaticamente
```

---

## 📊 Status Completo do Sistema

```bash
# Ver todos os serviços relacionados
systemctl status bluetooth
systemctl status bluetooth-discoverable
systemctl status trichogramma

# Ver logs de todos
journalctl -u bluetooth -u bluetooth-discoverable -u trichogramma -n 50
```

---

## 🐛 Troubleshooting

### Problema: Bluetooth não aparece nos dispositivos

**Solução 1: Verificar se está ativo**
```bash
sudo systemctl status bluetooth-discoverable
# Se não estiver ativo:
sudo systemctl start bluetooth-discoverable
```

**Solução 2: Executar manualmente**
```bash
sudo ~/trichogramma-pi/scripts/bluetooth_discoverable.sh
```

**Solução 3: Verificar com bluetoothctl**
```bash
sudo bluetoothctl
show
# Deve mostrar Discoverable: yes
```

### Problema: "Can't set scan mode on hci0"

**Isso é normal!** O erro aparece porque `hciconfig` é deprecated, mas o `bluetoothctl` funciona corretamente.

Verificar:
```bash
bluetoothctl show | grep Discoverable
# Deve mostrar: Discoverable: yes
```

### Problema: Bluetooth desaparece após conexão

Isso é comportamento padrão. Para manter sempre visível:

```bash
# Editar configuração do Bluetooth
sudo nano /etc/bluetooth/main.conf

# Adicionar/descomentar:
[General]
DiscoverableTimeout = 0
PairableTimeout = 0

# Reiniciar Bluetooth
sudo systemctl restart bluetooth
sudo systemctl restart bluetooth-discoverable
```

### Problema: Dispositivo não consegue conectar ao serviço

**Checklist:**
1. ✅ Bluetooth-discoverable está rodando? `systemctl status bluetooth-discoverable`
2. ✅ Serviço trichogramma está rodando? `systemctl status trichogramma`
3. ✅ Dispositivo está pareado? `bluetoothctl devices`
4. ✅ Ver logs: `journalctl -u trichogramma -f`

---

## 🎯 Resumo - Como Funciona

```
Boot da Raspberry Pi
  ↓
bluetooth.service inicia
  ↓
bluetooth-discoverable.service inicia
  ↓
Bluetooth fica SEMPRE detectável e pareável
  ↓
Qualquer dispositivo pode parear
  ↓
trichogramma.service aguarda conexões
  ↓
App/Tablet conecta ao "TrichoPi"
  ↓
Comandos funcionam normalmente
```

---

## 📝 Comandos de Diagnóstico

```bash
# Status geral
sudo systemctl status bluetooth bluetooth-discoverable trichogramma

# Logs em tempo real
sudo journalctl -f

# Teste manual do Bluetooth
sudo bluetoothctl
> show
> devices
> exit

# Testar se o serviço RFCOMM está anunciado
sdptool browse local | grep -A 5 "Serial Port"
```

---

**Pronto! Seu Bluetooth está sempre ativo e detectável!** 🎉

Qualquer dispositivo pode procurar, parear e conectar automaticamente ao serviço TrichoPi.

