import requests
import os

def test():
    token = os.environ.get('TG_BOT_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    res = requests.post(url, data={'chat_id': chat_id, 'text': '✅ 테스트 성공!'})
    print(f"결과코드: {res.status_code}")

if __name__ == "__main__":
    test()
