# Instruções de Teste Manual - Trichogramma Pi Service

Este documento fornece instruções detalhadas para testar o serviço Trichogramma Pi manualmente antes de habilitá-lo como serviço systemd.

## 📋 Pré-requisitos

Antes de iniciar os testes, certifique-se de que:

- [x] Raspberry Pi OS Lite está instalado e atualizado
- [x] Dependências do sistema estão instaladas (`bluetooth`, `bluez`, `python3-pip`)
- [x] Dependências Python estão instaladas (`pip3 install -r requirements.txt`)
- [x] Usuário `pi` está nos grupos `bluetooth` e `gpio`
- [x] Arquivo `config.yaml` foi editado com o pino GPIO correto
- [x] Servo está conectado fisicamente (VCC, GND, Sinal)

---

## 🧪 Teste 1: Verificar Dependências

### 1.1 Python e Módulos

```bash
python3 --version
# Deve mostrar Python 3.9+

python3 -c "import RPi.GPIO; print('RPi.GPIO OK')"
python3 -c "import bluetooth; print('bluetooth OK')"
python3 -c "import yaml; print('yaml OK')"
```

Se algum módulo falhar, reinstale as dependências:

```bash
cd ~/trichogramma-pi
pip3 install -r requirements.txt
```

### 1.2 Bluetooth

```bash
sudo systemctl status bluetooth
# Deve mostrar "active (running)"

hciconfig hci0
# Deve mostrar o adaptador Bluetooth UP
```

### 1.3 GPIO

```bash
gpio readall
# Deve mostrar a tabela de pinos

groups
# Deve incluir: gpio, bluetooth
```

---

## 🧪 Teste 2: Configuração

### 2.1 Verificar config.yaml

```bash
cat ~/trichogramma-pi/config.yaml
```

Confirme:
- `pwm_pin` está correto (BCM numbering)
- Parâmetros de calibração fazem sentido
- Caminho do logfile está acessível

### 2.2 Testar Permissões de Log

```bash
# Tentar criar o arquivo de log
sudo touch /var/log/trichogramma-service.log
sudo chown pi:pi /var/log/trichogramma-service.log
ls -l /var/log/trichogramma-service.log
```

---

## 🧪 Teste 3: Executar em Foreground

Execute o serviço manualmente para ver os logs em tempo real:

```bash
cd ~/trichogramma-pi/service
python3 main.py
```

**Saída esperada:**

```
Trichogramma Pi Service
============================================================
Dispositivo: Raspberry Pi Zero 2 W Rev 1.0
INFO: Servo inicializado no pino GPIO 18 (BCM)
INFO: Servo movido para 90° (duty cycle: 7.50%)
INFO: Servidor Bluetooth inicializado: TrichoPi
INFO: Servidor Bluetooth aguardando conexões na porta RFCOMM 1
INFO: Serviço 'TrichoPi' anunciado com UUID 00001101-0000-1000-8000-00805F9B34FB
```

Se houver erros, anote-os e consulte a seção de Troubleshooting do README.

**Deixe o serviço rodando** e prossiga para os próximos testes.

---

## 🧪 Teste 4: Conectar via Bluetooth (Celular/App)

### 4.1 Parear o Dispositivo

Se ainda não pareou, faça o pareamento:

1. No celular, abra Configurações > Bluetooth
2. Procure por "raspberrypi" ou "TrichoPi"
3. Pareie o dispositivo

### 4.2 Conectar ao Serviço

Use um app de terminal Bluetooth:
- **Android**: Serial Bluetooth Terminal
- **iOS**: BLE Serial (se implementado BLE)

1. Abra o app
2. Conecte ao dispositivo "TrichoPi" ou "raspberrypi"
3. Você deve ver no terminal da Pi: `INFO: Cliente conectado: [endereço MAC]`

---

## 🧪 Teste 5: Comandos Básicos

Com o cliente Bluetooth conectado, teste cada comando:

### 5.1 PING

```
Envie: PING
Espera: PONG
```

**No terminal da Pi, você deve ver:**
```
INFO: Comando recebido: PING
INFO: Resposta enviada: PONG
```

✅ **Sucesso**: Comunicação Bluetooth funcionando

### 5.2 STATUS

```
Envie: STATUS
Espera: {"gps":false,"bluetooth":"connected","servo_pin":18,...}
```

**Verifique se o JSON contém:**
- `bluetooth: "connected"`
- `servo_pin: 18` (ou seu pino)
- `servo_initialized: true`

✅ **Sucesso**: Servidor retorna status corretamente

### 5.3 GET_ANGLE

```
Envie: GET_ANGLE
Espera: ANGLE:90
```

✅ **Sucesso**: Servo está na posição inicial (90°)

### 5.4 SET_ANGLE:45

```
Envie: SET_ANGLE:45
Espera: OK
```

**Observe fisicamente**: O servo deve se mover para aproximadamente 45°

**No terminal da Pi:**
```
INFO: Comando recebido: SET_ANGLE:45
INFO: Servo movido para 45° (duty cycle: ...)
INFO: Resposta enviada: OK
```

✅ **Sucesso**: Servo responde a comandos

### 5.5 SET_ANGLE:135

```
Envie: SET_ANGLE:135
Espera: OK
```

**Observe**: Servo deve mover para 135° (oposto do anterior)

### 5.6 GET_ANGLE (novamente)

```
Envie: GET_ANGLE
Espera: ANGLE:135
```

✅ **Sucesso**: Servo mantém controle de posição

---

## 🧪 Teste 6: Calibração

### 6.1 CALIBRAR

```
Envie: CALIBRAR
Espera: CALIBRACAO_OK (pode demorar alguns segundos)
```

**Observe fisicamente**: O servo deve fazer um sweep completo:
- 0° → 10° → 20° → ... → 180° → 90° (posição final)

**No terminal da Pi:**
```
INFO: Comando recebido: CALIBRAR
INFO: Parando sweep em andamento... (se houver)
INFO: Iniciando calibração: 0° -> 180°
INFO: Iniciando sweep de 0° até 180°
INFO: Servo movido para 0°
INFO: Servo movido para 10°
...
INFO: Sweep concluído
INFO: Servo movido para 90°
INFO: Calibração concluída
INFO: Resposta enviada: CALIBRACAO_OK
```

✅ **Sucesso**: Rotina de calibração funciona

---

## 🧪 Teste 7: Interromper Sweep

Se você quiser testar a interrupção de um sweep em andamento:

```
1. Envie: CALIBRAR
2. Enquanto o servo está se movendo, envie: STOP
3. Espera: STOPPED
```

**Observe**: O servo deve parar imediatamente onde está.

✅ **Sucesso**: Comando STOP funciona

---

## 🧪 Teste 8: Tratamento de Erros

### 8.1 Comando Inválido

```
Envie: COMANDO_ALEATORIO
Espera: ERR:UNKNOWN_COMMAND
```

### 8.2 Ângulo Fora do Range

```
Envie: SET_ANGLE:200
Espera: ERR:Ângulo deve estar entre 0 e 180 graus
```

### 8.3 Formato Inválido

```
Envie: SET_ANGLE:ABC
Espera: ERR:Ângulo inválido: deve ser um número
```

✅ **Sucesso**: Servidor valida comandos corretamente

---

## 🧪 Teste 9: Desconexão e Reconexão

1. Desconecte o cliente Bluetooth (feche o app ou desconecte manualmente)
2. No terminal da Pi, você deve ver: `INFO: Cliente desconectou`
3. Reconecte pelo app
4. Envie `PING` novamente
5. Espera: `PONG`

✅ **Sucesso**: Servidor aceita múltiplas conexões sequenciais

---

## 🧪 Teste 10: Parar o Serviço

No terminal da Pi, pressione `Ctrl+C`:

```
^C
INFO: Sinal 2 recebido. Encerrando serviço...
INFO: Encerrando serviço...
INFO: Servidor Bluetooth parado
INFO: Limpando recursos do servo...
INFO: GPIO limpo com sucesso
INFO: Serviço encerrado
```

✅ **Sucesso**: Shutdown gracioso funciona

---

## 🧪 Teste 11: Cliente Python (Opcional)

Use o cliente de teste Python incluído:

```bash
cd ~/trichogramma-pi/tests
python3 client_console.py
```

Digite comandos interativamente e veja as respostas.

---

## 🚀 Próximos Passos

Se todos os testes acima passaram com sucesso, você pode habilitar o serviço systemd:

### Instalar como Serviço

```bash
sudo cp ~/trichogramma-pi/systemd/trichogramma.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trichogramma
sudo systemctl start trichogramma
```

### Verificar Status

```bash
sudo systemctl status trichogramma
sudo journalctl -u trichogramma -f
```

### Testar Auto-Start

```bash
sudo reboot
```

Após reiniciar, conecte via Bluetooth e teste os comandos novamente.

---

## 📝 Checklist Final

Antes de considerar o serviço pronto para produção:

- [ ] Todos os comandos testados funcionam
- [ ] Servo responde corretamente aos comandos
- [ ] Calibração executa sweep completo
- [ ] Logs estão sendo gravados em `/var/log/trichogramma-service.log`
- [ ] Serviço systemd inicia automaticamente no boot
- [ ] Reconexões Bluetooth funcionam sem problemas
- [ ] Tratamento de erros funciona adequadamente
- [ ] Shutdown gracioso limpa recursos corretamente

---

## 🐛 Problemas Comuns

### Servo não move

- Verifique conexões físicas
- Confirme que `pwm_pin` no `config.yaml` está correto (BCM numbering)
- Teste com outro pino GPIO
- Use fonte de alimentação externa se o servo for potente

### Bluetooth não conecta

- Verifique se o dispositivo está pareado: `bluetoothctl paired-devices`
- Torne a Pi detectável: `sudo bluetoothctl` → `discoverable on`
- Reinicie o Bluetooth: `sudo systemctl restart bluetooth`

### Permissão negada

- Certifique-se de que o usuário está nos grupos corretos: `groups`
- Faça logout e login após adicionar aos grupos
- Use `sudo` apenas para testar permissões

---

**Testes completos! Serviço pronto para uso em produção.**

