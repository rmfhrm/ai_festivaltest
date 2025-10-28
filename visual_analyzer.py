# 시각 트렌드 분석

# visual_analyzer.py

import requests
from colorthief import ColorThief
import io  # 이미지를 파일이 아닌 '메모리'에서 처리하기 위해 필요합니다.

# --- (1. 크롤링을 시뮬레이션할 테스트용 이미지 URL 리스트) ---
# (나중에 이 리스트를 '진짜 크롤링' 결과물로 교체할 겁니다)
SAMPLE_IMAGE_URLS = [
    # 1. 따뜻한 베이지/갈색 톤의 실내 이미지
    "https://images.pexels.com/photos/271816/pexels-photo-271816.jpeg",
    # 2. 파란색/녹색 톤의 자연(폭포) 이미지
    "https://images.pexels.com/photos/3225517/pexels-photo-3225517.jpeg",
    # 3. 강렬한 붉은색/검은색 톤의 도시(네온) 이미지
    "https://images.pexels.com/photos/1654498/pexels-photo-1654498.jpeg"
]

def get_dominant_colors(image_urls):
    """
    이미지 URL 리스트를 받아서, 각 이미지의 '주요 색상'을
    HEX 코드(예: '#FF0000') 리스트로 반환합니다.
    """
    print("  [get_dominant_colors] 이미지 URL에서 색상 추출 시작...")
    palette = []
    
    for url in image_urls:
        try:
            # 1. 'requests'로 이미지 데이터를 인터넷에서 다운로드
            print(f"    - 다운로드 중: {url[:50]}...")
            response = requests.get(url, timeout=10) # 10초 이상 걸리면 중단
            response.raise_for_status() # HTTP 오류(404 등)가 있으면 예외 발생
            
            # 2. 다운로드한 데이터를 '파일'처럼 메모리에 임시 저장
            image_data_io = io.BytesIO(response.content)
            
            # 3. 'ColorThief'로 메모리에 있는 이미지 데이터 분석
            color_thief = ColorThief(image_data_io)
            
            # 4. 이미지의 '주요 색상' 1개를 (R, G, B) 튜플로 가져오기
            dominant_color_rgb = color_thief.get_color(quality=1)
            
            # 5. (R, G, B) 튜플을 '#RRGGBB' HEX 코드 문자열로 변환
            hex_color = f"#{dominant_color_rgb[0]:02x}{dominant_color_rgb[1]:02x}{dominant_color_rgb[2]:02x}"
            palette.append(hex_color)
            
            print(f"    분석 성공. 주요 색상: {hex_color}")
            
        except Exception as e:
            print(f"    분석 실패: {url[:50]}... (오류: {e})")
            
    # 중복된 색상을 제거하고 리스트로 반환
    return list(set(palette))

def analyze_visual_trends(keyword):
    """
    [메인 함수] 키워드를 받아 시각 트렌드(색상 등)를 분석합니다.
    """
    print(f"\n--- [시각 분석 모듈] '{keyword}' 분석 시작 ---")
    
    # ----------------------------------------------------
    # TODO: (미래 과제) 
    # 여기에 'requests'와 'BeautifulSoup4' (또는 Selenium)를 사용해서
    # 'keyword'로 Behance/Pinterest를 '진짜' 크롤링하고,
    # image_urls_to_analyze 리스트를 채우는 코드가 들어가야 함.
    print("  1. (시뮬레이션) 트렌디한 이미지 URL 수집...")
    image_urls_to_analyze = SAMPLE_IMAGE_URLS # 지금은 샘플 URL 사용
    # ----------------------------------------------------
    
    print("  2. 수집된 이미지에서 주요 색상 추출...")
    dominant_colors = get_dominant_colors(image_urls_to_analyze)
    
    print(f"--- [시각 분석 모듈] 분석 완료 ---")
    
    # 이 모듈의 최종 결과물 (JSON으로 변환될 딕셔너리)
    return {
        "analyzed_keyword": keyword,
        "recommended_colors": dominant_colors,
        "source_image_urls": image_urls_to_analyze
    }

# --- (3. 이 파일 자체를 테스트하기 위한 실행 코드) ---
# (다른 파일에서 'import'할 때는 이 부분은 실행되지 않습니다)
if __name__ == "__main__":
    
    print("--- 'visual_analyzer.py' 파일 단독 테스트 실행 ---")
    
    # '담양 산타 축제' 키워드가 들어왔다고 가정
    test_keyword = "담양 산타 축제" 
    
    visual_data = analyze_visual_trends(test_keyword)
    
    print("\n--- [최종 반환 데이터 (딕셔너리)] ---")
    print(visual_data)