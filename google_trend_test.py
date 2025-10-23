# 필요한 라이브러리를 불러옵니다.
from pytrends.request import TrendReq
import pandas as pd
import datetime

def get_google_trends(keywords_list):
    """
    Google Trends API (pytrends)를 이용해 키워드 트렌드 데이터를 가져옵니다.

    Args:
        keywords_list (list): 분석할 키워드 리스트 (예: ["담양산TA축제", "겨울 축제"])
    """
    
    # Google Trends에 연결합니다.
    # hl='ko-KR' (한국어), tz=540 (한국 시간대, UTC+9*60)
    pytrends = TrendReq(hl='ko-KR', tz=540)

    # 검색 조건을 설정합니다.
    # timeframe: 'today 3-m' (오늘 기준 최근 3개월)
    # geo: 'KR' (대한민국)
    # 
    # 네이버와 달리, 구글은 '그룹' 개념이 아닌 개별 키워드를 리스트로 전달합니다.
    pytrends.build_payload(kw_list=keywords_list,
                           cat=0,
                           timeframe='today 3-m',
                           geo='KR',
                           gprop='')

    # 'Interest Over Time' (시간에 따른 관심도 변화) 데이터를 가져옵니다.
    # 이 데이터는 'pandas DataFrame'이라는 표(테이블) 형태로 반환됩니다.
    print("Google Trends 데이터 가져오는 중...")
    try:
        interest_data = pytrends.interest_over_time()
        
        if interest_data.empty:
            print("데이터가 없습니다. (키워드가 너무 적게 검색되었을 수 있습니다)")
            return None
        
        # 'isPartial' 컬럼은 "데이터가 부분적인가?"라는 뜻이라 제외하고 출력합니다.
        if 'isPartial' in interest_data.columns:
            interest_data = interest_data.drop(columns=['isPartial'])
            
        return interest_data

    except Exception as e:
        print(f"Google Trends API 오류 발생: {e}")
        return None

# --- [여기서부터 실제 코드 실행] ---
if __name__ == "__main__":
    
    # 1. 분석하고 싶은 키워드를 리스트로 정의합니다.
    # (주의: 구글 트렌드는 철자나 띄어쓰기에 매우 민감합니다.)
    keywords = ["담양 산타축제", "겨울 축제", "크리스마스 축제"]

    # 2. 함수를 호출하여 트렌드 데이터를 가져옵니다.
    trend_df = get_google_trends(keywords)

    # 3. 결과를 출력합니다.
    if trend_df is not None:
        print("\n--- [Google Trends 분석 결과 (Pandas DataFrame)] ---")
        print(trend_df)
        
        print("\n--- [최근 5일간의 데이터] ---")
        print(trend_df.tail(5))
        