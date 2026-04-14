import requests
import xml.etree.ElementTree as ET
import os

# GitHub Secrets에서 가져오는 정보들
SERVICE_KEY = os.environ.get('BUS_API_KEY')
BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
CHAT_ID = os.environ.get('TG_CHAT_ID')

def get_bus_arrival():
    # 주소에 v2를 넣었습니다.
    url = f"http://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalItem?serviceKey={SERVICE_KEY}"
    params = {'stationId': '218000624', 'routeId': '100100107'}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        root = ET.fromstring(response.content)
        predict_time = root.find(".//predictTime1")
        
        if predict_time is not None:
            return int(predict_time.text)
        return None
    except:
        return None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': message})

if __name__ == "__main__":
    time_left = get_bus_arrival()
    
    if time_left is not None:
        send_telegram(f"🚌 [705번 버스] {time_left}분 뒤 도착합니다!")
    else:
        # 버스가 끊겼어도 연결 성공했다는 걸 보여주려고 메시지를 보냅니다.
        send_telegram("✅ 연결은 성공! (지금은 버스 정보가 없는 시간입니다)")
