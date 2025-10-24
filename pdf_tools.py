# analysis_tools.py
# (PDF 분석 + 트렌드 분석을 담당하는 '도구' 모음)

import fitz  # PyMuPDF
import openai
import os
from dotenv import load_dotenv
from pytrends.request import TrendReq
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup

# --- OpenAI API 키 설정 (이 모듈도 AI를 쓰니까) ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ [analysis_tools] OPENAI_API_KEY를 찾을 수 없습니다.")
else:
    openai.api_key = api_key

# ----------------------------------------------------
# 기능 1: PDF 분석기 (ai_summary_test.py에서 가져옴)
# ----------------------------------------------------
def analyze_pdf(pdf_file_path):
    """
    PDF 파일 경로를 받아서, AI로 요약한 JSON을 반환합니다.
    """
    print(f"  [analysis_tools] 1. PDF 분석 시작: {pdf_file_path}")
    
    full_text = ""
    if not os.path.exists(pdf_file_path):
        print(f"    ❌ 오류: '{pdf_file_path}' 파일을 찾을 수 없습니다.")
        return {"error": "PDF 파일을 찾을 수 없습니다."}

    try:
        # 1. PDF 텍스트 추출
        doc = fitz.open(pdf_file_path)
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            full_text += page.get_text("text")
        doc.close()
        print(f"    - PDF 텍스트 추출 완료. (총 {len(full_text)}자)")

        # 2. AI에게 요약 요청 (v3 프롬프트 사용)
        system_prompt = """
        당신은 축제 기획서 분석 전문가입니다.
        (이하 생략 ... 이전 v3 프롬프트 내용 ... )
        만약 텍스트에서 특정 정보를 찾을 수 없다면, 해당 값은 "정보 없음"으로 표기하세요.
        """
        # (※ v3 프롬프트 전체 내용을 여기에 붙여넣어 주세요!)
        
        user_prompt = f"다음 텍스트를 분석하여 JSON으로 요약해줘:\n\n{full_text[:15000]}"

        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        ai_response_json_string = response.choices[0].message.content
        print("    - AI 요약 완료.")
        
        # JSON 문자열을 Python 딕셔너리로 변환해서 반환
        return json.loads(ai_response_json_string) 

    except Exception as e:
        print(f"    ❌ PDF 분석 중 오류 발생: {e}")
        return {"error": f"PDF 분석 오류: {e}"}

# ----------------------------------------------------
# 기능 2: 트렌드 분석기 (trend_test.py에서 가져옴)
# ----------------------------------------------------
def get_google_trends(keywords_list):
    """
    키워드 리스트를 받아서, Google 트렌드 데이터를 딕셔너리로 반환합니다.
    """
    print(f"  [analysis_tools] 2. Google 트렌드 분석 시작: {keywords_list}")
    
    try:
        pytrends = TrendReq(hl='ko-KR', tz=540)
        pytrends.build_payload(keywords_list, cat=0, timeframe='today 12-m', geo='KR')
        
        # (1) 시간별 관심도
        interest_df = pytrends.interest_over_time()
        
        # (2) 연관 검색어
        related_queries_dict = pytrends.related_queries()
        
        print("    - 트렌드 분석 완료.")
        
        # (※ DataFrame은 JSON으로 바로 보내기 까다로우므로,
        #    나중에 필요한 '연관 검색어'만 먼저 가공해서 반환합니다.)
        
        top_related = {}
        for kw in keywords_list:
            top_queries = related_queries_dict.get(kw, {}).get('top')
            if top_queries is not None and not top_queries.empty:
                # 'query' 컬럼의 상위 5개만 리스트로 변환
                top_related[kw] = top_queries['query'].head(5).tolist()
            else:
                top_related[kw] = []

        return {
            "analyzed_keywords": keywords_list,
            "top_related_queries": top_related
            # "interest_data": interest_df.to_dict() # (필요하다면 나중에 추가)
        }

    except Exception as e:
        # (429 오류 등이 발생할 수 있음)
        print(f"    ❌ 트렌드 분석 중 오류 발생: {e}")
        return {"error": f"트렌드 분석 오류: {e}"}
    
# ----------------------------------------------------
# 기능 3: 트렌드 분석기 (trend_test.py에서 가져옴)
# ----------------------------------------------------
# analysis_tools.py 파일에 이어서 추가하는 함수

def get_naver_buzzwords(keyword):
    """
    네이버 VIEW(블로그/카페) 탭을 크롤링하여
    '함께 찾는 키워드' (연관 태그) 리스트를 반환합니다.
    """
    print(f"  [analysis_tools] 3. Naver VIEW 탭 연관 키워드 분석 시작: {keyword}")
    
    # 1. 네이버 VIEW 탭 검색 URL
    # (where=view는 블로그/카페 탭을 의미)
    url = f"https://search.naver.com/search.naver?where=view&sm=tab_jum&query={keyword}"
    
    # 2. (⭐️중요) 크롤링 차단을 피하기 위한 'User-Agent' 헤더 설정
    # (우리가 '브라우저'인 척 접속합니다)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # 3. 'requests'로 HTML 페이지 가져오기
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # 200(성공) 코드가 아니면 오류 발생
        
        # 4. 'BeautifulSoup'로 HTML 파싱(분석) 준비
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 5. (⭐️가장 중요/취약) "함께 찾는 키워드"가 있는 영역 찾기
        #    네이버는 이 CSS 선택자(selector)를 자주 바꿉니다.
        #    '.keyword_box_wrap .keyword' 또는 '.total_tag_area .link_tag' 등을 시도합니다.
        related_tags_elements = soup.select('.keyword_box_wrap .keyword')
        
        if not related_tags_elements:
            # 만약 위 선택자가 작동 안 하면, '연관 태그' 영역을 시도
            related_tags_elements = soup.select('.total_tag_area .link_tag')

        buzzwords = []
        for tag_element in related_tags_elements:
            # 태그에서 텍스트만 추출
            buzzword = tag_element.get_text(strip=True)
            # '#광주맛집' 같은 # 기호 제거 (선택 사항)
            buzzwords.append(buzzword.replace('#', ''))
            
        if not buzzwords:
            print("    - (참고) 연관 키워드를 찾지 못했습니다. (네이버 구조가 변경되었거나 키워드 데이터가 없음)")
            return []

        print(f"    - Naver 연관 키워드 수집 완료: {buzzwords[:5]}...") # (로그에는 5개만)
        
        # 중복 제거 후 상위 10개만 반환
        return list(dict.fromkeys(buzzwords))[:10]

    except Exception as e:
        print(f"    ❌ Naver 크롤링 중 오류 발생: {e}")
        return []
# --- (이 파일 자체를 테스트하기 위한 코드) ---
if __name__ == "__main__":
    import json
    
    print("--- 🚀 'analysis_tools.py' 파일 단독 테스트 실행 ---")
    
    # 1. PDF 분석 테스트
    pdf_result = analyze_pdf("sample_plan.pdf")
    print("\n[PDF 분석 결과 (JSON)]")
    print(json.dumps(pdf_result, indent=2, ensure_ascii=False))
    
    # 2. 트렌드 분석 테스트
    trend_result = get_google_trends(["담양 산타 축제", "크리스마스",])
    print("\n[트렌드 분석 결과 (딕셔너리)]")
    print(json.dumps(trend_result, indent=2, ensure_ascii=False))