# 필요한 라이브러리를 불러옵니다.
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_font_names_with_selenium():
    """
    Selenium을 사용해 JavaScript로 렌더링되는 Google Fonts 페이지를 크롤링합니다.
    """
    
    # 크롤링할 대상 URL
    url = "https://fonts.google.com/specimen/Noto+Sans+KR"
    
    # 1. WebDriver 설정
    # ChromeDriverManager가 우리 크롬 버전에 맞는 '조종기'를 자동으로 설치/관리해 줍니다.
    print("WebDriver(크롬 조종기)를 설정합니다...")
    service = Service(ChromeDriverManager().install())
    
    # 2. Selenium이 제어할 크롬 브라우저를 실행합니다.
    # (옵션: 'headless'는 브라우저 창을 눈에 보이지 않게 백그라운드에서 실행)
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # <- 창을 숨기고 싶으면 이 주석을 푸세요.
    options.add_argument('--log-level=3') # <- 불필요한 로그 메시지 숨기기
    
    driver = webdriver.Chrome(service=service, options=options)
    print(f"'{url}' 페이지에 접속을 시도합니다...")

    # ... (driver 설정 코드는 그대로 둠) ...
    
    # 찾으려는 '주소'(CSS 선택자)를 변수로 만듭니다.
    selector = "h1.specimen-header__title" #  하이픈(-)이 맞습니다!

    try:
        # 3. 브라우저로 URL에 접속합니다.
        driver.get(url)
        
        # 10초간 '스마트 대기'할 선택자를 'h1' (태그 이름)으로 변경합니다.
        target_selector = 'h1' 
        wait_time = 10
        
        print(f"페이지 로드를 {wait_time}초간 '스마트 대기'합니다... (대상: {target_selector})")
        
        wait = WebDriverWait(driver, wait_time)
        
        # EC.presence_of_element_located: 해당 요소가 DOM에 존재할 때까지 기다립니다.
        font_title_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, target_selector))
        )

        title_text = font_title_element.text
        print(f" 성공: 찾은 요소의 텍스트는 '{title_text}' 입니다.")

    except TimeoutException:
        # 10초를 기다렸지만 '주소'를 못 찾았을 때 발생하는 오류 
        print(f"오류: 10초를 기다렸지만 '{selector}' 요소를 찾지 못했습니다.")
        print("    웹사이트 구조가 변경되었을 수 있습니다.")

    except Exception as e:
        #  그 외의 모든 오류 (인터넷 끊김 등) 
        print(f" Selenium으로 크롤링 중 예기치 못한 오류 발생: {e}")

    finally:
        # 7. 작업이 끝나면 반드시 브라우저를 종료합니다.
        print("크롬 브라우저를 종료합니다.")
        driver.quit()

# --- [여기서부터 실제 코드 실행] ---
if __name__ == "__main__":
    get_font_names_with_selenium()