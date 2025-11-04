#!/bin/bash
# Script de instalação automatizada do Trichogramma Pi
# Baixa do Git e configura tudo para rodar na inicialização
# 
# Uso: bash <(curl -sL https://raw.githubusercontent.com/RafaelAeroAgri/sistemateste-rasp2w/main/setup_from_git.sh)

set -e  # Para em caso de erro

REPO_URL="https://github.com/RafaelAeroAgri/sistemateste-rasp2w.git"
INSTALL_DIR="$HOME/trichogramma-pi"

echo "================================================================"
echo "Instalação Automatizada - Trichogramma Pi Service"
echo "================================================================"
echo ""
echo "Este script irá:"
echo "  1. Atualizar o sistema"
echo "  2. Instalar dependências (Bluetooth, Python, etc)"
echo "  3. Baixar o código do Git"
echo "  4. Configurar permissões"
echo "  5. Instalar pacotes Python"
echo "  6. Configurar para iniciar automaticamente no boot"
echo ""

# Verifica se já existe instalação
if [ -d "$INSTALL_DIR" ]; then
    echo "⚠️  AVISO: Já existe uma instalação em $INSTALL_DIR"
    echo ""
    read -p "Deseja remover e reinstalar? [s/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        echo "Removendo instalação anterior..."
        rm -rf "$INSTALL_DIR"
    else
        echo "Instalação cancelada."
        exit 0
    fi
fi

echo ""
echo "=========================================="
echo "PASSO 1/7: Atualizando sistema"
echo "=========================================="
sudo apt update
echo "✓ Sistema atualizado"

echo ""
echo "=========================================="
echo "PASSO 2/7: Instalando dependências"
echo "=========================================="
sudo apt install -y python3-pip bluetooth bluez libbluetooth-dev git build-essential
echo "✓ Dependências instaladas"

echo ""
echo "=========================================="
echo "PASSO 3/7: Baixando código do Git"
echo "=========================================="
cd "$HOME"
git clone "$REPO_URL" trichogramma-pi
cd trichogramma-pi
echo "✓ Código baixado de: $REPO_URL"

echo ""
echo "=========================================="
echo "PASSO 4/7: Configurando permissões"
echo "=========================================="
# Adiciona usuário aos grupos necessários
sudo usermod -a -G bluetooth $USER
sudo usermod -a -G gpio $USER

# Cria diretório de log
sudo mkdir -p /var/log
sudo touch /var/log/trichogramma-service.log
sudo chown $USER:$USER /var/log/trichogramma-service.log
sudo chmod 644 /var/log/trichogramma-service.log

# Torna o install.sh executável
chmod +x install.sh

echo "✓ Permissões configuradas"
echo ""
echo "⚠️  IMPORTANTE: Você precisará fazer LOGOUT e LOGIN novamente"
echo "   para aplicar as permissões de grupo (bluetooth e gpio)."
echo ""

echo ""
echo "=========================================="
echo "PASSO 5/7: Instalando pacotes Python"
echo "=========================================="

# Instalar pybluez via apt (mais confiável no Raspberry Pi OS)
echo "Instalando pybluez via apt..."
sudo apt install -y python3-bluez python3-pybluez

# Instalar outros pacotes Python
echo "Instalando pacotes Python restantes..."
pip3 install --break-system-packages RPi.GPIO==0.7.1 PyYAML==6.0.1 psutil==5.9.5

echo "✓ Pacotes Python instalados"

echo ""
echo "=========================================="
echo "PASSO 6/7: Configurando systemd"
echo "=========================================="
# Atualiza o arquivo de serviço com o usuário correto
sed -i "s/User=pi/User=$USER/g" systemd/trichogramma.service
sed -i "s/Group=pi/Group=$USER/g" systemd/trichogramma.service
sed -i "s|/home/pi/trichogramma-pi|$INSTALL_DIR|g" systemd/trichogramma.service

# Copia e habilita o serviço
sudo cp systemd/trichogramma.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trichogramma.service

echo "✓ Serviço systemd configurado"

echo ""
echo "=========================================="
echo "PASSO 7/7: Configurando Bluetooth"
echo "=========================================="
# Garante que o Bluetooth está habilitado
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Configura o Bluetooth para ser descoberto
sudo hciconfig hci0 piscan

echo "✓ Bluetooth configurado e ativo"

echo ""
echo "================================================================"
echo "✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "================================================================"
echo ""
echo "📋 PRÓXIMOS PASSOS IMPORTANTES:"
echo ""
echo "1. ⚠️  FAÇA LOGOUT E LOGIN NOVAMENTE (obrigatório):"
echo "   exit"
echo "   # Reconecte via SSH"
echo ""
echo "2. 🔧 Verifique se o servo está conectado no GPIO 4:"
echo "   - Vermelho (VCC)  → Pino 2 (5V)"
echo "   - Preto (GND)     → Pino 6 (GND)"
echo "   - Sinal           → GPIO 4 (Pino físico 7)"
echo ""
echo "3. 📱 PAREAR SEU TABLET:"
echo "   sudo bluetoothctl"
echo "   > power on"
echo "   > agent on"
echo "   > default-agent"
echo "   > discoverable on"
echo "   > pairable on"
echo "   > scan on"
echo "   # No tablet, vá em Configurações > Bluetooth e pareie 'raspberrypi'"
echo "   # Quando aparecer o MAC do tablet, anote e execute:"
echo "   > trust [MAC_DO_TABLET]"
echo "   > pair [MAC_DO_TABLET]"
echo "   > exit"
echo ""
echo "4. 🧪 TESTAR MANUALMENTE (após logout/login):"
echo "   cd ~/trichogramma-pi/service"
echo "   python3 main.py"
echo "   # Deve aparecer: 'Servidor Bluetooth aguardando conexões...'"
echo "   # Conecte do tablet e envie: PING"
echo "   # Pressione Ctrl+C para parar"
echo ""
echo "5. 🚀 INICIAR O SERVIÇO:"
echo "   sudo systemctl start trichogramma"
echo ""
echo "6. ✅ VERIFICAR STATUS:"
echo "   sudo systemctl status trichogramma"
echo ""
echo "7. 📊 VER LOGS:"
echo "   sudo journalctl -u trichogramma -f"
echo ""
echo "8. 🔄 TESTAR AUTO-START:"
echo "   sudo reboot"
echo "   # Aguarde 30s e conecte via Bluetooth do tablet!"
echo ""
echo "================================================================"
echo "📦 Instalação em: $INSTALL_DIR"
echo "🔗 Repositório: $REPO_URL"
echo "📖 Documentação: $INSTALL_DIR/README.md"
echo "================================================================"
echo ""
echo "🎉 Pronto! Siga os próximos passos acima para concluir."

