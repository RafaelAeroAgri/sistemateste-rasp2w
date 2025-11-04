#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Bluetooth RFCOMM/SPP (Serial Port Profile) para comunicação com o app.
Aguarda conexões de clientes e processa comandos linha por linha.
"""

import socket
from typing import Callable, Optional

try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False
    print("AVISO: PyBluez não disponível. Modo simulação ativado.")


class BluetoothServer:
    """
    Servidor RFCOMM que aceita conexões Bluetooth e processa comandos.
    """
    
    def __init__(self, service_name: str, uuid: str, logger=None):
        """
        Inicializa o servidor Bluetooth.
        
        Args:
            service_name: Nome do serviço Bluetooth
            uuid: UUID do serviço (SPP padrão: 00001101-0000-1000-8000-00805F9B34FB)
            logger: Instância do logger (opcional)
        """
        self.service_name = service_name
        self.uuid = uuid
        self.logger = logger
        self.server_sock = None
        self.client_sock = None
        self.client_address = None
        self.is_running = False
        self.command_callback = None
        
        self._log_info(f"Servidor Bluetooth inicializado: {service_name}")
    
    def _log_info(self, message: str):
        """Helper para log de info"""
        if self.logger:
            self.logger.info(message)
        else:
            print(f"INFO: {message}")
    
    def _log_warning(self, message: str):
        """Helper para log de warning"""
        if self.logger:
            self.logger.warning(message)
        else:
            print(f"WARNING: {message}")
    
    def _log_error(self, message: str, exc_info=False):
        """Helper para log de erro"""
        if self.logger:
            self.logger.error(message, exc_info=exc_info)
        else:
            print(f"ERROR: {message}")
    
    def start(self) -> bool:
        """
        Inicia o servidor Bluetooth RFCOMM.
        
        Returns:
            True se iniciado com sucesso, False caso contrário
        """
        if not BLUETOOTH_AVAILABLE:
            self._log_error("PyBluez não disponível. Não é possível iniciar servidor Bluetooth.")
            return False
        
        try:
            # Cria socket Bluetooth RFCOMM
            self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            
            # Bind em qualquer porta disponível (PORT_ANY)
            self.server_sock.bind(("", bluetooth.PORT_ANY))
            
            # Escuta por conexões
            self.server_sock.listen(1)
            
            # Obtém a porta alocada
            port = self.server_sock.getsockname()[1]
            
            # Anuncia o serviço via SDP (Service Discovery Protocol)
            bluetooth.advertise_service(
                self.server_sock,
                self.service_name,
                service_id=self.uuid,
                service_classes=[self.uuid, bluetooth.SERIAL_PORT_CLASS],
                profiles=[bluetooth.SERIAL_PORT_PROFILE]
            )
            
            self.is_running = True
            self._log_info(f"Servidor Bluetooth aguardando conexões na porta RFCOMM {port}")
            self._log_info(f"Serviço '{self.service_name}' anunciado com UUID {self.uuid}")
            
            return True
            
        except Exception as e:
            self._log_error(f"Erro ao iniciar servidor Bluetooth: {e}", exc_info=True)
            return False
    
    def set_command_callback(self, callback: Callable[[str], str]):
        """
        Define a função callback que será chamada para processar cada comando.
        
        Args:
            callback: Função que recebe um comando (string) e retorna uma resposta (string)
        """
        self.command_callback = callback
    
    def accept_connection(self) -> bool:
        """
        Aguarda e aceita uma conexão de cliente.
        Bloqueia até receber uma conexão.
        
        Returns:
            True se conexão aceita com sucesso, False caso contrário
        """
        if not self.is_running or not self.server_sock:
            self._log_error("Servidor não está rodando")
            return False
        
        try:
            self._log_info("Aguardando conexão de cliente...")
            
            # Aceita conexão (bloqueante)
            self.client_sock, self.client_address = self.server_sock.accept()
            
            self._log_info(f"Cliente conectado: {self.client_address}")
            
            return True
            
        except Exception as e:
            self._log_error(f"Erro ao aceitar conexão: {e}", exc_info=True)
            return False
    
    def handle_client(self):
        """
        Processa comandos do cliente conectado.
        Lê comandos linha por linha e chama o callback para processar.
        """
        if not self.client_sock:
            self._log_error("Nenhum cliente conectado")
            return
        
        buffer = ""
        
        try:
            while True:
                # Recebe dados do cliente (até 1024 bytes por vez)
                data = self.client_sock.recv(1024)
                
                if not data:
                    # Cliente desconectou
                    self._log_info("Cliente desconectou")
                    break
                
                # Decodifica os dados recebidos
                try:
                    received = data.decode('utf-8')
                    buffer += received
                    
                    # Processa todas as linhas completas no buffer
                    while '\n' in buffer:
                        # Extrai a primeira linha
                        line, buffer = buffer.split('\n', 1)
                        
                        # Remove espaços em branco e \r se houver
                        command = line.strip()
                        
                        if command:
                            self._log_info(f"Comando recebido: {command}")
                            
                            # Processa o comando via callback
                            if self.command_callback:
                                try:
                                    response = self.command_callback(command)
                                    
                                    # Envia a resposta de volta ao cliente
                                    if response:
                                        # Garante que a resposta termina com \n
                                        if not response.endswith('\n'):
                                            response += '\n'
                                        
                                        self.client_sock.send(response.encode('utf-8'))
                                        self._log_info(f"Resposta enviada: {response.strip()}")
                                        
                                except Exception as e:
                                    self._log_error(f"Erro ao processar comando '{command}': {e}", exc_info=True)
                                    error_response = f"ERR:INTERNAL_ERROR\n"
                                    self.client_sock.send(error_response.encode('utf-8'))
                            else:
                                self._log_warning("Nenhum callback de comando definido")
                
                except UnicodeDecodeError as e:
                    self._log_error(f"Erro ao decodificar dados: {e}")
                    # Limpa o buffer em caso de erro de decodificação
                    buffer = ""
                    
        except OSError as e:
            # Erro de socket (cliente desconectou abruptamente)
            self._log_info(f"Conexão perdida: {e}")
            
        except Exception as e:
            self._log_error(f"Erro ao processar cliente: {e}", exc_info=True)
            
        finally:
            # Fecha a conexão com o cliente
            self.close_client()
    
    def close_client(self):
        """
        Fecha a conexão com o cliente atual.
        """
        if self.client_sock:
            try:
                self.client_sock.close()
                self._log_info("Conexão com cliente fechada")
            except Exception as e:
                self._log_error(f"Erro ao fechar conexão com cliente: {e}")
            finally:
                self.client_sock = None
                self.client_address = None
    
    def run_forever(self):
        """
        Loop principal: aceita conexões e processa clientes indefinidamente.
        """
        if not self.start():
            self._log_error("Falha ao iniciar servidor")
            return
        
        self._log_info("Servidor em modo loop. Aguardando conexões...")
        
        try:
            while self.is_running:
                # Aguarda e aceita conexão
                if self.accept_connection():
                    # Processa o cliente
                    self.handle_client()
                    
                    # Cliente desconectou, volta a aguardar nova conexão
                    self._log_info("Pronto para nova conexão")
                    
        except KeyboardInterrupt:
            self._log_info("Servidor interrompido por Ctrl+C")
            
        finally:
            self.stop()
    
    def stop(self):
        """
        Para o servidor e fecha todas as conexões.
        """
        self._log_info("Parando servidor Bluetooth...")
        
        self.is_running = False
        
        # Fecha conexão com cliente se houver
        self.close_client()
        
        # Fecha o socket do servidor
        if self.server_sock:
            try:
                self.server_sock.close()
                self._log_info("Servidor Bluetooth parado")
            except Exception as e:
                self._log_error(f"Erro ao fechar servidor: {e}")
            finally:
                self.server_sock = None
    
    def __del__(self):
        """Destrutor: garante limpeza dos recursos"""
        self.stop()

