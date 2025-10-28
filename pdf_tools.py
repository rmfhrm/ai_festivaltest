import fitz  # PyMuPDF
import openai
import os
from dotenv import load_dotenv
from pytrends.request import TrendReq
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
import docx  # .docx 파일용
import cloudconvert

# --- API 키 설정 (OpenAI + CloudConvert) ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("[pdf_tools] OPENAI_API_KEY를 찾을 수 없습니다.")
else:
    openai.api_key = OPENAI_API_KEY

# 2. CloudConvert API 키 로드
CLOUDCONVERT_API_KEY = os.getenv("CLOUDCONVERT_API_KEY")
if not CLOUDCONVERT_API_KEY:
    print("[pdf_tools] 경고: .env 파일에 CLOUDCONVERT_API_KEY가 없습니다.")
    print("    (HWP 파일 변환이 불가능합니다)")
else:
    cloudconvert.configure(api_key=CLOUDCONVERT_API_KEY)
# ----------------------------------------------------

def analyze_pdf(pdf_file_path):
    """
    PDF, DOCX, HWP 파일 경로를 받아서, AI로 요약한 JSON을 반환합니다.
    (HWP는 CloudConvert API를 통해 PDF로 변환하여 처리)
    """
    print(f"  [pdf_tools] 1. 파일 분석 시작: {pdf_file_path}")
    
    full_text = ""
    if not os.path.exists(pdf_file_path):
        print(f" 오류: '{pdf_file_path}' 파일을 찾을 수 없습니다.")
        return {"error": "PDF 파일을 찾을 수 없습니다."}

    try:
        print(f"    - 파일 타입 감지 중...")
        file_extension = os.path.splitext(pdf_file_path)[1].lower()

        # ---------------------------------
        # PDF / DOCX 처리 
        # ---------------------------------
        if file_extension == '.pdf':
            print("    - PDF 파일 감지. PyMuPDF로 텍스트 추출...")
            doc = fitz.open(pdf_file_path)
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                full_text += page.get_text("text")
            doc.close()
        
        elif file_extension == '.docx':
            print("    - DOCX 파일 감지. python-docx로 텍스트 추출...")
            doc = docx.Document(pdf_file_path)
            for para in doc.paragraphs:
                full_text += para.text + "\n"
        
        # ---------------------------------
        # 3. HWP 처리 (CloudConvert API로 완전 교체)
        # ---------------------------------
        elif file_extension == '.hwp':
            print("    - HWP 파일 감지. CloudConvert API로 PDF 변환 시작...")

            if not CLOUDCONVERT_API_KEY:
                return {"error": "HWP 파일을 처리하려면 .env에 CLOUDCONVERT_API_KEY가 필요합니다."}

            # (1) API 작업(Job) 생성: HWP -> PDF 변환
            job = cloudconvert.Job.create(payload={
                "tasks": {
                    'upload-hwp': { 'operation': 'import/upload' },
                    'convert-to-pdf': { 'operation': 'convert', 'input': 'upload-hwp', 'output_format': 'pdf', 'engine': 'office' },
                    'export-pdf': { 'operation': 'export/url', 'input': 'convert-to-pdf', 'inline': True }
                }
            })

            # (2) HWP 파일 업로드
            upload_task = job['tasks'][0]
            cloudconvert.Task.upload(file_name=pdf_file_path, task=upload_task)

            # (3) 작업 완료 대기
            print("    - (CloudConvert) HWP 파일 업로드 완료. PDF로 변환 중...")
            job = cloudconvert.Job.wait(id=job['id'])

            # (오류 상태 확인 강화)
            if job.get("status") == "error":
                error_message = job.get('message', '알 수 없는 오류')
                for task in job.get("tasks", []):
                    if task.get("status") == "error":
                        error_message = f"Task '{task.get('name', 'unknown')}' failed: {task.get('message', 'No details')}"
                        break
                raise Exception(f"CloudConvert API 오류: {error_message}")

            # (4) 변환된 PDF의 다운로드 URL 가져오기 (더 안전한 방식)
            export_task = None
            for task in job.get("tasks", []):
                # 이름으로 'export-pdf' 작업을 찾음
                if task.get("name") == "export-pdf":
                    export_task = task
                    break
            
            if not export_task:
                 raise Exception("CloudConvert job result does not contain the 'export-pdf' task.")

            if export_task.get("status") != "finished":
                 raise Exception(f"CloudConvert 'export-pdf' task did not finish successfully. Status: {export_task.get('status')}")

            result = export_task.get("result")
            if not result or not result.get("files"):
                 raise Exception("CloudConvert 'export-pdf' task result is missing or does not contain files.")

            files = result.get("files")
            if not files: # files 리스트가 비어있는지 확인
                 raise Exception("CloudConvert 'export-pdf' task result contains an empty 'files' list.")

            # '.get()'을 사용하여 'url' 키에 안전하게 접근
            pdf_url = files[0].get('url') 
            if not pdf_url:
                 # 'url' 키가 없을 경우 명확한 오류 발생
                 raise KeyError("The key 'url' was not found in the first file result of the 'export-pdf' task.")
            
            # (5) 변환된 PDF 데이터를 메모리로 다운로드
            print("    - (CloudConvert) PDF 변환 완료. PDF 데이터 다운로드 중...")
            pdf_response = requests.get(pdf_url)
            pdf_response.raise_for_status()

            # (6) 다운로드한 PDF 데이터를 'fitz'에게 전달
            print("    - (CloudConvert) PDF 데이터 분석 시작...")
            doc = fitz.open(stream=pdf_response.content, filetype="pdf")
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                full_text += page.get_text("text")
            doc.close()
        # --- ⭐️ HWP 처리 (디버깅 버전) 끝 ⭐️ ---
        # ---------------------------------
        
        else:
            print(f"지원하지 않는 파일 형식입니다: {file_extension}")
            return {"error": f"지원하지 않는 파일 형식: {file_extension}. (PDF, DOCX, HWP만 지원)"}

        print(f"    - 텍스트 추출 완료. (총 {len(full_text)}자)")

        # ---------------------------------
        # AI 요약 요청 (기존과 동일)
        # ---------------------------------
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
        
        user_prompt = f"다음 텍스트를 분석하여 JSON으로 요약해줘:\n\n{full_text[:10000]}"

        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # (테스트 결과 gpt-3.5-turbo보다 gpt-4-turbo가 훨씬 안정적입니다)
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens= 4000
        )
        
        ai_response_json_string = response.choices[0].message.content
        print("    - AI 요약 완료.")
        
        # JSON 문자열을 Python 딕셔너리로 변환해서 반환
        return json.loads(ai_response_json_string) 

    except Exception as e:
        print(f" PDF 분석 중 오류 발생: {e}")
        return {"error": f"PDF 분석 오류: {e}"}

# # ----------------------------------------------------
# # 기능 2: 트렌드 분석기 (trend_test.py에서 가져옴)
# # ----------------------------------------------------
# def get_google_trends(keywords_list):
#     """
#     키워드 리스트를 받아서, Google 트렌드 데이터를 딕셔너리로 반환합니다.
#     """
#     print(f"  [analysis_tools] 2. Google 트렌드 분석 시작: {keywords_list}")
    
#     try:
#         pytrends = TrendReq(hl='ko-KR', tz=540)
#         pytrends.build_payload(keywords_list, cat=0, timeframe='today 12-m', geo='KR')
        
#         # (1) 시간별 관심도
#         interest_df = pytrends.interest_over_time()
        
#         # (2) 연관 검색어
#         related_queries_dict = pytrends.related_queries()
        
#         print("    - 트렌드 분석 완료.")
        
#         # (※ DataFrame은 JSON으로 바로 보내기 까다로우므로,
#         #    나중에 필요한 '연관 검색어'만 먼저 가공해서 반환합니다.)
        
#         top_related = {}
#         for kw in keywords_list:
#             top_queries = related_queries_dict.get(kw, {}).get('top')
#             if top_queries is not None and not top_queries.empty:
#                 # 'query' 컬럼의 상위 5개만 리스트로 변환
#                 top_related[kw] = top_queries['query'].head(5).tolist()
#             else:
#                 top_related[kw] = []

#         return {
#             "analyzed_keywords": keywords_list,
#             "top_related_queries": top_related
#             # "interest_data": interest_df.to_dict() # (필요하다면 나중에 추가)
#         }

#     except Exception as e:
#         # (429 오류 등이 발생할 수 있음)
#         print(f"    ❌ 트렌드 분석 중 오류 발생: {e}")
#         return {"error": f"트렌드 분석 오류: {e}"}
    
# # ----------------------------------------------------
# # 기능 3: 트렌드 분석기 (trend_test.py에서 가져옴)
# # ----------------------------------------------------
# # analysis_tools.py 파일에 이어서 추가하는 함수

# def get_naver_buzzwords(keyword):
#     """
#     네이버 VIEW(블로그/카페) 탭을 크롤링하여
#     '함께 찾는 키워드' (연관 태그) 리스트를 반환합니다.
#     """
#     print(f"  [analysis_tools] 3. Naver VIEW 탭 연관 키워드 분석 시작: {keyword}")
    
#     # 1. 네이버 VIEW 탭 검색 URL
#     # (where=view는 블로그/카페 탭을 의미)
#     url = f"https://search.naver.com/search.naver?where=view&sm=tab_jum&query={keyword}"
    
#     # 2. (⭐️중요) 크롤링 차단을 피하기 위한 'User-Agent' 헤더 설정
#     # (우리가 '브라우저'인 척 접속합니다)
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     }

#     try:
#         # 3. 'requests'로 HTML 페이지 가져오기
#         response = requests.get(url, headers=headers, timeout=10)
#         response.raise_for_status() # 200(성공) 코드가 아니면 오류 발생
        
#         # 4. 'BeautifulSoup'로 HTML 파싱(분석) 준비
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # 5. (⭐️가장 중요/취약) "함께 찾는 키워드"가 있는 영역 찾기
#         #    네이버는 이 CSS 선택자(selector)를 자주 바꿉니다.
#         #    '.keyword_box_wrap .keyword' 또는 '.total_tag_area .link_tag' 등을 시도합니다.
#         related_tags_elements = soup.select('.keyword_box_wrap .keyword')
        
#         if not related_tags_elements:
#             # 만약 위 선택자가 작동 안 하면, '연관 태그' 영역을 시도
#             related_tags_elements = soup.select('.total_tag_area .link_tag')

#         buzzwords = []
#         for tag_element in related_tags_elements:
#             # 태그에서 텍스트만 추출
#             buzzword = tag_element.get_text(strip=True)
#             # '#광주맛집' 같은 # 기호 제거 (선택 사항)
#             buzzwords.append(buzzword.replace('#', ''))
            
#         if not buzzwords:
#             print("    - (참고) 연관 키워드를 찾지 못했습니다. (네이버 구조가 변경되었거나 키워드 데이터가 없음)")
#             return []

#         print(f"    - Naver 연관 키워드 수집 완료: {buzzwords[:5]}...") # (로그에는 5개만)
        
#         # 중복 제거 후 상위 10개만 반환
#         return list(dict.fromkeys(buzzwords))[:10]

#     except Exception as e:
#         print(f"    ❌ Naver 크롤링 중 오류 발생: {e}")
#         return []
# # --- (이 파일 자체를 테스트하기 위한 코드) ---
# if __name__ == "__main__":
#     import json
    
#     print("--- 🚀 'analysis_tools.py' 파일 단독 테스트 실행 ---")
    
#     # 1. PDF 분석 테스트
#     pdf_result = analyze_pdf("sample_plan.pdf")
#     print("\n[PDF 분석 결과 (JSON)]")
#     print(json.dumps(pdf_result, indent=2, ensure_ascii=False))
    
#     # 2. 트렌드 분석 테스트
#     trend_result = get_google_trends(["담양 산타 축제", "크리스마스",])
#     print("\n[트렌드 분석 결과 (딕셔너리)]")
#     print(json.dumps(trend_result, indent=2, ensure_ascii=False))