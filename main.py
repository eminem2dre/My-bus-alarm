import requests
import xml.etree.ElementTree as ET
import os
from datetime import datetime
import pytz

# 1. 설정값 불러오기
SERVICE_KEY = os.environ.get('BUS_API_KEY')
BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
CHAT_ID = os.environ.get('TG_CHAT_ID')

STATION_ID = '218000624'
ROUTE_ID = '100100107'

def get_bus_arrival():
    # v2 주소 사용 및 인증키 강제 주입 (중복 인코딩 방지)
    url = f"http://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalItem?serviceKey={SERVICE_KEY}"
    params = {'stationId': STATION_ID, 'routeId': ROUTE_ID}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        # API가 에러를 뱉는지 확인하기 위해 로그 출력
        print(f"API Response: {response.status_code}")
        
        root = ET.fromstring(response.content)
        predict_time = root.find(".//predictTime1")
        
        if predict_time is not None:
            return int(predict_time.text)
        return None
    except Exception as e:
        print(f"오류 발생: {e}")
        return None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    requests.post(url, data=payload)

if __name__ == "__main__":
    # 테스트를 위해 시간/요일 조건 다 뺐습니다. 실행하면 무조건 작동합니다.
    remaining_minutes = get_bus_arrival()
    
    if remaining_minutes is not None:
        msg = f"🚌 [705번 버스] {remaining_minutes}분 뒤 도착 예정입니다!"
        send_telegram(msg)
        print(f"전송 완료: {remaining_minutes}분")
    else:
        # 버스 정보가 없을 때도 테스트를 위해 텔레그램을 하나 쏩니다.
        send_telegram("🚌 705번 버스 정보가 현재 없습니다. (운행 종료 등)")
        print("도착 정보 없음")
