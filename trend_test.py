import pandas as pd
from pytrends.request import TrendReq

print("Google Trends 분석을 시작합니다...")

try:
    # 1. Google Trends 연결 (한국 시간, 한국어)
    pytrends = TrendReq(hl='ko-KR', tz=540) # 540 = 한국시간(UTC+9)

    # 2. 분석할 키워드 (UI에서 사용자가 입력할 값)
    keywords = ["크리스마스", "가족 나들이", "담양 산타 축제"]
    
    # 3. 데이터 요청 (지난 1년간, 대한민국 기준)
    pytrends.build_payload(
        keywords,
        cat=0,                # 카테고리 (0=전체)
        timeframe='today 12-m', # 'today 12-m' = 지난 12개월
        geo='KR',             # 지역 (KR=대한민국)
        gprop=''              # 검색 속성 (''=웹 검색)
    )

    print(f"키워드: {keywords} (지난 1년, 대한민국)")

    # 4. (결과 1) 시간별 관심도 추이 가져오기
    interest_over_time_df = pytrends.interest_over_time()
    
    if not interest_over_time_df.empty:
        print("\n--- [결과 1] 시간별 관심도 추이 ---")
        # 'isPartial' 열은 True/False 값이라 제외하고 출력
        print(interest_over_time_df.drop(columns='isPartial').tail(10)) # 마지막 10개 행만 출력
    else:
        print("\n--- [결과 1] 시간별 관심도 추이 데이터가 없습니다 ---")


    # 5. (결과 2) 연관 검색어 가져오기
    #    AI 프롬프트에 활용할 아주 유용한 데이터입니다.
    related_queries_dict = pytrends.related_queries()
    
    print("\n---  [결과 2] 연관 검색어 ---")
    
    for kw in keywords:
        print(f"\n--- '{kw}'의 연관 검색어 ---")
        
        # '상승 중인' 연관 검색어
        rising_queries = related_queries_dict.get(kw, {}).get('rising')
        if rising_queries is not None and not rising_queries.empty:
            print("[상승세 🔥]")
            print(rising_queries.head()) # 상위 5개만 출력
        else:
            print("[상승세 🔥] 데이터 없음")
            
        # '인기 있는' 연관 검색어
        top_queries = related_queries_dict.get(kw, {}).get('top')
        if top_queries is not None and not top_queries.empty:
            print("\n[인기 검색 👑]")
            print(top_queries.head()) # 상위 5개만 출력
        else:
            print("\n[인기 검색 👑] 데이터 없음")

except Exception as e:
    print(f" 오류 발생: {e}")
    print("    (참고: 너무 짧은 기간에 자주 요청하면 Google에서 일시적으로 차단할 수 있습니다.)")