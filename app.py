# app.py (메인 지휘자 파일 - 최종 조립본)

import json
import os


# ----------------------------------------------------
# 1. 우리가 만든 모든 기능 파일(모듈)들을 import
# ----------------------------------------------------
# (※ 각 파일에 오류가 없어야 import가 성공합니다)
try:
    import pdf_tools       # (PDF, 텍스트 트렌드 분석 모듈)
    import visual_analyzer      # (시각 분석 모듈)
    import cardnews_generator   # (카드뉴스 텍스트 생성 모듈)
except ImportError as e:
    print(f"🚨 [app.py] 모듈 import 실패! {e}")
    print("   파일 이름(analysis_tools.py 등)이 올바른지 확인하세요.")
    exit()
except Exception as e:
    print(f"🚨 [app.py] 모듈 로딩 중 오류 발생! {e}")
    exit()

# ----------------------------------------------------
# 2. (가상) 프론트엔드에서 넘어온 입력 데이터
# ----------------------------------------------------
print("--- [메인 서버] 프론트엔드로부터 요청 수신 (시뮬레이션) ---")
USER_THEME = "2030 연인들을 위한 로맨틱하고 감성적인 크리스마스 축제"
script_dir = os.path.dirname(os.path.abspath(__file__))
PDF_FILE_PATH = os.path.join(script_dir, "sample_plan.pdf")
KEYWORDS = ["양림 산타 축제", "크리스마스 데이트", "따뜻함"]

# 최종 결과를 담을 딕셔너리
final_response_to_frontend = {}

# ----------------------------------------------------
# 3. 백엔드 모듈 순차 실행 (지휘)
# ----------------------------------------------------
try:
    print("\n--- [메인 서버] 1. 기획서/트렌드 분석 시작 ---")
    
    # [호출 1] pdf_tools.py의 analyze_pdf 함수
    pdf_data = pdf_tools.analyze_pdf(PDF_FILE_PATH)
    final_response_to_frontend["analysis_summary"] = pdf_data
    if "error" in pdf_data:
        raise Exception(f"PDF 분석 실패: {pdf_data['error']}")
    
    # [호출 2] pdf_tools.py의 get_google_trends 함수
    trend_data = pdf_tools.get_google_trends(KEYWORDS)
    final_response_to_frontend["trend_summary"] = trend_data
    if "error" in trend_data:
        raise Exception(f"트렌드 분석 실패: {trend_data['error']}")
    
    # [호출 3] pdf_tools.py의 get_naver_buzzwords 함수
    # (대표 키워드로 Naver 버즈워드를 수집)
    naver_buzzwords = pdf_tools.get_naver_buzzwords(KEYWORDS[0])
    final_response_to_frontend["naver_buzzwords"] = naver_buzzwords
    print(f"    - Naver 버즈워드 수집: {naver_buzzwords[:3]}...")
    
    print("    ✅ 1. 분석 완료")


    print("\n--- [메인 서버] 2. 시각 트렌드 분석 시작 ---")
    
    # [호출 3] visual_analyzer.py의 analyze_visual_trends 함수
    visual_data = visual_analyzer.analyze_visual_trends(KEYWORDS[0]) # 대표 키워드로 검색
    final_response_to_frontend["visual_summary"] = visual_data
    print("    ✅ 2. 시각 분석 완료")
    
    
    print("\n--- [메인 서버] 3. 최종 카드뉴스 텍스트 생성 시작 ---")
    
    # 'cardnews_generator'에 전달할 재료 가공
    # (트렌드 결과에서 '키워드 리스트'만 추출)
    trend_keywords_list = trend_data.get("top_related_queries", {}).get(KEYWORDS[0], [])
    
    # [호출 4] cardnews_generator.py의 create_cardnews_text 함수
    cardnews_text_json = cardnews_generator.create_cardnews_text(
        USER_THEME, 
        pdf_data,                # PDF 요약본 (딕셔너리)
        trend_keywords_list,      # 트렌드 연관 키워드 (리스트)
        naver_buzzwords
    )
    final_response_to_frontend["cardnews_draft"] = cardnews_text_json
    if "error" in cardnews_text_json:
        raise Exception(f"카드뉴스 생성 실패: {cardnews_text_json['error']}")
        
    print("    ✅ 3. 카드뉴스 텍스트 생성 완료")

    # ----------------------------------------------------
    # 4. 프론트엔드에 보낼 '최종 종합 JSON' 생성
    # ----------------------------------------------------
    final_response_to_frontend["status"] = "success"

    print("\n--- ✅ [메인 서버] 모든 작업 완료! ---")
    print("--- 프론트엔드로 전송할 최종 종합 JSON 데이터 ---")
    
    # indent=2를 주면 JSON을 예쁘게 출력해 줍니다.
    print(json.dumps(final_response_to_frontend, indent=2, ensure_ascii=False))


except Exception as e:
    print(f"\n🚨 [메인 서버] 작업 중단! 심각한 오류 발생: {e}")
    # 프론트엔드에는 에러 상태를 JSON으로 보냅니다
    final_response_to_frontend["status"] = "error"
    final_response_to_frontend["message"] = str(e)
    print(json.dumps(final_response_to_frontend, indent=2, ensure_ascii=False))