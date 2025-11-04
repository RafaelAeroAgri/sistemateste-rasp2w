# 🔄 Atualizações do Sistema - Trichogramma Pi

## ✅ Alterações Realizadas

### 1. **GPIO 4 Configurado**
- ✅ `config.yaml` atualizado para usar **GPIO 4** (pino físico 7)
- ✅ Comentário adicionado indicando a configuração

### 2. **Script de Instalação Automatizada**
- ✅ Novo arquivo: `setup_from_git.sh`
- ✅ Instala tudo automaticamente a partir do Git
- ✅ Configura systemd para auto-start
- ✅ Ajusta usuário automaticamente (funciona com qualquer usuário, não só `pi`)

### 3. **Guia de Bluetooth para Tablet**
- ✅ Novo arquivo: `BLUETOOTH_TABLET_SETUP.md`
- ✅ Instruções detalhadas de pareamento
- ✅ Recomendações de apps para Android
- ✅ Troubleshooting específico para conexão Bluetooth
- ✅ Dicas de configuração do app Serial Bluetooth Terminal

### 4. **Guia de Instalação Rápida**
- ✅ Novo arquivo: `INSTALACAO_RAPIDA.md`
- ✅ Resumo de instalação em uma linha de comando
- ✅ Checklist pós-instalação
- ✅ Comandos essenciais

---

## 🚀 Como Usar (Instalação do Zero)

### Na Raspberry Pi Zero 2 W:

```bash
# 1. Instalar automaticamente (UMA LINHA!)
bash <(curl -sL https://raw.githubusercontent.com/RafaelAeroAgri/sistemateste-rasp2w/main/setup_from_git.sh)

# 2. Logout e login (aplicar permissões)
exit
ssh aeroagri@raspberrypi.local

# 3. Testar
cd ~/trichogramma-pi/service
python3 main.py

# 4. Parear tablet (ver BLUETOOTH_TABLET_SETUP.md)
# 5. Testar comandos via Bluetooth
# 6. Habilitar auto-start
sudo systemctl start trichogramma

# 7. Testar reboot
sudo reboot
```

---

## 📱 Conexão Bluetooth - Tablet Android

### App Recomendado:
**Serial Bluetooth Terminal**
- Play Store: https://play.google.com/store/apps/details?id=de.kai_morich.serial_bluetooth_terminal

### Pareamento:
1. Na Pi: `sudo bluetoothctl` → `discoverable on` → `pairable on`
2. No tablet: Configurações → Bluetooth → Parear "raspberrypi"
3. Na Pi: `trust [MAC]` → `pair [MAC]`
4. No app: Conectar ao "TrichoPi"
5. Enviar: `PING` → Receber: `PONG`

---

## 🔌 Conexões Físicas (GPIO 4)

```
Servo (3 fios):
├─ Vermelho (VCC)  → Pino 2 (5V) ou fonte externa
├─ Preto (GND)     → Pino 6 (GND)  
└─ Laranja (Sinal) → GPIO 4 (Pino físico 7) ✅ CONFIGURADO
```

---

## 📋 Comandos Bluetooth Disponíveis

| Comando | Ação | Resposta |
|---------|------|----------|
| `PING` | Teste de conexão | `PONG` |
| `STATUS` | Status do sistema | JSON |
| `SET_ANGLE:90` | Move para 90° | `OK` |
| `GET_ANGLE` | Ângulo atual | `ANGLE:90` |
| `CALIBRAR` | Calibração (0→180→90) | `CALIBRACAO_OK` |
| `STOP` | Para movimento | `STOPPED` |

---

## 📂 Arquivos Novos/Modificados

### Novos:
- ✅ `setup_from_git.sh` - Instalação automática do Git
- ✅ `BLUETOOTH_TABLET_SETUP.md` - Guia de conexão tablet
- ✅ `INSTALACAO_RAPIDA.md` - Guia rápido
- ✅ `ATUALIZACOES.md` - Este arquivo

### Modificados:
- ✅ `config.yaml` - GPIO 4 configurado

---

## 🔗 Repositório Git

**URL**: https://github.com/RafaelAeroAgri/sistemateste-rasp2w.git

**Usuário Raspberry Pi**: `aeroagri`

---

## ✅ Status

- ✅ Código pronto para uso
- ✅ GPIO 4 configurado
- ✅ Script de instalação automatizada criado
- ✅ Guias de conexão Bluetooth completos
- ✅ Documentação atualizada

---

## 📝 Próximos Passos Recomendados

1. **Fazer commit e push das alterações**:
```bash
git add .
git commit -m "Configura GPIO 4, adiciona instalação automática e guia Bluetooth tablet"
git push origin main
```

2. **Testar na Raspberry Pi**:
```bash
bash <(curl -sL https://raw.githubusercontent.com/RafaelAeroAgri/sistemateste-rasp2w/main/setup_from_git.sh)
```

3. **Conectar tablet via Bluetooth**

4. **Validar comandos**

---

**Desenvolvido por: Sistema Trichogramma**
**Data: Novembro 2025**

