"""
Configuração de logging estruturado para a aplicação.
Usa python-json-logger para logs em formato JSON.
"""
import logging
import sys
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Formatter customizado para adicionar campos extras aos logs."""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(
            log_record, record, message_dict
        )
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configura o sistema de logging da aplicação.
    
    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    # Remove handlers existentes para evitar duplicação
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Cria handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    
    # Configura formatter JSON
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(logger)s %(module)s '
        '%(function)s %(line)s %(message)s',
        timestamp=True
    )
    handler.setFormatter(formatter)
    
    # Configura root logger
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, level.upper()))
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Retorna um logger com o nome especificado.
    
    Args:
        name: Nome do logger (geralmente __name__ do módulo)
    
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


# Logger padrão da aplicação
app_logger = setup_logging("INFO")
