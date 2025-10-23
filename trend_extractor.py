import requests
import json
import datetime
import os  # .env 파일을 읽기 위해 os 라이브러리 추가
from dotenv import load_dotenv  # .env 파일을 로드하는 함수 추가

def get_naver_datalab_trend(client_id, client_secret, keywords_groups):
    """
    네이버 데이터랩 API를 호출하여 키워드 트렌드 데이터를 가져오는 함수입니다.
    (함수 내용은 이전과 동일합니다)
    """
    
    url = "https://openapi.naver.com/v1/datalab/search"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json"
    }
    end_date = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=90)).strftime("%Y-%m-%d")

    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": [
            {
                "groupName": group[0],
                "keywords": group[1:]
            } for group in keywords_groups
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body))
        
        if response.status_code == 200:
            print(" 네이버 데이터랩 API 호출 성공!")
            return response.json()
        else:
            print(f" 오류 발생: {response.status_code}")
            print(f"오류 메시지: {response.text}")
            return None
            
    except Exception as e:
        print(f" API 요청 중 예외 발생: {e}")
        return None

# --- [여기서부터 실제 코드 실행] ---
if __name__ == "__main__":
    
    # 1.  .env 파일 로드
    # 이 스크립트가 실행될 때, 같은 폴더에 있는 .env 파일을 찾아서
    # 그 안의 변수들을 환경 변수로 설정해 줍니다.
    load_dotenv()

    # 2.  환경 변수에서 Client ID와 Secret을 안전하게 가져오기
    # os.environ.get('변수명')을 사용합니다.
    MY_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
    MY_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")

    # (필수) 키 값이 .env 파일에 잘 설정되었는지 확인
    if not MY_CLIENT_ID or not MY_CLIENT_SECRET:
        print(" 오류: NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET이 .env 파일에 설정되지 않았습니다.")
        print("   .env 파일을 확인하고 다시 실행해 주세요.")
    else:
        # 3. 분석하고 싶은 키워드 그룹을 정의합니다.
        keyword_list = [
            ["담양산타축제", "담양 산타축제", "담양 크리스마스"], # 첫 번째 그룹 (주제어)
            ["크리스마스 축제", "겨울 축제"]                 # 두 번째 그룹 (비교군)
        ]

        # 4. 함수를 호출하여 트렌드 데이터를 가져옵니다.
        trend_data = get_naver_datalab_trend(MY_CLIENT_ID, MY_CLIENT_SECRET, keyword_list)

        # 5. 결과를 예쁘게 출력해 봅니다.
        if trend_data:
            print("\n--- [트렌드 분석 결과] ---")
            
            for result in trend_data['results']:
                print(f"\n[키워드 그룹: {result['title']}]")
                print(" (검색 키워드: " + ", ".join(result['keywords']) + ")")
                print("-----------------------------------")
                print("날짜\t\t검색량 비율 (ratio)")
                print("-----------------------------------")
                for data in result['data']:
                    print(f"{data['period']}\t{data['ratio']:.2f}")