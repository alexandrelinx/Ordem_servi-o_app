# app/utils/timezone.py
from datetime import datetime, timezone
import pytz

def agora_brasilia():
    brasilia = pytz.timezone('America/Sao_Paulo')
    return datetime.now(timezone.utc).astimezone(brasilia)