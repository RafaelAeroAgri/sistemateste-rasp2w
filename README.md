# Trichogramma Pi Service

Serviço Bluetooth RFCOMM/SPP para controle de servo motor via comandos de texto em Raspberry Pi Zero 2 W (headless).

## 📋 Sumário

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalação do Zero na Raspberry Pi OS Lite](#instalação-do-zero-na-raspberry-pi-os-lite)
- [Configuração Inicial](#configuração-inicial)
- [Auto-Start no Boot (Systemd)](#auto-start-no-boot-systemd)
- [Comandos Suportados](#comandos-suportados)
- [Troubleshooting](#troubleshooting)
- [Estrutura do Projeto](#estrutura-do-projeto)

---

## ✨ Características

- Servidor Bluetooth RFCOMM/SPP (Serial Port Profile)
- Controle preciso de servo via PWM (GPIO)
- Comandos simples em texto (linha por linha)
- Rotina de calibração automática com sweep
- Logs detalhados em arquivo com rotação automática
- Serviço systemd com auto-start no boot
- Reinicialização automática em caso de falha
- Thread-safe e otimizado para Raspberry Pi Zero 2 W

---

## 📦 Requisitos

### Hardware
- Raspberry Pi Zero 2 W (ou modelos superiores)
- Servo motor (3 fios: VCC, GND, sinal)
- Fonte de alimentação adequada
- Adaptador Bluetooth integrado

### Software
- Raspberry Pi OS Lite (Bookworm ou Bullseye recomendado)
- Python 3.9 ou superior
- BlueZ (sistema Bluetooth Linux)
- Pacotes Python: `pybluez`, `RPi.GPIO`, `pyyaml`

---

## 🚀 Instalação do Zero na Raspberry Pi OS Lite

Este guia assume que você tem uma Raspberry Pi com Raspberry Pi OS Lite instalado e acesso SSH configurado.

### Passo 1: Atualizar o Sistema

Conecte-se via SSH à sua Raspberry Pi e atualize os pacotes:

```bash
sudo apt update
sudo apt upgrade -y
```

### Passo 2: Instalar Dependências do Sistema

Instale as ferramentas necessárias para Bluetooth e Python:

```bash
sudo apt install -y python3-pip bluetooth bluez libbluetooth-dev git
```

Verifique a instalação do Python:

```bash
python3 --version
# Deve mostrar Python 3.9 ou superior
```

### Passo 3: Transferir os Arquivos do Projeto

Você tem duas opções:

**Opção A: Clonar do repositório Git (se disponível)**

```bash
cd ~
git clone https://github.com/seu-usuario/trichogramma-pi.git
cd trichogramma-pi
```

**Opção B: Transferir via SCP/SFTP**

Do seu computador, transfira a pasta completa:

```bash
scp -r trichogramma-pi/ pi@<IP_DA_PI>:/home/pi/
```

Ou use um cliente SFTP como FileZilla/WinSCP.

### Passo 4: Instalar Dependências Python

Entre na pasta do projeto e instale as dependências:

```bash
cd ~/trichogramma-pi
pip3 install -r requirements.txt
```

**Nota**: Se encontrar erro com `pybluez`, você pode precisar instalar a partir do código-fonte:

```bash
pip3 install pybluez --break-system-packages
```

Ou use um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Passo 5: Configurar Permissões

Adicione o usuário `pi` aos grupos necessários:

```bash
sudo usermod -a -G bluetooth pi
sudo usermod -a -G gpio pi
```

**IMPORTANTE**: Faça logout e login novamente para aplicar as permissões:

```bash
exit
# Conecte-se novamente via SSH
```

Verifique se as permissões foram aplicadas:

```bash
groups
# Deve incluir: pi bluetooth gpio
```

### Passo 6: Habilitar Bluetooth no Boot

Certifique-se de que o Bluetooth está habilitado:

```bash
sudo systemctl enable bluetooth
sudo systemctl start bluetooth
```

Verifique o status:

```bash
sudo systemctl status bluetooth
# Deve mostrar "active (running)"
```

---

## ⚙️ Configuração Inicial

### 1. Configurar o Pino do Servo

Edite o arquivo `config.yaml` e ajuste o pino GPIO do seu servo:

```bash
nano ~/trichogramma-pi/config.yaml
```

Altere a linha `pwm_pin` para o pino que você conectou o sinal do servo (BCM numbering):

```yaml
servo:
  pwm_pin: 18  # ALTERE PARA O SEU PINO (ex: 12, 13, 18, 19)
  frequency: 50
  min_duty: 2.5
  max_duty: 12.5
```

**Conexões do Servo (exemplo)**:
- Vermelho (VCC) → Pino 2 (5V) ou fonte externa
- Preto/Marrom (GND) → Pino 6 (GND)
- Laranja/Amarelo (Sinal) → Pino GPIO configurado (ex: GPIO18 = Pino físico 12)

**IMPORTANTE**: Servos podem consumir muita corrente. Para aplicações com múltiplos servos ou cargas pesadas, use uma fonte de alimentação externa dedicada.

### 2. Parear Dispositivo Bluetooth

Antes de conectar o app, você precisa parear seu celular/tablet com a Raspberry Pi.

Entre no modo bluetoothctl:

```bash
sudo bluetoothctl
```

No prompt do bluetoothctl, execute:

```
power on
agent on
default-agent
discoverable on
pairable on
scan on
```

No seu celular/tablet:
1. Abra as configurações de Bluetooth
2. Procure por "raspberrypi" (ou o hostname da sua Pi)
3. Inicie o pareamento

Quando aparecer a solicitação no bluetoothctl:

```
# Anote o endereço MAC que aparecerá, exemplo: AA:BB:CC:DD:EE:FF
trust <MAC_DO_CELULAR>
pair <MAC_DO_CELULAR>
```

Confirme o código de pareamento no celular e no terminal.

Após parear:

```
exit
```

### 3. Testar em Foreground (Recomendado)

Antes de habilitar o serviço automático, teste se tudo funciona:

```bash
cd ~/trichogramma-pi/service
python3 main.py
```

Você deve ver:

```
Trichogramma Pi Service
============================================================
Dispositivo: Raspberry Pi Zero 2 W Rev 1.0
...
INFO: Servidor Bluetooth aguardando conexões na porta RFCOMM 1
INFO: Serviço 'TrichoPi' anunciado...
```

**Teste básico**:

Do seu celular, conecte ao serviço "TrichoPi" usando um app de terminal Bluetooth (como Serial Bluetooth Terminal) e envie:

```
PING
```

Deve receber:

```
PONG
```

Se funcionar, pressione `Ctrl+C` para parar o serviço.

---

## 🔄 Auto-Start no Boot (Systemd)

Para que o serviço inicie automaticamente toda vez que a Raspberry Pi ligar:

### 1. Copiar o Arquivo de Serviço

```bash
sudo cp ~/trichogramma-pi/systemd/trichogramma.service /etc/systemd/system/
```

### 2. Recarregar o Systemd

```bash
sudo systemctl daemon-reload
```

### 3. Habilitar o Serviço

```bash
sudo systemctl enable trichogramma.service
```

### 4. Iniciar o Serviço

```bash
sudo systemctl start trichogramma.service
```

### 5. Verificar o Status

```bash
sudo systemctl status trichogramma.service
```

Deve mostrar:

```
● trichogramma.service - Trichogramma Pi Bluetooth Service
     Loaded: loaded (/etc/systemd/system/trichogramma.service; enabled)
     Active: active (running) since ...
```

### 6. Ver Logs em Tempo Real

```bash
sudo journalctl -u trichogramma -f
```

Pressione `Ctrl+C` para sair da visualização de logs.

### 7. Testar o Auto-Start

Reinicie a Raspberry Pi:

```bash
sudo reboot
```

Após reiniciar, aguarde cerca de 30 segundos e verifique se o serviço subiu:

```bash
sudo systemctl status trichogramma
```

Conecte via Bluetooth do celular e teste os comandos!

### Comandos Úteis do Systemd

```bash
# Parar o serviço
sudo systemctl stop trichogramma

# Iniciar o serviço
sudo systemctl start trichogramma

# Reiniciar o serviço
sudo systemctl restart trichogramma

# Desabilitar auto-start
sudo systemctl disable trichogramma

# Ver logs (últimas 100 linhas)
sudo journalctl -u trichogramma -n 100

# Ver logs com follow (tempo real)
sudo journalctl -u trichogramma -f
```

---

## 📡 Comandos Suportados

Todos os comandos devem ser enviados como texto terminado com `\n` (newline).

| Comando | Descrição | Resposta |
|---------|-----------|----------|
| `PING` | Testa conectividade | `PONG` |
| `STATUS` | Retorna status do sistema | JSON: `{"gps":false,"bluetooth":"connected","servo_pin":18,...}` |
| `CALIBRAR` | Executa sweep de calibração (0° → 180° → 90°) | `CALIBRACAO_OK` |
| `SET_ANGLE:NN` | Move servo para ângulo NN (0-180) | `OK` ou `ERR:mensagem` |
| `GET_ANGLE` | Retorna ângulo atual do servo | `ANGLE:NN` |
| `STOP` | Para qualquer sweep em andamento | `STOPPED` |
| `SHUTDOWN` | Solicita desligamento (negado por segurança) | `DENIED` |
| `LIST` | Lista arquivos de voo salvos | `NO_FILES` (futuro) |

### Exemplos de Uso

```
> PING
< PONG

> STATUS
< {"gps":false,"bluetooth":"connected","servo_pin":18,"servo_angle":90,"servo_initialized":true}

> SET_ANGLE:45
< OK

> GET_ANGLE
< ANGLE:45

> CALIBRAR
< CALIBRACAO_OK

> STOP
< STOPPED
```

---

## 🔧 Troubleshooting

### Problema: "Permission denied" ao acessar GPIO

**Solução**: Certifique-se de que o usuário `pi` está no grupo `gpio`:

```bash
sudo usermod -a -G gpio pi
# Logout e login novamente
```

### Problema: Bluetooth não aparece ou não conecta

**Solução 1**: Verifique se o Bluetooth está ativo:

```bash
sudo systemctl status bluetooth
sudo hciconfig hci0 up
```

**Solução 2**: Torne a Pi detectável:

```bash
sudo bluetoothctl
power on
discoverable on
pairable on
```

### Problema: Servo não se move

**Checklist**:
1. Verifique se o pino está correto no `config.yaml` (BCM numbering)
2. Confirme as conexões físicas (VCC, GND, Sinal)
3. Teste se o servo funciona conectando-o diretamente a uma bateria (VCC/GND)
4. Verifique os logs: `sudo journalctl -u trichogramma -n 50`

### Problema: Erro "pybluez not found"

**Solução**: Instale manualmente:

```bash
pip3 install pybluez --break-system-packages
```

Ou use ambiente virtual:

```bash
python3 -m venv ~/trichogramma-pi/venv
source ~/trichogramma-pi/venv/bin/activate
pip install -r requirements.txt
```

Atualize o `ExecStart` no arquivo `.service` se usar venv:

```
ExecStart=/home/pi/trichogramma-pi/venv/bin/python3 /home/pi/trichogramma-pi/service/main.py
```

### Problema: Serviço não inicia automaticamente

**Solução**:

```bash
# Verifique se está habilitado
sudo systemctl is-enabled trichogramma

# Se não, habilite
sudo systemctl enable trichogramma

# Verifique erros nos logs
sudo journalctl -u trichogramma -n 100
```

### Logs do Sistema

Os logs são gravados em dois lugares:

1. **Arquivo**: `/var/log/trichogramma-service.log` (com rotação automática)
2. **Journald**: `sudo journalctl -u trichogramma`

Se não conseguir escrever em `/var/log`, o log será criado em `~/trichogramma-service.log`.

---

## 📁 Estrutura do Projeto

```
trichogramma-pi/
├── README.md                    # Este arquivo
├── requirements.txt             # Dependências Python
├── config.yaml                  # Configurações editáveis
├── service/                     # Código Python
│   ├── main.py                  # Loop principal
│   ├── bluetooth_server.py      # Servidor RFCOMM
│   ├── servo_control.py         # Controle PWM do servo
│   ├── logger.py                # Sistema de logging
│   └── utils.py                 # Funções auxiliares
├── systemd/                     # Configuração systemd
│   └── trichogramma.service     # Unit file
└── tests/                       # Testes e exemplos
    ├── manual_test_instructions.md
    └── client_console.py        # Cliente de teste
```

---

## 🔐 Segurança

- O comando `SHUTDOWN` é **negado** por padrão para evitar desligamentos remotos não autorizados
- O serviço roda com o usuário `pi` (não root)
- Recomenda-se parear apenas dispositivos confiáveis
- Para ambientes críticos, considere implementar autenticação adicional

---

## 🛠️ Desenvolvimento Futuro

Funcionalidades planejadas:

- Integração com GPS via UART (GPIO 14/15)
- Suporte para BLE (GATT) além do SPP (compatibilidade iOS)
- Endpoint HTTP local para diagnóstico
- Upload e gerenciamento de planos de voo
- Controle de múltiplos servos
- Interface web de configuração

---

## 📄 Licença

Este projeto faz parte do sistema Trichogramma para controle de drones agrícolas.

---

## 🆘 Suporte

Para problemas ou dúvidas:

1. Verifique os logs: `sudo journalctl -u trichogramma -f`
2. Revise a seção de Troubleshooting acima
3. Abra uma issue no repositório do projeto

---

**Desenvolvido para Raspberry Pi Zero 2 W - Sistema Trichogramma**

