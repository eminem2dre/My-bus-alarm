import os
import requests
import datetime
import pytz

def get_bus_info():
    # 1. 시간 설정 (한국 시간 강제 지정)
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.datetime.now(kst)
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 스크립트 실행 시작")

    # 환경 변수 로드
    api_key = os.environ.get('BUS_API_KEY')
    bot_token = os.environ.get('TG_BOT_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')

    # 2. 실행 조건 체크 (오전 7시인지 확인)
    # 수동으로 돌릴 때도 확인하기 위해 일단 7시 조건은 넣어두되, 로그를 남깁니다.
    if now.hour != 7:
        print(f"현재 시간은 {now.hour}시입니다. 7시가 아니므로 종료합니다.")
        # 만약 수동 실행 시 무조건 보내고 싶다면 위 두 줄을 지우세요.
        return 

    # 3. 버스 정보 가져오기 (여기에 실제 API URL과 파라미터를 넣으세요)
    # 기존에 사용하시던 URL과 노선 ID를 그대로 쓰시면 됩니다.
    url = "공공데이터포털_버스정보_URL" 
    params = {
        'serviceKey': api_key,
        # 'cityCode': '...', 
        # 'routeId': '...'
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"API 응답 상태: {response.status_code}")
        
        # 실제 메시지 조립 및 전송 로직
        msg = f"🚌 {now.strftime('%H:%M')} 버스 도착 정보입니다.\n(여기에 실제 데이터 파싱 결과 추가)"
        
        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        send_res = requests.post(send_url, data={'chat_id': chat_id, 'text': msg})
        
        if send_res.status_code == 200:
            print("텔레그램 메시지 전송 성공!")
        else:
            print(f"텔레그램 전송 실패: {send_res.text}")

    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    get_bus_info()

