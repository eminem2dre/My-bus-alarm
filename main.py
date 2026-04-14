import requests
import xml.etree.ElementTree as ET
import os
from datetime import datetime
import pytz

# 1. GitHub Secrets에 저장된 환경 변수 불러오기
# 직접 코드를 수정할 필요 없이 GitHub 설정에서 등록만 하면 됩니다.
SERVICE_KEY = os.environ.get('BUS_API_KEY')
BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
CHAT_ID = os.environ.get('TG_CHAT_ID')

# 2. 버스 및 정류소 고유 정보 (고양시 기준)
# 고양동산초등학교·창릉동행정복지센터 (19573) -> stationId: 218000624
# 705번 버스 -> routeId: 100100107
STATION_ID = '218000624'
ROUTE_ID = '100100107'

def get_bus_arrival():
    """경기도 버스 도착 정보 API를 호출하여 남은 시간을 반환합니다."""
    url = "http://apis.data.go.kr/6410000/busarrivalservice/getBusArrivalItem"
    
    # API 키가 이미 인코딩되어 있으므로 중복 인코딩 방지를 위해 dict 대신 직접 파라미터 구성
    params = {
        'serviceKey': SERVICE_KEY,
        'stationId': STATION_ID,
        'routeId': ROUTE_ID
    }
    
    try:
        # 10초 내에 응답이 없으면 타임아웃 처리
        response = requests.get(url, params=params, timeout=10)
        
        # XML 데이터 파싱
        root = ET.fromstring(response.content)
        
        # 결과 메시지 확인 (정상: '정상적으로 처리되었습니다.')
        # 남은 시간 데이터(predictTime1) 추출
        predict_time = root.find(".//predictTime1")
        
        if predict_time is not None:
            return int(predict_time.text)
        else:
            print("도착 정보가 없습니다. (운행 종료 또는 정보 미제공)")
            return None
            
    except Exception as e:
        print(f"API 호출 중 오류 발생: {e}")
        return None

def send_telegram(message):
    """텔레그램 봇을 통해 사용자에게 메시지를 전송합니다."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")

# 3. 메인 실행 로직
if __name__ == "__main__":
    # 한국 시간 설정
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(seoul_tz)
    
    # 현재 시간이 평일(월~금) 오전 7시 ~ 8시 사이인지 확인
    # weekday()는 0(월)부터 6(일)까지입니다. 5 미만이면 평일입니다.
    if now.weekday() < 5 and 7 <= now.hour < 8:
        remaining_minutes = get_bus_arrival()
        
        # 남은 시간이 10분 이하일 때만 알림 전송
        if remaining_minutes is not None and remaining_minutes <= 10:
            msg = f"🚌 [705번 버스 알림]\n지금 {remaining_minutes}분 뒤 도착 예정입니다!\n준비하고 정류장으로 나가세요."
            send_telegram(msg)
            print(f"알림 전송 완료: {remaining_minutes}분 전")
        else:
            print(f"조건 미충족 (남은 시간: {remaining_minutes}분)")
    else:
        print("알림 설정 시간이 아니거나 주말입니다.")
