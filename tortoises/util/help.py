
from datetime import datetime
import pytz


UTC = pytz.timezone('Asia/Shanghai')


def time():
    return datetime.now(tz=UTC).strftime('%Y-%m-%d %H:%M:%S %p')
