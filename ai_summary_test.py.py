import fitz  # PyMuPDF
import os
import openai
from dotenv import load_dotenv  # 1. .env 라이브러리 import

# --- ⭐️ 이 부분이 수정되었습니다! ---
# 2. .env 파일에서 환경 변수를 불러옵니다.
load_dotenv() 

# 3. os.getenv()를 사용해 환경 변수에서 API 키를 안전하게 가져옵니다.
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ 오류: OPENAI_API_KEY를 .env 파일에서 찾을 수 없습니다.")
    print("    .env 파일에 'OPENAI_API_KEY=sk-...' 형식으로 키를 입력했는지 확인하세요.")
    exit() # 키가 없으면 프로그램 종료

openai.api_key = api_key
# --- 수정된 부분 끝 ---


print("PDF 파일 분석 및 AI 요약을 시작합니다...")

pdf_filename = "sample_plan.pdf" # 분석할 PDF 파일

full_text = "" 

if not os.path.exists(pdf_filename):
    print(f"❌ 오류: '{pdf_filename}' 파일을 찾을 수 없습니다.")
else:
    try:
        # --- 1. PDF 텍스트 추출 ---
        doc = fitz.open(pdf_filename)
        print(f"✅ '{pdf_filename}' 파일 열기 성공. (총 {doc.page_count} 페이지)")
        
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            full_text += page.get_text("text")
        doc.close()
        
        print("✅ PDF 텍스트 추출 완료. 이제 AI에게 요약을 요청합니다...")

        # --- 2. AI에게 정보 추출 요청 ---
        
        # AI의 역할을 정의 (시스템 프롬프트) - ⭐️ v3 업그레이드!
        system_prompt = """
        당신은 축제 기획서 분석 전문가입니다.
        사용자가 제공하는 기획서 텍스트를 분석하여,
        아래 항목에 해당하는 '구체적인 상세 내용'을 추출하고
        반드시 JSON 형식으로만 응답해주세요.
        
        - "title": 축제 공식 제목
        - "date": 축제가 열리는 정확한 날짜와 기간
        - "location": 축제가 열리는 구체적인 장소
        - "host": 주최 기관
        - "organizer": 주관 기관
        - "targetAudience": 축제의 주요 대상 고객 (예: '가족 단위 방문객', '2030 연인', '어린이'). '주요 타깃' 또는 '고객층' 같은 단어 근처를 찾아보세요.
        - "summary": 축제의 목적과 핵심 내용을 요약
        - "programs": 방문객이 '체험'할 수 있는 주요 프로그램의 '구체적인 내용' (리스트). (주의: '프로그램'이라는 제목의 목차뿐만 아니라, 그 '상세 내용'을 찾아주세요.)
        - "events": 축제 기간 중 열리는 '특별 이벤트'의 '구체적인 내용' (리스트). (예: '개막 퍼포먼스', '산타 이벤트 운영'). (주의: '이벤트'라는 제목의 목차뿐만 아니라, 그 '상세 내용'을 찾아주세요.)
        - "visualKeywords": 카드뉴스 디자인에 참고할 만한 시각적 키워드 (예: "야간 조명", "크리스마스 트리", "산타") (리스트)
        - "contactInfo": 방문객이 문의할 수 있는 전화번호 또는 공식 웹사이트 주소
        - "directions": 방문객이 축제 장소에 '오시는 길' (예: 'xx IC에서 10분', '담양 버스터미널에서 5번 버스', '주차: 메타랜드 주차장 이용').
                       (주의: '사업 지시'나 '제안서 접수' 내용이 아님. 방문객용 교통/주차 정보가 명확히 없으면 "정보 없음"으로 표기)
        
        만약 텍스트에서 특정 정보를 찾을 수 없다면, 해당 값은 "정보 없음"으로 표기하세요.
        """
        
        user_prompt = f"""
        다음 축제 기획서 텍스트를 분석하여 JSON으로 요약해줘:
        
        --- 기획서 텍스트 시작 ---
        {full_text[:15000]} 
        --- 기획서 텍스트 끝 ---
        """ 

        client = openai.OpenAI() 
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"} 
        )
        
        print("\n--- ✅ [결과] AI가 추출한 핵심 정보 (JSON) ---")
        ai_response_json = response.choices[0].message.content
        print(ai_response_json)

    except openai.AuthenticationError:
        print("❌ 오류: OpenAI API 키가 잘못되었습니다. .env 파일의 키를 다시 확인하세요.")
    except Exception as e:
        print(f"🚨 처리 중 오류 발생: {e}")