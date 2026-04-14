import requests
import xml.etree.ElementTree as ET
import os
from datetime import datetime
import pytz

# 1. 설정
SERVICE_KEY = os.environ.get('BUS_API_KEY')
BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
CHAT_ID = os.environ.get('TG_CHAT_ID')

def get_bus_arrival():
    # v2 주소 및 중복 인코딩 방지 처리
    url = f"http://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalItem?serviceKey={SERVICE_KEY}"
    params = {'stationId': '218000624', 'routeId': '100100107'}
    try:
        response = requests.get(url, params=params, timeout=10)
        root = ET.fromstring(response.content)
        predict_time = root.find(".//predictTime1")
        return int(predict_time.text) if predict_time is not None else None
    except:
        return None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': message})

if __name__ == "__main__":
    # 한국 시간 설정
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(seoul_tz)
    
    # 평일(월-금) 아침 7시 ~ 8시 사이일 때만 실행
    if now.weekday() < 5 and 7 <= now.hour < 8:
        remaining = get_bus_arrival()
        if remaining is not None and remaining <= 10:
            send_telegram(f"🚌 [705번] {remaining}분 뒤 도착! 얼른 나가세요!")
