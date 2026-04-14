import os
import requests
import datetime
import pytz

def get_bus_info():
    # 1. 한국 시간 설정 (현재 오전 7시 30분 상황 반영)
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.datetime.now(kst)
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 스크립트 실행 시작")

    # 2. 환경 변수 로드
    api_key = os.environ.get('BUS_API_KEY')
    bot_token = os.environ.get('TG_BOT_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')

    # 3. 버스 API 설정 (경기도 v2 주소 + 정류소 ID 19573)
    url = "https://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalList"
    
    params = {
        'serviceKey': api_key,
        'stationId': '19573', # 어제 알려주신 정류소 번호 적용
        'format': 'json'
    }

    try:
        # API 호출
        response = requests.get(url, params=params, timeout=10)
        print(f"API 응답 상태: {response.status_code}")
        
        # 4. 텔레그램 메시지 조립 및 전송
        # 지금은 실행 확인용이며, 나중에 도착 시간 데이터를 뽑아서 넣을 수 있습니다.
        msg = f"🚌 [19573 정류소] {now.strftime('%H:%M')} 알림\n서버 정상 작동 중입니다."

        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(send_url, data={'chat_id': chat_id, 'text': msg})
        print("텔레그램 전송 완료")

    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    get_bus_info()
