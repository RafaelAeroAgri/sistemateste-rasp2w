# 🚀 Instalação RaspAP - Solução Profissional WiFi

RaspAP é uma interface web profissional para gerenciar WiFi na Raspberry Pi. Permite alternar entre modo Cliente e Hotspot facilmente!

---

## ⚡ Instalação Rápida (10 minutos)

**Na Raspberry Pi (via SSH):**

```bash
# 1. Atualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Configurar iptables para modo legacy
sudo apt install iptables -y
sudo update-alternatives --set iptables /usr/sbin/iptables-legacy
sudo update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy

# 3. Instalar RaspAP (instalador automático)
curl -sL https://install.raspap.com | bash
```

**Durante a instalação, responda:**
- `Yes` para todas as perguntas
- `Yes` para instalar Ad Blocking (opcional)
- `Yes` para instalar OpenVPN (opcional - pode pular)
- `Yes` para reboot no final

**Aguarde instalação** (~5-10 minutos)

---

## 🌐 Acessar Interface Web

Após instalação e reboot:

### **Modo 1: Via Rede WiFi Atual (Cliente)**

1. Conecte SSH: `ssh aeroagri@raspberrypi.local`
2. Veja o IP: `hostname -I`
3. No navegador: `http://[IP_DA_PI]`

**Login padrão:**
- Usuário: `admin`
- Senha: `secret`

### **Modo 2: Via Hotspot (raspap-webgui)**

Se já mudou para hotspot:

1. Tablet → WiFi → Conecte em **"raspi-webgui"**
2. Senha padrão: **"ChangeMe"**
3. Navegador: `http://10.3.141.1`
4. Login: `admin` / `secret`

---

## ⚙️ Configurar Hotspot Personalizado

**Na interface web do RaspAP:**

1. **Hotspot** → Basic
   - SSID: `TrichoPi`
   - Senha: `tricho2025`
   - Channel: `6`
   - Salvar

2. **DHCP Server**
   - Range: `192.168.4.2 - 192.168.4.20`
   - Gateway: `192.168.4.1`
   - Salvar

3. **System** → Reboot

---

## 🔄 Alternar Entre Modos (Interface Web)

### **Cliente → Hotspot (Para Campo)**

1. Acesse interface: `http://[IP]:80`
2. **Hotspot** → `Start Hotspot`
3. Pronto! WiFi "TrichoPi" criado

### **Hotspot → Cliente (Voltar Casa)**

1. Conecte no hotspot TrichoPi
2. Acesse: `http://192.168.4.1`
3. **Hotspot** → `Stop Hotspot`
4. **WiFi Client** → Selecione sua rede → Conecte
5. Pronto! Volta ao WiFi normal

**Tudo via interface web! Sem comandos!** ✨

---

## 🔧 Instalar Serviço HTTP do Trichogramma

**Após instalar RaspAP:**

```bash
ssh aeroagri@raspberrypi.local

cd ~/trichogramma-pi

# Copiar serviço HTTP
sudo cp systemd/trichogramma-http.service /etc/systemd/system/

# Habilitar
sudo systemctl daemon-reload
sudo systemctl enable trichogramma-http
sudo systemctl start trichogramma-http

# Verificar
sudo systemctl status trichogramma-http
```

---

## 📱 Configurar App Flutter

O app já está configurado para `http://192.168.4.1:8080`

**Quando em modo hotspot:**
1. Conecte no WiFi "TrichoPi"
2. Abra o app
3. Conecta automaticamente!

**Quando em modo cliente:**
- App não conecta (precisa descobrir IP dinamicamente)
- OU configure IP fixo no RaspAP

---

## 🎯 IP Fixo no Modo Cliente (Recomendado)

Para o app sempre encontrar a Pi em qualquer modo:

**Na interface RaspAP:**

1. **DHCP Server** → Advanced
2. **Static IP Leases**
3. Adicione IP fixo: `192.168.4.1` (mesmo em modo cliente)
4. Salvar

OU configure router para sempre dar o mesmo IP para a Pi.

---

## 📊 Vantagens do RaspAP

- ✅ **Interface web intuitiva**
- ✅ **Alterna modos sem SSH**
- ✅ **Configuração visual**
- ✅ **Logs e monitoramento**
- ✅ **Firewall integrado**
- ✅ **VPN suporte**
- ✅ **Ad blocking**

---

## 🐛 Se Algo Der Errado

### Não consegue acessar interface web

```bash
# Reiniciar serviços RaspAP
sudo systemctl restart lighttpd
sudo systemctl restart hostapd
sudo systemctl restart dnsmasq
```

### Esqueceu senha da interface

```bash
# Resetar senha
sudo raspi-config
# System Options → Password
```

### Hotspot não aparece

```bash
# Forçar hotspot via CLI
sudo systemctl start hostapd
```

---

## 📖 Documentação Oficial

- Site: https://raspap.com
- Docs: https://docs.raspap.com
- GitHub: https://github.com/RaspAP/raspap-webgui

---

## 🎉 Próximos Passos

1. ✅ **Instale RaspAP**: `curl -sL https://install.raspap.com | bash`
2. ✅ **Configure hotspot**: Interface web
3. ✅ **Instale serviço HTTP**: `systemctl enable trichogramma-http`
4. ✅ **Teste app Flutter**: Conecta e controla servo

---

**Agora execute a instalação do RaspAP!** Muito mais profissional e fácil de usar! 🚀

```bash
curl -sL https://install.raspap.com | bash
```
