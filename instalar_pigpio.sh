#!/bin/bash
# Script para instalar e configurar pigpio na Raspberry Pi
# Resolve problema de jitter/flickering no servo

set -e

echo "=========================================="
echo "INSTALANDO PIGPIO - PWM VIA HARDWARE"
echo "=========================================="

# 1. Instalar pigpio via apt
echo ""
echo "1. Instalando pigpio e python3-pigpio..."
sudo apt update
sudo apt install -y pigpio python3-pigpio

# 2. Instalar pigpio via pip (biblioteca Python)
echo ""
echo "2. Instalando biblioteca Python pigpio..."
pip3 install --break-system-packages pigpio

# 3. Habilitar e iniciar daemon pigpiod
echo ""
echo "3. Habilitando e iniciando daemon pigpiod..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# 4. Verificar status
echo ""
echo "4. Verificando status do pigpiod..."
if sudo systemctl is-active --quiet pigpiod; then
    echo "✅ pigpiod está rodando!"
else
    echo "❌ pigpiod NÃO está rodando"
    echo "Tentando iniciar manualmente..."
    sudo pigpiod
    sleep 2
fi

# 5. Atualizar serviço HTTP para depender de pigpiod
echo ""
echo "5. Atualizando serviço trichogramma-http..."
sudo cp ~/trichogramma-pi/systemd/trichogramma-http.service /etc/systemd/system/
sudo systemctl daemon-reload

# 6. Reiniciar serviço HTTP
echo ""
echo "6. Reiniciando serviço HTTP..."
sudo systemctl restart trichogramma-http

# 7. Verificar status do serviço HTTP
echo ""
echo "7. Verificando status do serviço..."
sleep 2
sudo systemctl status trichogramma-http --no-pager -l

echo ""
echo "=========================================="
echo "✅ INSTALAÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "O servo agora usa PWM via hardware (pigpio)"
echo "Isso elimina o jitter/flickering!"
echo ""
echo "Teste fazendo uma requisição:"
echo "  curl http://10.3.141.1:8080/ping"
echo "  curl -X POST http://10.3.141.1:8080/angle -d '{\"angle\": 90}'"
echo ""

