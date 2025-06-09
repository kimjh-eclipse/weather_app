import requests
from dotenv import load_dotenv
import os
from datetime import datetime
from googletrans import Translator
import tkinter as tk
from tkinter import ttk
import threading

class WeatherApp:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    def get_weather(self, city_name):
        """도시의 날씨 정보를 가져옵니다."""
        # 도시명을 영어로 변환
        translator = Translator()
        try:
            translated_city = translator.translate(city_name, dest='en').text
        except Exception as e:
            return f"도시명 변환 중 에러 발생: {str(e)}"

        params = {
            'q': translated_city,
            'appid': self.api_key,
            'units': 'metric',  # 섭씨 온도로 표시
            'lang': 'kr'  # 한국어로 표시
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                weather = {
                    '도시': data['name'],
                    '온도': f"{data['main']['temp']}°C",
                    '날씨': data['weather'][0]['description'],
                    '습도': f"{data['main']['humidity']}%",
                    '풍속': f"{data['wind']['speed']} m/s"
                }
                return weather
            else:
                return f"날씨 정보를 가져오는데 실패했습니다: {data['message']}"
                
        except Exception as e:
            return f"에러 발생: {str(e)}"

class WeatherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("날씨 정보 조회")
        self.root.geometry("400x300")
        
        # 도시명 입력 프레임
        input_frame = ttk.Frame(root, padding="10")
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="도시명 입력:").pack(side=tk.LEFT)
        self.city_entry = ttk.Entry(input_frame)
        self.city_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 엔터 키 이벤트 처리
        def on_enter(event):
            self.get_weather()
            return "break"
            
        self.city_entry.bind('<Return>', on_enter)
        
        # 확인 버튼
        ttk.Button(input_frame, text="확인", command=self.get_weather).pack(side=tk.LEFT)
        
        # 상태 표시 레이블
        self.status_label = ttk.Label(root, text="")
        self.status_label.pack(pady=5)
        
        # 프로그레스바
        self.progress = ttk.Progressbar(root, mode='determinate', maximum=100)
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        
        # 결과 표시 프레임
        self.result_frame = ttk.Frame(root, padding="10")
        self.result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 스크롤바가 있는 텍스트 위젯
        self.text_widget = tk.Text(self.result_frame, height=10, width=40)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.result_frame, command=self.text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(yscrollcommand=scrollbar.set)
        
        # 날씨 앱 인스턴스 생성
        self.weather_app = WeatherApp()
        
    def update_ui(self, result, error=None):
        """UI를 업데이트합니다."""
        self.text_widget.delete(1.0, tk.END)
        
        if error:
            self.text_widget.insert(tk.END, f"에러: {error}")
            self.status_label.config(text="에러 발생")
        else:
            if isinstance(result, dict):
                self.text_widget.insert(tk.END, "현재 날씨 정보:\n\n")
                for key, value in result.items():
                    self.text_widget.insert(tk.END, f"{key}: {value}\n")
                self.status_label.config(text="날씨 정보 조회 완료")
            else:
                self.text_widget.insert(tk.END, f"에러: {result}")
                self.status_label.config(text="에러 발생")
                
        # 진행 상태 표시 종료
        self.progress.stop()
        self.progress['value'] = 100

    def get_weather(self):
        """날시 정보를 가져와 텍스트 위젯에 표시합니다."""
        city = self.city_entry.get()
        if not city:
            return
            
        # 진행 상태 표시 시작
        self.status_label.config(text="날씨 정보를 조회 중입니다...")
        self.progress.start()
        
        # 새로운 스레드에서 날씨 정보를 가져옵니다
        def fetch_weather():
            try:
                result = self.weather_app.get_weather(city)
                self.root.after(0, lambda: self.update_ui(result))
            except Exception as e:
                self.root.after(0, lambda: self.update_ui(None, str(e)))
                
        threading.Thread(target=fetch_weather, daemon=True).start()

def main():
    root = tk.Tk()
    app = WeatherGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
