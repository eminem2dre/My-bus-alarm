import os
import requests
import datetime
import pytz


TARGET_ROUTE_ID = 100100587
TARGET_STATION_ID = '218000641'
ALERT_THRESHOLD_MIN = 10


def get_bus_info():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.datetime.now(kst)

    api_key = os.environ.get('BUS_API_KEY')
    bot_token = os.environ.get('TG_BOT_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')

    if not all([api_key, bot_token, chat_id]):
        print("필수 환경변수 누락 (BUS_API_KEY, TG_BOT_TOKEN, TG_CHAT_ID)")
        return

    url = "https://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalListv2"
    params = {
        'serviceKey': api_key,
        'stationId': TARGET_STATION_ID,
    }

    try:
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
            print(f"[{now:%H:%M}] 705번 도착 정보 없음 - 전송 스킵")
            return

        if predict_time >= ALERT_THRESHOLD_MIN:
            print(f"[{now:%H:%M}] 705번 {predict_time}분 전 - 여유 있음, 전송 스킵")
            return

        msg = f"⚠️ [705번 알람]\n현재 {predict_time}분 전입니다. 빨리 나오세요!"

        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        tg_resp = requests.post(send_url, data={'chat_id': chat_id, 'text': msg}, timeout=10)

        if tg_resp.ok:
            print(f"[{now:%H:%M}] 705번 {predict_time}분 전 - 전송 완료")
        else:
            print(f"[{now:%H:%M}] 텔레그램 전송 실패: {tg_resp.status_code} {tg_resp.text}")

    except requests.RequestException as e:
        print(f"네트워크 에러: {e}")
    except (KeyError, ValueError) as e:
        print(f"응답 파싱 에러: {e}")
    except Exception as e:
        print(f"예상치 못한 에러: {e}")


if __name__ == "__main__":
    get_bus_info()
