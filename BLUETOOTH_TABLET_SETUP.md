# Guia de Conexão Bluetooth - Tablet com Raspberry Pi

Este guia mostra como parear e conectar seu tablet Android ao serviço Trichogramma Pi via Bluetooth.

## 📱 Pré-requisitos

- ✅ Raspberry Pi ligada e com o serviço instalado
- ✅ Tablet Android com Bluetooth
- ✅ App de terminal Bluetooth instalado no tablet

---

## 📲 PASSO 1: Instalar App no Tablet

### Aplicativos Recomendados (Android)

**Opção 1 - Serial Bluetooth Terminal** (Recomendado)
- 🔗 Play Store: [Serial Bluetooth Terminal](https://play.google.com/store/apps/details?id=de.kai_morich.serial_bluetooth_terminal)
- ✅ Simples e funcional
- ✅ Gratuito
- ✅ Suporta SPP (Serial Port Profile)

**Opção 2 - Bluetooth Terminal**
- 🔗 Play Store: [Bluetooth Terminal](https://play.google.com/store/apps/details?id=Qwerty.BluetoothTerminal)
- ✅ Interface limpa
- ✅ Gratuito

**Opção 3 - BlueTerm**
- 🔗 Play Store: [BlueTerm](https://play.google.com/store/apps/details?id=es.pymasde.blueterm)
- ✅ Open source
- ✅ Leve

---

## 🔧 PASSO 2: Configurar Bluetooth na Raspberry Pi

Conecte via SSH na Raspberry Pi:

```bash
ssh aeroagri@raspberrypi.local
```

### 2.1 Verificar Status do Bluetooth

```bash
# Verificar se o Bluetooth está ativo
sudo systemctl status bluetooth

# Se não estiver ativo, inicie:
sudo systemctl start bluetooth
sudo systemctl enable bluetooth
```

### 2.2 Tornar a Pi Detectável

```bash
# Entrar no bluetoothctl
sudo bluetoothctl

# Comandos dentro do bluetoothctl:
power on
agent on
default-agent
discoverable on
pairable on
scan on
```

Deixe o `bluetoothctl` rodando e vá para o próximo passo.

---

## 📱 PASSO 3: Parear o Tablet

### 3.1 No Tablet

1. Abra **Configurações** → **Bluetooth**
2. Ative o Bluetooth
3. Procure dispositivos disponíveis
4. Você deve ver: **"raspberrypi"** ou **"trichopi"**
5. Toque para parear

### 3.2 De Volta na Raspberry Pi (bluetoothctl)

Quando o tablet tentar parear, você verá algo como:

```
[NEW] Device AA:BB:CC:DD:EE:FF Tablet_Nome
Request confirmation
[agent] Confirm passkey 123456 (yes/no):
```

Digite:
```
yes
```

**IMPORTANTE**: Anote o endereço MAC que apareceu (ex: `AA:BB:CC:DD:EE:FF`)

### 3.3 Confiar e Parear

No `bluetoothctl`, execute (substitua pelo MAC do seu tablet):

```bash
trust AA:BB:CC:DD:EE:FF
pair AA:BB:CC:DD:EE:FF
```

Confirme no tablet se pedido.

### 3.4 Sair do bluetoothctl

```bash
exit
```

---

## 🚀 PASSO 4: Conectar ao Serviço TrichoPi

### 4.1 Iniciar o Serviço (se não estiver rodando)

```bash
# Ver se está rodando
sudo systemctl status trichogramma

# Se não estiver, inicie:
sudo systemctl start trichogramma

# Ver logs em tempo real
sudo journalctl -u trichogramma -f
```

### 4.2 No App do Tablet

1. Abra o **Serial Bluetooth Terminal**
2. Toque no ícone de **menu** (☰) ou **dispositivos**
3. Selecione **"TrichoPi"** ou **"raspberrypi"**
4. Conecte

Você deve ver: **"Conectado"**

Na Raspberry Pi, os logs devem mostrar:
```
INFO: Cliente conectado: [AA:BB:CC:DD:EE:FF]
```

---

## ✅ PASSO 5: Testar Comandos

No app do tablet, digite e envie:

### Teste 1: PING
```
PING
```
Resposta esperada: `PONG`

### Teste 2: STATUS
```
STATUS
```
Resposta esperada: JSON com informações do sistema

### Teste 3: Mover Servo
```
SET_ANGLE:90
```
Resposta esperada: `OK`
O servo deve se mover para 90°

### Teste 4: Calibração
```
CALIBRAR
```
Resposta esperada: `CALIBRACAO_OK` (após alguns segundos)
O servo faz sweep completo: 0° → 180° → 90°

### Teste 5: Ângulo Atual
```
GET_ANGLE
```
Resposta esperada: `ANGLE:90` (ou o ângulo atual)

---

## 🎯 Configurações do App (Serial Bluetooth Terminal)

Para melhor experiência, configure:

1. **Menu** → **Configurações**
2. **Terminador de Linha** (Line Terminator):
   - Enviar: `\n` (Newline)
   - Receber: `\n` (Newline)
3. **Auto Scroll**: Ativado
4. **Timestamp**: Ativado (opcional)

---

## 🔧 Troubleshooting

### Problema: Tablet não encontra a Raspberry Pi

**Solução**:
```bash
# Na Pi, tornar detectável novamente
sudo hciconfig hci0 piscan

# Ou via bluetoothctl
sudo bluetoothctl
> discoverable on
> pairable on
```

### Problema: Pareamento falha

**Solução**:
```bash
# Remover pareamento anterior
sudo bluetoothctl
> remove AA:BB:CC:DD:EE:FF
> exit

# Reiniciar Bluetooth
sudo systemctl restart bluetooth

# Tentar novamente
```

### Problema: Conecta mas não recebe respostas

**Checklist**:
1. ✅ Serviço está rodando? `sudo systemctl status trichogramma`
2. ✅ Logs mostram conexão? `sudo journalctl -u trichogramma -f`
3. ✅ Comandos terminam com `\n` (Enter)?
4. ✅ App configurado para SPP (Serial Port Profile)?

### Problema: "Connection refused" ou "Not available"

**Solução**:
```bash
# Ver se o serviço RFCOMM está anunciado
sdptool browse local

# Deve aparecer algo com "Serial Port" e UUID 00001101...

# Se não aparecer, reinicie o serviço:
sudo systemctl restart trichogramma
```

---

## 📋 Comandos Rápidos

| Comando | Descrição | Resposta |
|---------|-----------|----------|
| `PING` | Testa conexão | `PONG` |
| `STATUS` | Info do sistema | JSON |
| `SET_ANGLE:45` | Move para 45° | `OK` |
| `GET_ANGLE` | Ângulo atual | `ANGLE:NN` |
| `CALIBRAR` | Calibração completa | `CALIBRACAO_OK` |
| `STOP` | Para movimento | `STOPPED` |

---

## 🔄 Reconexão Automática

Após parear uma vez:

1. **Abra o app no tablet**
2. **Selecione "TrichoPi"**
3. **Conecte** (não precisa parear novamente)

Se a Raspberry Pi reiniciar:
- O serviço inicia automaticamente
- Basta reconectar do app

---

## 💡 Dicas

### Manter Conexão Estável

1. **Mantenha os dispositivos próximos** (< 5 metros)
2. **Evite obstáculos** entre Pi e tablet
3. **Bateria do tablet carregada** (Bluetooth consome bateria)

### Salvar Comandos Favoritos (Serial Bluetooth Terminal)

No app:
1. **Menu** → **Macros**
2. Adicione comandos frequentes
3. Execute com um toque

Exemplo de macros úteis:
- Macro 1: `PING`
- Macro 2: `STATUS`
- Macro 3: `SET_ANGLE:90`
- Macro 4: `CALIBRAR`

---

## 🎉 Pronto!

Agora você pode controlar o servo da Raspberry Pi diretamente do seu tablet via Bluetooth!

### Próximos Passos

- Testar todos os comandos
- Criar macros no app para comandos frequentes
- Integrar com seu app Flutter (se houver)

---

**Desenvolvido para: Raspberry Pi Zero 2 W + Tablet Android**
**Projeto: Sistema Trichogramma**

