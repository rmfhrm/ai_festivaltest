import json
import os
import pdf_tools
from dotenv import load_dotenv # 2. 

# --- .env 파일 로드 ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print(" 오류: .env 파일에서 OPENAI_API_KEY를 찾을 수 없습니다.")
    exit()

# --- 1. (입력) 사용자가 직접 입력한 값 ---
print("--- ACC AI : 기획서 분석 ---")
user_theme_input = input("1. 축제 기획 의도(테마)를 입력하세요")
user_keywords_input = ["2. 핵심 키워드를 콤마(,)로 구분해 입력하세요 (예: 꽃, 쉼, 열정): "]
pdf_file_name = input("3. 분석할 기획서 파일명을 입력하세요 (예: sample_plan.pdf): ")


# --- 2. (입력) 분석할 PDF 파일 경로 ---
script_dir = os.path.dirname(os.path.abspath(__file__))
pdf_file_path = os.path.join(script_dir, pdf_file_path) 

print("--- 1. '기획서 분석'을 시작합니다... ---")
pdf_analysis_result = pdf_tools.analyze_pdf(pdf_file_path)

if "error" in pdf_analysis_result:
    print(f"분석 실패: {pdf_analysis_result['error']}")
else:
    print("--- '기획서 분석' 완료 ---")

    # --- 4. (출력) 사용자님이 원하신 최종 결과물 ---
    # (분석 결과와 입력값을 하나의 JSON으로 합치기)
    final_report = {
        # (1) 기획서 분석 결과
        "analysis_summary": pdf_analysis_result,
        
        # (2) 기획의도와 키워드 넣은 것
        "user_inputs": {
            "theme": user_theme_input,
            "keywords": user_keywords_input
        }
    }
    
    print("\n--- [결과: 기획서 분석 + 사용자 입력값] ---")
    print(json.dumps(final_report, indent=2, ensure_ascii=False))