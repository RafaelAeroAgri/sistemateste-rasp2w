# 🔧 Atualização: Usar pigpio para Servo (Elimina Jitter)

## ⚠️ PROBLEMA
O servo estava com **jitter/flickering** (tremendo/oscilando) porque o `RPi.GPIO` usa PWM via software, que não é estável.

## ✅ SOLUÇÃO
Mudamos para **`pigpio`**, que usa **PWM via hardware**, muito mais estável e sem jitter.

---

## 📋 O QUE FOI ALTERADO

### **Arquivos modificados:**

1. **`service/servo_control.py`**
   - Trocado `RPi.GPIO` por `pigpio`
   - Usa `set_servo_pulsewidth()` ao invés de `ChangeDutyCycle()`
   - PWM via hardware = sem jitter

2. **`requirements.txt`**
   - Removido `RPi.GPIO==0.7.1`
   - Adicionado `pigpio`

3. **`systemd/trichogramma-http.service`**
   - Adicionado `Requires=pigpiod.service`
   - Garante que `pigpiod` daemon está rodando

---

## 🚀 COMO ATUALIZAR NA RASPBERRY PI

**Execute estes comandos NA RASPBERRY PI:**

```bash
# 1. Ir para o diretório do projeto
cd ~/trichogramma-pi

# 2. Atualizar código do Git (se necessário)
git pull

# 3. Instalar pigpio
sudo apt update
sudo apt install -y pigpio python3-pigpio

# 4. Instalar biblioteca Python
pip3 install --break-system-packages pigpio

# 5. Habilitar e iniciar daemon pigpiod
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# 6. Verificar se pigpiod está rodando
sudo systemctl status pigpiod

# 7. Atualizar serviço HTTP
sudo cp systemd/trichogramma-http.service /etc/systemd/system/
sudo systemctl daemon-reload

# 8. Reiniciar serviço HTTP
sudo systemctl restart trichogramma-http

# 9. Verificar status
sudo systemctl status trichogramma-http
```

---

## 🎯 OU USE O SCRIPT AUTOMÁTICO

```bash
cd ~/trichogramma-pi
chmod +x instalar_pigpio.sh
./instalar_pigpio.sh
```

---

## ✅ BENEFÍCIOS

1. **Sem jitter/flickering** - PWM via hardware é extremamente estável
2. **Mais preciso** - Controle fino de pulsewidth (microsegundos)
3. **Menos carga CPU** - Hardware faz o trabalho
4. **Mais confiável** - Não depende de timing do kernel

---

## 🧪 TESTAR

```bash
# 1. Verificar se pigpiod está rodando
sudo systemctl status pigpiod

# 2. Testar servo via HTTP
curl http://10.3.141.1:8080/ping

# 3. Mover servo para 90°
curl -X POST http://10.3.141.1:8080/angle -H "Content-Type: application/json" -d '{"angle": 90}'

# 4. Mover servo para 0°
curl -X POST http://10.3.141.1:8080/angle -H "Content-Type: application/json" -d '{"angle": 0}'

# 5. Mover servo para 180°
curl -X POST http://10.3.141.1:8080/angle -H "Content-Type: application/json" -d '{"angle": 180}'

# 6. Ver logs
sudo journalctl -u trichogramma-http -f
```

O servo deve se mover **suavemente, sem tremer ou oscilar**.

---

## 🐛 SOLUÇÃO DE PROBLEMAS

### pigpiod não inicia

```bash
# Iniciar manualmente
sudo pigpiod

# Verificar se está rodando
ps aux | grep pigpiod
```

### Erro "pigpio não disponível"

```bash
# Reinstalar
sudo apt install --reinstall pigpio python3-pigpio
pip3 install --break-system-packages --force-reinstall pigpio
```

### Erro "Não foi possível conectar ao pigpiod"

```bash
# Verificar se o daemon está rodando
sudo systemctl status pigpiod

# Se não estiver, iniciar
sudo systemctl start pigpiod

# Verificar porta (padrão: 8888)
sudo netstat -tulpn | grep pigpiod
```

---

## 📊 COMPARAÇÃO

| Característica | RPi.GPIO (antes) | pigpio (agora) |
|---------------|------------------|----------------|
| Tipo PWM | Software | **Hardware** |
| Jitter | ❌ Alto | ✅ Nenhum |
| Precisão | ~100us | ✅ ~5us |
| Carga CPU | Alta | ✅ Baixa |
| Estabilidade | Variável | ✅ Excelente |

---

## ✅ RESULTADO ESPERADO

Após a atualização:
- ✅ Servo se move **suavemente** sem tremor
- ✅ Posições são **precisas** e **estáveis**
- ✅ Não há **oscilação** ou **flickering**
- ✅ Sistema roda automaticamente no boot

