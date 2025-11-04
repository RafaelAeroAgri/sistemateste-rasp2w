#!/bin/bash
# Script de instalação automatizada do Trichogramma Pi Service
# Para Raspberry Pi Zero 2 W com Raspberry Pi OS Lite

set -e  # Para em caso de erro

echo "================================================================"
echo "Instalação do Trichogramma Pi Service"
echo "================================================================"
echo ""

# Verifica se está rodando como pi (não root)
if [ "$EUID" -eq 0 ]; then 
   echo "ERRO: Não execute este script como root (sudo)."
   echo "Execute como usuário pi: ./install.sh"
   exit 1
fi

# Verifica se está na Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "AVISO: Não parece ser uma Raspberry Pi. Continuando mesmo assim..."
else
    echo "Dispositivo: $(cat /proc/device-tree/model)"
fi

echo ""
echo "Este script irá:"
echo "  1. Atualizar o sistema (apt update/upgrade)"
echo "  2. Instalar dependências (bluetooth, bluez, python3-pip)"
echo "  3. Adicionar usuário aos grupos (bluetooth, gpio)"
echo "  4. Instalar pacotes Python"
echo "  5. Configurar permissões"
echo "  6. Configurar systemd (opcional)"
echo ""
read -p "Deseja continuar? [s/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    echo "Instalação cancelada."
    exit 0
fi

# 1. Atualizar sistema
echo ""
echo "[1/6] Atualizando sistema..."
sudo apt update
sudo apt upgrade -y

# 2. Instalar dependências
echo ""
echo "[2/6] Instalando dependências do sistema..."
sudo apt install -y python3-pip bluetooth bluez libbluetooth-dev git build-essential

# 3. Adicionar usuário aos grupos
echo ""
echo "[3/6] Adicionando usuário aos grupos necessários..."
sudo usermod -a -G bluetooth pi
sudo usermod -a -G gpio pi
echo "NOTA: Você precisará fazer logout e login para aplicar as permissões de grupo."

# 4. Instalar pacotes Python
echo ""
echo "[4/6] Instalando pacotes Python..."
cd "$(dirname "$0")"

# Instalar pybluez via apt (mais confiável no Raspberry Pi OS Bookworm+)
echo "Instalando pybluez via apt..."
sudo apt install -y python3-bluez python3-pybluez

# Instalar outros pacotes Python com --break-system-packages
echo "Instalando pacotes Python restantes..."
pip3 install --break-system-packages RPi.GPIO==0.7.1 PyYAML==6.0.1 psutil==5.9.5

# 5. Configurar permissões
echo ""
echo "[5/6] Configurando permissões..."

# Cria diretório de log se não existir
sudo mkdir -p /var/log
sudo touch /var/log/trichogramma-service.log
sudo chown pi:pi /var/log/trichogramma-service.log
sudo chmod 644 /var/log/trichogramma-service.log

# Garante que config.yaml existe
if [ ! -f config.yaml ]; then
    echo "ERRO: config.yaml não encontrado!"
    exit 1
fi

echo "Permissões configuradas."

# 6. Configurar systemd (opcional)
echo ""
echo "[6/6] Configuração do systemd..."
echo ""
read -p "Deseja instalar e habilitar o serviço systemd (auto-start no boot)? [s/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[SsYy]$ ]]; then
    echo "Instalando serviço systemd..."
    
    # Copia o arquivo de serviço
    sudo cp systemd/trichogramma.service /etc/systemd/system/
    
    # Recarrega systemd
    sudo systemctl daemon-reload
    
    # Habilita o serviço
    sudo systemctl enable trichogramma.service
    
    echo ""
    echo "Serviço instalado e habilitado para iniciar no boot."
    echo ""
    read -p "Deseja iniciar o serviço agora? [s/N] " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        sudo systemctl start trichogramma.service
        echo ""
        echo "Serviço iniciado!"
        echo ""
        echo "Ver status:"
        echo "  sudo systemctl status trichogramma"
        echo ""
        echo "Ver logs:"
        echo "  sudo journalctl -u trichogramma -f"
    else
        echo "Para iniciar manualmente:"
        echo "  sudo systemctl start trichogramma"
    fi
else
    echo "Serviço systemd não instalado."
    echo ""
    echo "Para instalar manualmente depois:"
    echo "  sudo cp systemd/trichogramma.service /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable --now trichogramma"
fi

# Finalização
echo ""
echo "================================================================"
echo "Instalação concluída!"
echo "================================================================"
echo ""
echo "PRÓXIMOS PASSOS:"
echo ""
echo "1. IMPORTANTE: Faça logout e login novamente para aplicar as permissões:"
echo "   exit"
echo ""
echo "2. Edite o arquivo config.yaml e configure o pino do servo:"
echo "   nano ~/trichogramma-pi/config.yaml"
echo ""
echo "3. Teste o serviço manualmente (recomendado):"
echo "   cd ~/trichogramma-pi/service"
echo "   python3 main.py"
echo ""
echo "4. Pareie seu dispositivo Bluetooth:"
echo "   sudo bluetoothctl"
echo "   > power on"
echo "   > agent on"
echo "   > default-agent"
echo "   > discoverable on"
echo "   > scan on"
echo "   (Pareie do celular e use 'trust' e 'pair')"
echo ""
echo "5. Se o serviço systemd foi instalado, verifique o status:"
echo "   sudo systemctl status trichogramma"
echo ""
echo "Documentação completa: README.md"
echo "Guia rápido: INSTALL_QUICK.md"
echo "Testes: tests/manual_test_instructions.md"
echo ""
echo "================================================================"

