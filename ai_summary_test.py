import fitz  # PyMuPDF
import os
import openai
from dotenv import load_dotenv  
load_dotenv() 

# 3. os.getenv()를 사용해 환경 변수에서 API 키를 안전하게 가져옵니다.
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print(" 오류: OPENAI_API_KEY를 .env 파일에서 찾을 수 없습니다.")
    print("    .env 파일에 'OPENAI_API_KEY=sk-...' 형식으로 키를 입력했는지 확인하세요.")
    exit() # 키가 없으면 프로그램 종료

openai.api_key = api_key
# --- 수정된 부분 끝 ---


print("PDF 파일 분석 및 AI 요약을 시작합니다...")

pdf_filename = "sample_plan.pdf" # 분석할 PDF 파일

full_text = "" 

if not os.path.exists(pdf_filename):
    print(f" 오류: '{pdf_filename}' 파일을 찾을 수 없습니다.")
else:
    try:
        # --- 1. PDF 텍스트 추출 ---
        doc = fitz.open(pdf_filename)
        print(f"'{pdf_filename}' 파일 열기 성공. (총 {doc.page_count} 페이지)")
        
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            full_text += page.get_text("text")
        doc.close()
        
        print(" PDF 텍스트 추출 완료. 이제 AI에게 요약을 요청합니다...")

        # --- 2. AI에게 정보 추출 요청 ---
        
        system_prompt = """
        당신은 축제 기획서 분석 전문가입니다.
        사용자가 제공하는 기획서 텍스트를 분석하여,
        아래 항목에 해당하는 '구체적인 상세 내용'을 추출하고
        반드시 JSON 형식으로만 응답해주세요.
        
        [중요 규칙]
        1. 오직 아래 목록에서 요청된 항목('title', 'date', 'location' 등)만 추출하세요.
        2. '예산', '사업비', '총금액' 등 **금액(돈)과 관련된 모든 정보**는 
           그것이 어떤 항목이든 **절대로** 요약에 포함하지 마세요.
        3. '안전 대책(Safety Measures)', '행정 사항', '입찰' 등 
           목록에 없는 다른 정보도 **절대로** 요약에 포함하지 마세요.
        
        --- (추출할 항목 목록) ---
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

        [최종 확인 규칙]
        응답하기 전, 당신이 생성한 JSON을 다시 한번 확인하세요.
        JSON 내부에 '예산', '사업비' 등 **금액(돈)과 관련된 내용**이나, 
        '안전 대책' 등 --- (추출할 항목 목록) ---에 없었던 항목이 포함되어 있나요?
        만약 그렇다면, 그 항목들을 **반드시 삭제**하고
        오직 'title'부터 'directions'까지의 항목만 포함해서 응답하세요.
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
        
        print("\n---  [결과] AI가 추출한 핵심 정보 (JSON) ---")
        ai_response_json = response.choices[0].message.content
        print(ai_response_json)

    except openai.AuthenticationError:
        print(" 오류: OpenAI API 키가 잘못되었습니다. .env 파일의 키를 다시 확인하세요.")
    except Exception as e:
        print(f" 처리 중 오류 발생: {e}")