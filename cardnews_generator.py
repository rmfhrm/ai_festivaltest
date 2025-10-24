# cardnews_generator.py

import json
import openai
import os
from dotenv import load_dotenv

# --- (1. .env 파일에서 API 키 로드) ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ [cardnews_generator] OPENAI_API_KEY를 찾을 수 없습니다.")
    exit()
openai.api_key = api_key
client = openai.OpenAI()

# ----------------------------------------------------
# 기능 1: 카드뉴스 텍스트 생성기
# (보여주신 코드를 '함수'로 포장했습니다)
# ----------------------------------------------------
def create_cardnews_text(user_theme, pdf_data_dict, trends_keywords, naver_buzzwords):
    """
    모든 재료를 받아 AI 카피라이터에게 카드뉴스 텍스트 초안(JSON)을 요청합니다.
    """
    print(f"  [cardnews_generator] 3. AI 카피라이터 호출 시작...")

    # pdf_data_dict (딕셔너리)를 JSON 문자열로 변환
    pdf_json_string = json.dumps(pdf_data_dict, ensure_ascii=False, indent=2)

    system_prompt = """
    당신은 대한민국 최고의 축제 홍보 전문 카피라이터입니다.
    (이하 생략 ... 카드뉴스 생성용 프롬프트 ... )
    ] 형식의 JSON 리스트로만 응답해야 합니다.
    """
    # (※ 보여주신 '카피라이터' system_prompt 전체를 여기에 붙여넣으세요!)

    user_prompt = f"""
    [핵심 주제]
    {user_theme}

    [기획서 정보 (JSON)]
    {pdf_json_string}

    [최신 트렌드 키워드 (Google)]
    {', '.join(trends_keywords)}

    [최신 소셜 트렌드 (Naver)]
    {', '.join(naver_buzzwords)}

---

    ---
    위 3가지 정보를 모두 반영하여, 인스타그램 카드뉴스 6장 분량의 JSON을 생성해줘.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        cardnews_json_string = response.choices[0].message.content
        print("    - 카드뉴스 텍스트 생성 완료.")
        
        # JSON 문자열을 Python 딕셔너리/리스트로 변환해서 반환
        return json.loads(cardnews_json_string)

    except Exception as e:
        print(f"    ❌ 카드뉴스 생성 중 오류 발생: {e}")
        return {"error": f"카드뉴스 생성 오류: {e}"}

# --- (이 파일 자체를 테스트하기 위한 코드) ---
if __name__ == "__main__":
    
    print("--- 🚀 'cardnews_generator.py' 파일 단독 테스트 실행 ---")
    
    # (가짜 재료로 테스트)
    test_theme = "2030 연인들을 위한 로맨틱 축제"
    test_pdf_data = {
        "title": "제7회 담양 산타 축제",
        "programs": ["야간경관", "산타 포토존"]
    }
    test_trends = ["크리스마스 데이트 코스", "분위기 좋은 곳"]
    
    cardnews_result = create_cardnews_text(test_theme, test_pdf_data, test_trends)
    
    print("\n[카드뉴스 생성 결과 (JSON)]")
    print(json.dumps(cardnews_result, indent=2, ensure_ascii=False))