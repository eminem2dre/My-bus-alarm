import os
import time
import requests
import datetime
import pytz


TARGET_ROUTE_ID = 100100587
TARGET_STATION_ID = '218000641'
ALERT_THRESHOLD_MIN = 10
CHECK_INTERVAL = 180
START_HOUR = 7
END_HOUR = 8


def check_bus(api_key, bot_token, chat_id, now):
    url = "https://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalListv2"
    params = {
        'serviceKey': api_key,
        'stationId': TARGET_STATION_ID,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    result_code = data['response']['msgHeader']['resultCode']
    if result_code != 0:
        print(f"API 에러 (resultCode: {result_code})")
        return

    arrivals = data['response']['msgBody'].get('busArrivalList', [])
    predict_time = None

    for arrival in arrivals:
        if arrival.get('routeId') == TARGET_ROUTE_ID:
            raw = arrival.get('predictTime1')
            if raw and raw != '':
                predict_time = int(raw)
            break

    if predict_time is None:
        print(f"[{now:%H:%M}] 705번 도착 정보 없음")
        return

    if predict_time >= ALERT_THRESHOLD_MIN:
        print(f"[{now:%H:%M}] 705번 {predict_time}분 전 - 여유 있음")
        return

    msg = f"⚠️ [705번 알람]\n현재 {predict_time}분 전입니다. 빨리 나오세요!"
    send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    tg_resp = requests.post(send_url, data={'chat_id': chat_id, 'text': msg}, timeout=10)

    if tg_resp.ok:
        print(f"[{now:%H:%M}] 705번 {predict_time}분 전 - 전송 완료")
    else:
        print(f"[{now:%H:%M}] 텔레그램 전송 실패: {tg_resp.status_code}")


def main():
    api_key = os.environ.get('BUS_API_KEY')
    bot_token = os.environ.get('TG_BOT_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')

    if not all([api_key, bot_token, chat_id]):
        print("필수 환경변수 누락")
        return

    kst = pytz.timezone('Asia/Seoul')

    # KST 7시까지 대기
    while True:
        now = datetime.datetime.now(kst)
        if now.hour >= START_HOUR:
            break
        wait = 60 - now.second
        print(f"[{now:%H:%M}] 아직 {START_HOUR}시 전 - {wait}초 대기")
        time.sleep(wait)

    # KST 7시~8시 동안 3분 간격 체크
    while True:
        now = datetime.datetime.now(kst)
        if now.hour >= END_HOUR:
            print(f"[{now:%H:%M}] {END_HOUR}시 지남 - 종료")
            break
        try:
            check_bus(api_key, bot_token, chat_id, now)
        except Exception as e:
            print(f"[{now:%H:%M}] 에러: {e}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
