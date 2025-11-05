# 📡 Guia Completo: WiFi Hotspot vs WiFi Normal

## 🔄 Dois Modos de Operação

### **Modo 1: WiFi Cliente (Normal)**
- ✅ Pi conecta em rede WiFi existente
- ✅ Tem acesso à internet
- ✅ SSH via rede local (ex: `ssh aeroagri@192.168.1.8`)
- ❌ Não funciona em campo sem WiFi

### **Modo 2: WiFi Hotspot (Campo)**
- ✅ Pi cria rede WiFi própria ("TrichoPi")
- ✅ Funciona em qualquer lugar (campo, sem internet)
- ✅ Tablet conecta direto na Pi
- ✅ SSH via IP fixo (`ssh aeroagri@192.168.4.1`)
- ❌ Pi não tem internet
- ❌ Perde conexão com rede WiFi doméstica

---

## 🚀 ATIVAR MODO HOTSPOT (Para Campo)

**Execute na Raspberry Pi:**

```bash
cd ~/trichogramma-pi
chmod +x wifi_backup_and_hotspot.sh
sudo ./wifi_backup_and_hotspot.sh
```

O script irá:
1. ✅ **Fazer backup** de TODAS as configurações WiFi atuais
2. ✅ Configurar hotspot
3. ✅ **Criar script de reversão automática**
4. ✅ Perguntar se quer reiniciar

**Após reiniciar:**

### No Tablet:
1. Configurações → WiFi
2. Procure: **TrichoPi**
3. Senha: **tricho2025**
4. Conecte

### SSH (se precisar):
```bash
ssh aeroagri@192.168.4.1
```

### No App:
Abre automaticamente e conecta em `http://192.168.4.1:8080`

---

## 🔙 VOLTAR AO MODO WIFI NORMAL

**Quando voltar do campo**, conecte no WiFi TrichoPi e execute:

```bash
ssh aeroagri@192.168.4.1
cd ~/trichogramma-pi
./wifi_restore_normal.sh
```

Ou se tiver acesso físico:

```bash
# Conecte monitor e teclado (ou use Serial)
cd ~/trichogramma-pi
./wifi_restore_normal.sh
sudo reboot
```

Depois configure sua rede WiFi normalmente:

```bash
sudo raspi-config
# System Options → Wireless LAN
# Digite SSID e senha da sua rede
sudo reboot
```

**Pronto! Volta a funcionar como antes!** ✅

---

## 📂 Arquivos de Backup

O script cria backup em:
```
~/trichogramma-pi-backup-[DATA-HORA]/
├── dhcpcd.conf.backup
├── dnsmasq.conf.backup
├── hostapd.conf.backup
├── wpa_supplicant.conf.backup
└── wpa_supplicant.state
```

**NUNCA apague esses backups!** Use para recuperar se necessário.

---

## 🔧 Recuperação Manual (Se der Problema)

Se algo der errado e perder acesso:

### Opção 1: Via Monitor e Teclado

1. Conecte monitor HDMI e teclado USB
2. Faça login (usuário: aeroagri)
3. Execute:

```bash
cd ~/trichogramma-pi
./wifi_restore_normal.sh
sudo reboot
```

### Opção 2: Via Cartão SD

1. Desligue a Pi
2. Retire o cartão SD
3. Coloque no PC
4. Abra a partição `boot`
5. Delete ou renomeie: `dhcpcd.conf`
6. Coloque o cartão de volta
7. Ligue a Pi (voltará ao padrão)

### Opção 3: Restaurar Backup Manualmente

1. Acesse a Pi (monitor ou SSH via hotspot)
2. Execute:

```bash
# Encontrar backup mais recente
ls -lt ~ | grep trichogramma-pi-backup

# Restaurar (substitua DATA pela pasta do backup)
cd ~/trichogramma-pi-backup-DATA
sudo cp dhcpcd.conf.backup /etc/dhcpcd.conf
sudo cp wpa_supplicant.conf.backup /etc/wpa_supplicant/wpa_supplicant.conf

# Desabilitar hotspot
sudo systemctl disable hostapd
sudo systemctl disable dnsmasq
sudo systemctl enable wpa_supplicant

# Rebootar
sudo reboot
```

---

## 🧪 Testar Antes de Reiniciar

**Após executar o script** mas ANTES de reiniciar:

```bash
# Verificar se backup foi criado
ls -la ~/trichogramma-pi-backup*

# Verificar script de reversão
cat ~/trichogramma-pi/wifi_restore_normal.sh

# Verificar configurações
cat /etc/hostapd/hostapd.conf
```

Se tudo estiver OK, aí sim reinicie.

---

## 📋 Checklist Pré-Ativação

Antes de ativar o hotspot, certifique-se:

- [ ] Backup foi criado com sucesso
- [ ] Script `wifi_restore_normal.sh` existe
- [ ] Você tem acesso físico à Pi (monitor/teclado) em caso de emergência
- [ ] Você anotou a senha do hotspot: `tricho2025`
- [ ] Você sabe que o novo IP será `192.168.4.1`

---

## 🎯 Resumo dos Comandos

### Ativar Hotspot (Desenvolvimento → Campo)
```bash
cd ~/trichogramma-pi
sudo ./wifi_backup_and_hotspot.sh
# Aguarde backup → Confirme → Reinicia
```

### Voltar ao WiFi Normal (Campo → Desenvolvimento)
```bash
# Via SSH no hotspot (192.168.4.1) ou monitor físico
cd ~/trichogramma-pi
./wifi_restore_normal.sh
sudo reboot
```

### Acessar via SSH (Modo Hotspot)
```bash
# Conecte no WiFi TrichoPi primeiro
ssh aeroagri@192.168.4.1
```

### Acessar via SSH (Modo Normal)
```bash
# Use o IP da rede local
ssh aeroagri@192.168.1.X
# Ou
ssh aeroagri@raspberrypi.local
```

---

## ⚠️ AVISOS IMPORTANTES

1. **Modo Hotspot**: Pi NÃO terá internet
2. **Modo Hotspot**: SSH via `192.168.4.1` (não mais `.1.8`)
3. **Sempre faça backup** antes de alterar
4. **Mantenha os backups** - não apague!
5. **Teste o script de reversão** antes de ir para campo

---

## 💡 Fluxo Recomendado

### Desenvolvimento (Casa):
```
WiFi Normal → SSH via rede local → Desenvolve e testa
```

### Campo (Sem WiFi):
```
Ativa Hotspot → Tablet conecta → App funciona → Volta casa → Restaura WiFi Normal
```

---

## 🆘 Suporte de Emergência

Se ficar sem acesso:

1. **Monitor + Teclado** (opção mais segura)
2. **Cartão SD no PC** (editar configurações)
3. **Re-flash do SD** (última opção - perde tudo)

---

**Com esses scripts e guias, você tem controle total e segurança!** ✅

Execute `wifi_backup_and_hotspot.sh` quando estiver pronto.

