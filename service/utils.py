#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Funções utilitárias para o Trichogramma Pi Service.
Validação de comandos, helpers e funções auxiliares.
"""

import os
import re
from typing import Tuple, Optional


def validate_angle(angle_str: str) -> Tuple[bool, Optional[float], str]:
    """
    Valida se uma string representa um ângulo válido (0-180).
    
    Args:
        angle_str: String contendo o ângulo
        
    Returns:
        Tupla (válido, ângulo_float, mensagem_erro)
    """
    try:
        angle = float(angle_str)
        
        if angle < 0 or angle > 180:
            return False, None, "Ângulo deve estar entre 0 e 180 graus"
        
        return True, angle, ""
        
    except ValueError:
        return False, None, "Ângulo inválido: deve ser um número"


def parse_set_angle_command(command: str) -> Tuple[bool, Optional[float], str]:
    """
    Faz parse do comando SET_ANGLE:NN.
    
    Args:
        command: Comando completo (ex: "SET_ANGLE:90")
        
    Returns:
        Tupla (válido, ângulo, mensagem_erro)
    """
    # Pattern: SET_ANGLE:número (com ou sem espaços)
    pattern = r'^SET_ANGLE\s*:\s*([0-9]+\.?[0-9]*)$'
    match = re.match(pattern, command, re.IGNORECASE)
    
    if not match:
        return False, None, "Formato inválido. Use: SET_ANGLE:NN (ex: SET_ANGLE:90)"
    
    angle_str = match.group(1)
    return validate_angle(angle_str)


def ensure_directory_exists(path: str) -> bool:
    """
    Garante que um diretório existe, criando-o se necessário.
    
    Args:
        path: Caminho do diretório
        
    Returns:
        True se o diretório existe ou foi criado, False caso contrário
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False


def ensure_file_writable(filepath: str) -> bool:
    """
    Verifica se é possível escrever em um arquivo.
    
    Args:
        filepath: Caminho completo do arquivo
        
    Returns:
        True se pode escrever, False caso contrário
    """
    directory = os.path.dirname(filepath)
    
    # Verifica se o diretório existe
    if not os.path.exists(directory):
        return ensure_directory_exists(directory)
    
    # Verifica se tem permissão de escrita no diretório
    return os.access(directory, os.W_OK)


def get_system_info() -> dict:
    """
    Retorna informações básicas do sistema.
    
    Returns:
        Dicionário com informações do sistema
    """
    info = {
        "platform": "unknown",
        "python_version": "unknown"
    }
    
    try:
        import platform
        import sys
        
        info["platform"] = platform.system()
        info["python_version"] = sys.version.split()[0]
        
        # Tenta detectar se está em Raspberry Pi
        if os.path.exists('/proc/device-tree/model'):
            try:
                with open('/proc/device-tree/model', 'r') as f:
                    model = f.read().strip()
                    info["device_model"] = model
            except:
                pass
                
    except Exception:
        pass
    
    return info


def format_json_response(data: dict) -> str:
    """
    Formata um dicionário como JSON compacto (uma linha).
    
    Args:
        data: Dicionário a ser formatado
        
    Returns:
        String JSON
    """
    import json
    return json.dumps(data, separators=(',', ':'))


def normalize_command(command: str) -> str:
    """
    Normaliza um comando: remove espaços extras e converte para uppercase.
    
    Args:
        command: Comando original
        
    Returns:
        Comando normalizado
    """
    return command.strip().upper()


def is_valid_command(command: str) -> bool:
    """
    Verifica se um comando é válido (não vazio e formato aceitável).
    
    Args:
        command: Comando a validar
        
    Returns:
        True se válido, False caso contrário
    """
    if not command or not command.strip():
        return False
    
    # Comandos válidos: letras, números, underscore, dois-pontos
    pattern = r'^[A-Z0-9_:\.]+$'
    return bool(re.match(pattern, normalize_command(command)))


def list_flight_files(directory: str = "/home/pi/flight_data") -> list:
    """
    Lista arquivos de voo salvos (placeholder para implementação futura).
    
    Args:
        directory: Diretório onde procurar arquivos
        
    Returns:
        Lista de nomes de arquivos
    """
    # TODO: Implementar quando houver funcionalidade de salvar planos de voo
    if not os.path.exists(directory):
        return []
    
    try:
        files = [f for f in os.listdir(directory) if f.endswith('.json') or f.endswith('.txt')]
        return sorted(files)
    except Exception:
        return []


def get_bluetooth_mac_address() -> Optional[str]:
    """
    Tenta obter o endereço MAC do adaptador Bluetooth.
    
    Returns:
        Endereço MAC ou None se não conseguir obter
    """
    try:
        # Tenta ler do sistema
        if os.path.exists('/sys/class/bluetooth/hci0/address'):
            with open('/sys/class/bluetooth/hci0/address', 'r') as f:
                return f.read().strip()
    except Exception:
        pass
    
    return None


def check_gpio_permissions() -> bool:
    """
    Verifica se o usuário tem permissões para acessar GPIO.
    
    Returns:
        True se tem permissão, False caso contrário
    """
    # Verifica se o usuário está no grupo gpio
    try:
        import grp
        gpio_group = grp.getgrnam('gpio')
        return os.getgid() in [gpio_group.gr_gid] or os.getuid() == 0
    except (KeyError, ImportError):
        # Se não conseguir verificar, assume que tem permissão
        return True


def check_bluetooth_permissions() -> bool:
    """
    Verifica se o usuário tem permissões para usar Bluetooth.
    
    Returns:
        True se tem permissão, False caso contrário
    """
    try:
        import grp
        bluetooth_group = grp.getgrnam('bluetooth')
        return os.getgid() in [bluetooth_group.gr_gid] or os.getuid() == 0
    except (KeyError, ImportError):
        return True

