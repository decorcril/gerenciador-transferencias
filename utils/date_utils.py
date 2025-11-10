# utils/date_utils.py
from datetime import datetime, timezone, timedelta

TIMEZONE_BRASILIA = timezone(timedelta(hours=-3))

def get_brasilia_time():
    """Retorna o horário atual de Brasília"""
    return datetime.now(TIMEZONE_BRASILIA)

def utc_to_brasilia(utc_dt):
    """Converte UTC para horário de Brasília"""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(TIMEZONE_BRASILIA)