import json
import openai
import os
from dotenv import load_dotenv

# --- (1. .env 파일에서 API 키 로드) ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ 오류: OPENAI_API_KEY를 .env 파일에서 찾을 수 없습니다.")
    exit()
openai.api_key = api_key
client = openai.OpenAI()

# --- (2. 재료 준비: 실제로는 각 함수에서 이 값들을 받아옵니다) ---

# 재료 1: 사용자 직접 입력 (UI에서 왔다고 가정)
user_theme = "2030 연인들을 위한 로맨틱하고 감성적인 크리스마스 축제"

# 재료 2: PDF 분석 결과 (방금 AI가 뽑아준 JSON을 문자열로 가져옴)
pdf_json_string = """
{
    "title": "제7회 담양 산타 축제",
    "date": "2025. 12. 24.(수)~12. 25.(목)",
    "location": "메타랜드 일원",
    "targetAudience": "가족, 연인 등",
    "programs": ["산타축제공연", "야간경관 및 포토존 조성"],
    "events": ["개막 퍼포먼스", "산타 이벤트 운영"],
    "visualKeywords": ["크리스마스 분위기", "야간경관", "포토존"]
}
"""

# 재료 3: 트렌드 분석 결과 (pytrends에서 왔다고 가정)
trends_keywords = ["크리스마스 데이트 코스", "담양 가볼만한 곳", "분위기 좋은 곳"]


# --- (3. AI에게 보낼 '마스터 프롬프트' 조립) ---

print("AI 카드뉴스 초안 생성을 시작합니다...")

system_prompt = """
당신은 대한민국 최고의 축제 홍보 전문 카피라이터입니다.
제공된 '핵심 주제', '기획서 정보', '최신 트렌드'를 모두 조합하여,
'인스타그램 카드뉴스' 6장 분량의 홍보 문구(제목 + 본문)를 생성합니다.

[규칙]
1. '핵심 주제'의 분위기(예: 로맨틱, 감성적)를 텍스트 전체에 반영해야 합니다.
2. '기획서 정보'에 있는 구체적인 프로그램, 날짜, 장소를 반드시 포함해야 합니다.
3. '최신 트렌드' 키워드를 자연스럽게 문장에 녹여내야 합니다.
4. 문구는 짧고, 감각적이며, 이모지를 적절히 사용해야 합니다.
5. 응답은 반드시 [
    {"page": 1, "title": "...", "body": "..."},
    {"page": 2, "title": "...", "body": "..."},
    ...
    {"page": 6, "title": "...", "body": "..."}
   ] 형식의 JSON 리스트로만 응답해야 합니다.
"""

user_prompt = f"""
[핵심 주제]
{user_theme}

[기획서 정보 (JSON)]
{pdf_json_string}

[최신 트렌드 키워드]
{', '.join(trends_keywords)}

---
위 3가지 정보를 모두 반영하여, 인스타그램 카드뉴스 6장 분량의 JSON을 생성해줘.
"""

try:
    response = client.chat.completions.create(
        model="gpt-4-turbo", # 창의적인 문구 생성에는 gpt-4 모델을 추천합니다.
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    print("\n--- ✅ [결과] AI가 생성한 카드뉴스 텍스트 초안 (JSON) ---")
    cardnews_json = response.choices[0].message.content
    print(cardnews_json)
    
    # (이 cardnews_json 데이터를 UI로 보내 `image_741cf8.png` 화면에 뿌려줍니다)

except Exception as e:
    print(f"🚨 AI 카드뉴스 생성 중 오류 발생: {e}")