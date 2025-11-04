#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trichogramma Pi Service - Serviço principal
Servidor Bluetooth RFCOMM para controle de servo via comandos de texto.

Autor: Sistema Trichogramma
Data: 2025
"""

import sys
import os
import signal
import yaml
import threading
import time

# Importa os módulos do serviço
from logger import create_logger
from servo_control import ServoControl
from bluetooth_server import BluetoothServer
from utils import (
    parse_set_angle_command,
    format_json_response,
    normalize_command,
    list_flight_files,
    get_bluetooth_mac_address
)


class TrichogrammaService:
    """
    Classe principal do serviço Trichogramma Pi.
    Gerencia o servidor Bluetooth e o controle do servo.
    """
    
    def __init__(self, config_path: str = "../config.yaml"):
        """
        Inicializa o serviço.
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config = None
        self.logger = None
        self.servo = None
        self.bt_server = None
        self.is_running = False
        self.config_path = config_path
        
        # Handler para sinais de sistema
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """
        Handler para sinais de sistema (SIGTERM, SIGINT).
        Realiza shutdown gracioso do serviço.
        """
        if self.logger:
            self.logger.info(f"Sinal {signum} recebido. Encerrando serviço...")
        else:
            print(f"Sinal {signum} recebido. Encerrando serviço...")
        
        self.shutdown()
        sys.exit(0)
    
    def load_config(self) -> bool:
        """
        Carrega o arquivo de configuração YAML.
        
        Returns:
            True se carregado com sucesso, False caso contrário
        """
        try:
            # Tenta encontrar o arquivo de configuração
            config_paths = [
                self.config_path,
                os.path.join(os.path.dirname(__file__), "..", "config.yaml"),
                "/etc/trichogramma/config.yaml",
                os.path.expanduser("~/trichogramma-pi/config.yaml")
            ]
            
            config_file = None
            for path in config_paths:
                if os.path.exists(path):
                    config_file = path
                    break
            
            if not config_file:
                print(f"ERRO: Arquivo de configuração não encontrado")
                print(f"Tentativas: {config_paths}")
                return False
            
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            
            print(f"Configuração carregada de: {config_file}")
            return True
            
        except Exception as e:
            print(f"ERRO ao carregar configuração: {e}")
            return False
    
    def initialize(self) -> bool:
        """
        Inicializa todos os componentes do serviço.
        
        Returns:
            True se inicializado com sucesso, False caso contrário
        """
        try:
            # Carrega configuração
            if not self.load_config():
                return False
            
            # Inicializa logger
            log_config = self.config.get('logging', {})
            logfile = log_config.get('logfile', '/var/log/trichogramma-service.log')
            log_level = log_config.get('level', 'INFO')
            
            self.logger = create_logger(logfile, log_level)
            self.logger.info("=" * 60)
            self.logger.info("Trichogramma Pi Service iniciando...")
            self.logger.info("=" * 60)
            
            # Exibe informações do sistema
            mac_address = get_bluetooth_mac_address()
            if mac_address:
                self.logger.info(f"Endereço MAC Bluetooth: {mac_address}")
            
            # Inicializa controle do servo
            servo_config = self.config.get('servo', {})
            pwm_pin = servo_config.get('pwm_pin', 18)
            frequency = servo_config.get('frequency', 50)
            min_duty = servo_config.get('min_duty', 2.5)
            max_duty = servo_config.get('max_duty', 12.5)
            
            self.logger.info(f"Inicializando servo no pino GPIO {pwm_pin} (BCM)")
            self.servo = ServoControl(
                pin=pwm_pin,
                frequency=frequency,
                min_duty=min_duty,
                max_duty=max_duty,
                logger=self.logger
            )
            
            if not self.servo.is_initialized:
                self.logger.warning("Servo não inicializado - modo seguro ativado")
            
            # Inicializa servidor Bluetooth
            bt_config = self.config.get('bluetooth', {})
            service_name = bt_config.get('service_name', 'TrichoPi')
            uuid = bt_config.get('uuid', '00001101-0000-1000-8000-00805F9B34FB')
            
            self.bt_server = BluetoothServer(
                service_name=service_name,
                uuid=uuid,
                logger=self.logger
            )
            
            # Define o callback de comandos
            self.bt_server.set_command_callback(self.process_command)
            
            self.logger.info("Serviço inicializado com sucesso")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.critical(f"Erro fatal ao inicializar: {e}", exc_info=True)
            else:
                print(f"ERRO FATAL: {e}")
            return False
    
    def process_command(self, command: str) -> str:
        """
        Processa um comando recebido via Bluetooth.
        
        Args:
            command: Comando recebido (string)
            
        Returns:
            Resposta a ser enviada ao cliente
        """
        # Normaliza o comando (uppercase, remove espaços)
        cmd = normalize_command(command)
        
        try:
            # Comando: PING
            if cmd == "PING":
                return "PONG"
            
            # Comando: STATUS
            elif cmd == "STATUS":
                status = {
                    "gps": False,  # Placeholder para futura implementação
                    "bluetooth": "connected",
                    "servo_pin": self.config['servo']['pwm_pin'],
                    "servo_angle": int(self.servo.get_angle()) if self.servo else 0,
                    "servo_initialized": self.servo.is_initialized if self.servo else False
                }
                return format_json_response(status)
            
            # Comando: CALIBRAR
            elif cmd == "CALIBRAR":
                if not self.servo or not self.servo.is_initialized:
                    return "ERR:SERVO_NOT_INITIALIZED"
                
                # Para qualquer sweep em andamento
                self.servo.stop_sweep()
                
                # Obtém parâmetros de calibração
                cal_config = self.config.get('calibration', {})
                from_angle = cal_config.get('sweep_angle_from', 0)
                to_angle = cal_config.get('sweep_angle_to', 180)
                delay_s = cal_config.get('sweep_delay_s', 0.5)
                
                self.logger.info(f"Iniciando calibração: {from_angle}° -> {to_angle}°")
                
                # Cria event para controle do sweep
                stop_event = threading.Event()
                
                # Inicia sweep (não bloqueante - em thread)
                self.servo.sweep(from_angle, to_angle, delay_s, step=10.0, stop_event=stop_event)
                
                # Aguarda a conclusão do sweep
                # (em uma thread para não bloquear o servidor)
                def wait_for_sweep():
                    while self.servo.is_sweeping():
                        time.sleep(0.1)
                    
                    # Após o sweep, volta para posição média
                    middle_angle = (from_angle + to_angle) / 2
                    self.servo.set_angle(middle_angle)
                    self.logger.info("Calibração concluída")
                
                # Executa em thread separada
                threading.Thread(target=wait_for_sweep, daemon=True).start()
                
                return "CALIBRACAO_OK"
            
            # Comando: SET_ANGLE:NN
            elif cmd.startswith("SET_ANGLE"):
                if not self.servo or not self.servo.is_initialized:
                    return "ERR:SERVO_NOT_INITIALIZED"
                
                # Parse do comando
                valid, angle, error_msg = parse_set_angle_command(cmd)
                
                if not valid:
                    return f"ERR:{error_msg}"
                
                # Move o servo
                success = self.servo.set_angle(angle)
                
                if success:
                    return "OK"
                else:
                    return "ERR:FAILED_TO_MOVE_SERVO"
            
            # Comando: GET_ANGLE
            elif cmd == "GET_ANGLE":
                if not self.servo:
                    return "ERR:SERVO_NOT_INITIALIZED"
                
                angle = int(self.servo.get_angle())
                return f"ANGLE:{angle}"
            
            # Comando: STOP
            elif cmd == "STOP":
                if not self.servo:
                    return "ERR:SERVO_NOT_INITIALIZED"
                
                self.servo.stop_sweep()
                return "STOPPED"
            
            # Comando: SHUTDOWN
            elif cmd == "SHUTDOWN":
                # Por segurança, não permite shutdown remoto
                self.logger.warning("Tentativa de shutdown remoto negada")
                return "DENIED"
            
            # Comando: LIST
            elif cmd == "LIST":
                # Placeholder para listagem de arquivos de voo
                files = list_flight_files()
                if files:
                    return "FILES:" + ",".join(files)
                else:
                    return "NO_FILES"
            
            # Comando desconhecido
            else:
                self.logger.warning(f"Comando desconhecido: {cmd}")
                return "ERR:UNKNOWN_COMMAND"
        
        except Exception as e:
            self.logger.error(f"Erro ao processar comando '{cmd}': {e}", exc_info=True)
            return "ERR:PROCESSING_ERROR"
    
    def run(self):
        """
        Executa o loop principal do serviço.
        """
        if not self.initialize():
            print("Falha na inicialização. Encerrando.")
            return
        
        self.is_running = True
        
        try:
            # Inicia o servidor Bluetooth em modo loop
            self.logger.info("Iniciando servidor Bluetooth...")
            self.bt_server.run_forever()
            
        except Exception as e:
            self.logger.critical(f"Erro no loop principal: {e}", exc_info=True)
            
        finally:
            self.shutdown()
    
    def shutdown(self):
        """
        Encerra o serviço de forma limpa.
        """
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.logger:
            self.logger.info("Encerrando serviço...")
        
        # Para o servidor Bluetooth
        if self.bt_server:
            self.bt_server.stop()
        
        # Libera recursos do servo
        if self.servo:
            self.servo.cleanup()
        
        if self.logger:
            self.logger.info("Serviço encerrado")
            self.logger.info("=" * 60)


def main():
    """
    Função principal de entrada do programa.
    """
    print("Trichogramma Pi Service")
    print("=" * 60)
    
    # Verifica se está rodando na Raspberry Pi
    try:
        if os.path.exists('/proc/device-tree/model'):
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read().strip()
                print(f"Dispositivo: {model}")
    except:
        pass
    
    # Cria e executa o serviço
    service = TrichogrammaService()
    service.run()


if __name__ == "__main__":
    main()

