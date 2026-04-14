import os
import requests
import datetime
import pytz
import xml.etree.ElementTree as ET

def get_bus_info():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.datetime.now(kst)
    
    api_key = os.environ.get('BUS_API_KEY')
    bot_token = os.environ.get('TG_BOT_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')

    # 705번 노선 ID (경기도 기준)
    TARGET_ROUTE_ID = '229000045'
    
    url = "https://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalList"
    params = {'serviceKey': api_key, 'stationId': '19573'}

    try:
        response = requests.get(url, params=params, timeout=10)
        root = ET.fromstring(response.content)
        
        msg = ""
        should_send = False

        for arrival in root.findall('.//busArrivalList'):
            route_id = arrival.findtext('routeId')
            
            # 705번 노선만 필터링
            if route_id == TARGET_ROUTE_ID:
                predict_time = arrival.findtext('predictTime1')
                
                if predict_time and int(predict_time) < 10:
                    msg = f"⚠️ [705번 알람]\n현재 {predict_time}분 전입니다. 빨리 나오세요!"
                    should_send = True
                break # 705번 찾았으면 루프 종료

        if should_send:
            send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(send_url, data={'chat_id': chat_id, 'text': msg})
            print(f"705번 {predict_time}분 전 - 전송 완료")
        else:
            print("705번이 10분 이상 남았거나 정보가 없음 - 전송 스킵")

    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    get_bus_info()
