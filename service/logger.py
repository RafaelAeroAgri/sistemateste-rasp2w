#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de logging centralizado para o Trichogramma Pi Service.
Fornece logging rotativo para arquivo e console simultaneamente.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


class TrichoLogger:
    """
    Classe para gerenciar o sistema de logging do serviço.
    Escreve logs tanto em arquivo quanto no console.
    """
    
    def __init__(self, logfile: str, level: str = "INFO", max_bytes: int = 10485760, backup_count: int = 5):
        """
        Inicializa o sistema de logging.
        
        Args:
            logfile: Caminho completo do arquivo de log
            level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Tamanho máximo do arquivo antes de rotacionar (padrão: 10MB)
            backup_count: Número de arquivos de backup a manter
        """
        self.logfile = logfile
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.logger = logging.getLogger("TrichogrammaService")
        self.logger.setLevel(self.level)
        
        # Remove handlers existentes para evitar duplicação
        self.logger.handlers.clear()
        
        # Formato detalhado dos logs
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para arquivo com rotação automática
        try:
            # Cria o diretório do log se não existir
            log_dir = os.path.dirname(logfile)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                logfile,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(self.level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
        except PermissionError:
            # Se não tiver permissão para escrever no arquivo principal,
            # tenta criar no diretório home do usuário
            fallback_logfile = os.path.expanduser("~/trichogramma-service.log")
            print(f"AVISO: Sem permissão para escrever em {logfile}. Usando {fallback_logfile}")
            
            file_handler = RotatingFileHandler(
                fallback_logfile,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(self.level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"ERRO ao criar arquivo de log: {e}")
        
        # Handler para console (stdout)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """
        Retorna o objeto logger configurado.
        
        Returns:
            Logger configurado
        """
        return self.logger
    
    def info(self, message: str):
        """Log de nível INFO"""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log de nível DEBUG"""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log de nível WARNING"""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info=False):
        """
        Log de nível ERROR
        
        Args:
            message: Mensagem de erro
            exc_info: Se True, inclui informações de exceção (stacktrace)
        """
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info=False):
        """
        Log de nível CRITICAL
        
        Args:
            message: Mensagem crítica
            exc_info: Se True, inclui informações de exceção (stacktrace)
        """
        self.logger.critical(message, exc_info=exc_info)


def create_logger(logfile: str, level: str = "INFO") -> TrichoLogger:
    """
    Função auxiliar para criar um logger rapidamente.
    
    Args:
        logfile: Caminho do arquivo de log
        level: Nível de logging
        
    Returns:
        Instância configurada de TrichoLogger
    """
    return TrichoLogger(logfile, level)

