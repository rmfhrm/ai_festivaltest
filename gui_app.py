import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import pdf_tools  # 1. 우리의 '엔진' 파일을 import
from dotenv import load_dotenv

# --- .env 파일 로드 (API 키 때문에) ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    messagebox.showerror("오류", ".env 파일에서 OPENAI_API_KEY를 찾을 수 없습니다.")
    exit()

# --- 전역 변수 (선택된 파일 경로 저장용) ---
selected_file_path = ""

# --- 2. "분석 시작" 버튼을 눌렀을 때 실행될 함수 ---
def start_analysis():
    global selected_file_path
    
    print("--- 1. '분석 시작' 버튼 클릭됨 ---")
    
    # (1) GUI에서 사용자 입력값 가져오기
    user_title = entry_title.get()
    user_theme = entry_theme.get("1.0", tk.END).strip() # Text 위젯에서 가져오기
    user_keywords_str = entry_keywords.get()
    
    # (2) 입력값 검증
    if not user_title or not user_theme or not user_keywords_str:
        messagebox.showwarning("입력 오류", "제목, 테마, 키워드를 모두 입력해야 합니다.")
        return
        
    if not selected_file_path:
        messagebox.showwarning("파일 오류", "기획서 파일을 선택해야 합니다.")
        return
        
    # (3) 키워드를 리스트로 변환
    user_keywords_list = [k.strip() for k in user_keywords_str.split(',')]
    
    print(f"    - 제목: {user_title}")
    print(f"    - 테마: {user_theme[:20]}...")
    print(f"    - 키워드: {user_keywords_list}")
    print(f"    - 파일: {selected_file_path}")
    
    # (4) 결과창 비우기 및 '분석 중' 메시지 표시
    result_text.delete('1.0', tk.END)
    result_text.insert(tk.END, f"'{os.path.basename(selected_file_path)}' 파일 분석 중...\n\n(AI가 응답할 때까지 1~2분 정도 걸릴 수 있습니다...)")
    root.update_idletasks() # 화면 즉시 새로고침

    try:
        # (5)'pdf_tools 호출
        pdf_analysis_result = pdf_tools.analyze_pdf(selected_file_path)

        if "error" in pdf_analysis_result:
            raise Exception(pdf_analysis_result['error'])

        # (6) 최종 보고서 조합
        final_report = {
            "analysis_summary": pdf_analysis_result,
            "user_inputs": {
                "title": user_title,
                "theme": user_theme,
                "keywords": user_keywords_list
            }
        }
        
        # (7) 결과창에 최종 JSON 출력
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, json.dumps(final_report, indent=2, ensure_ascii=False))
        
    except Exception as e:
        # (8) 오류 발생 시 결과창에 오류 메시지 출력
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, f"--- 분석 실패 ---\n\n오류: {e}")

# --- 1. "파일 선택" 버튼을 눌렀을 때 실행될 함수 ---
def select_file():
    global selected_file_path
    
    # (파일 선택 대화상자 열기)
    filetypes = (
        ('모든 기획서 파일', '*.pdf *.docx *.hwp'),
        ('PDF 파일', '*.pdf'),
        ('Word 파일', '*.docx'),
        ('한글 파일', '*.hwp'),
        ('모든 파일', '*.*')
    )
    
    file_path = filedialog.askopenfilename(
        title='분석할 기획서 파일을 선택하세요',
        filetypes=filetypes
    )
    
    if file_path:
        selected_file_path = file_path
        # (선택된 파일 이름을 라벨에 표시)
        file_label.config(text=f"선택된 파일: {os.path.basename(file_path)}")
        print(f"--- 파일 선택됨: {file_path} ---")

# --- 3. GUI 윈도우 생성 ---
root = tk.Tk()
root.title("FestGen AI : 기획서 분석기 v1.0")
root.geometry("700x800") # 창 크기

# (프레임: 입력 영역)
input_frame = ttk.Frame(root, padding="10")
input_frame.pack(fill='x')

# (1) 제목 입력
ttk.Label(input_frame, text="축제 제목:").pack(anchor='w', padx=5)
entry_title = ttk.Entry(input_frame)
entry_title.pack(fill='x', padx=5, pady=2)

# (2) 테마(기획의도) 입력 (여러 줄)
ttk.Label(input_frame, text="테마/기획의도:").pack(anchor='w', padx=5, pady=(10, 0))
entry_theme = tk.Text(input_frame, height=5, width=60)
entry_theme.pack(fill='x', padx=5, pady=2)

# (3) 키워드 입력
ttk.Label(input_frame, text="핵심 키워드 (콤마,로 구분):").pack(anchor='w', padx=5, pady=(10, 0))
entry_keywords = ttk.Entry(input_frame)
entry_keywords.pack(fill='x', padx=5, pady=2)

# (4) 파일 선택 버튼(끌어오기 대체)
file_frame = ttk.Frame(input_frame)
file_frame.pack(fill='x', pady=(15, 5))

btn_select_file = ttk.Button(file_frame, text="기획서 파일 선택 (.pdf, .docx, .hwp)", command=select_file)
btn_select_file.pack(side='left', padx=5)

file_label = ttk.Label(file_frame, text="파일이 선택되지 않았습니다.", foreground="grey")
file_label.pack(side='left', padx=10)

# (5) 분석 시작 버튼
btn_start = ttk.Button(root, text="기획서 분석 시작", command=start_analysis)
btn_start.pack(fill='x', padx=15, pady=10)

# (프레임: 결과 영역)
result_frame = ttk.Frame(root, padding="10")
result_frame.pack(fill='both', expand=True)

ttk.Label(result_frame, text="--- 분석 결과 (JSON) ---").pack(anchor='w')

# (6) 결과 출력창 (스크롤 가능)
result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, width=80, height=25)
result_text.pack(fill='both', expand=True)

# (윈도우 실행)
root.mainloop()