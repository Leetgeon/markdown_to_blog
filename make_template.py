from PIL import Image, ImageDraw, ImageFont
import os

def create_base_template(output_path):
    # 크기 설정
    width, height = 1000, 1000
    
    # 1. 흰색 배경 생성 (RGBA)
    img = Image.new('RGBA', (width, height), color=(255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 2. 노란색 두꺼운 외부 테두리 (예시 이미지 참고: 꽉 찬 밝은 노란색/주황색)
    border_color = (250, 190, 50) 
    border_width = 18
    draw.rectangle([(0, 0), (width, height)], outline=border_color, width=border_width)

    # 3. 브라우저 윗부분 (연한 회색 배경)
    header_height = 140
    # 머리 부분 사각형
    draw.rectangle([(border_width, border_width), (width - border_width, header_height)], fill=(245, 245, 245))
    
    # 구분선 (하단 그림자 느낌)
    draw.line([(border_width, header_height), (width - border_width, header_height)], fill=(220, 220, 220), width=2)
    draw.line([(border_width, 85), (width - border_width, 85)], fill=(220, 220, 220), width=1)

    # 4. 브라우저 버튼 3개 (빨강, 노랑, 초록)
    btn_y = 52
    btn_radius = 8
    draw.ellipse([(45, btn_y-btn_radius), (45+btn_radius*2, btn_y+btn_radius)], fill=(255, 95, 86))
    draw.ellipse([(75, btn_y-btn_radius), (75+btn_radius*2, btn_y+btn_radius)], fill=(255, 189, 46))
    draw.ellipse([(105, btn_y-btn_radius), (105+btn_radius*2, btn_y+btn_radius)], fill=(39, 201, 63))

    # 5. Naver Blog 로고 & 텍스트 (간략화 표현)
    # 폰트 로드 시도 (없으면 기본)
    font_path = "C:/Windows/Fonts/malgun.ttf"
    try:
        font_logo = ImageFont.truetype(font_path, 20)
        font_url = ImageFont.truetype(font_path, 20)
    except IOError:
        font_logo = ImageFont.load_default()
        font_url = ImageFont.load_default()

    # 초록색 N 원형 로고 모방
    n_x, n_y = 155, 52
    n_radius = 16
    draw.ellipse([(n_x-n_radius, n_y-n_radius), (n_x+n_radius, n_y+n_radius)], fill=(3, 199, 90))
    draw.text((n_x, n_y), "N", font=font_logo, fill=(255, 255, 255), anchor="mm")
    
    # 텍스트
    draw.text((180, 52), "Naver Blog", font=font_logo, fill=(50, 50, 50), anchor="lm")
    
    # 회색 플러스 아이콘
    draw.text((370, 52), "+", font=font_logo, fill=(150, 150, 150), anchor="lm")
    draw.line([(395, 30), (395, 75)], fill=(220, 220, 220), width=1)
    
    # 화살표 아이콘 (좌, 우, 새로고침)
    draw.text((70, 112), "<  >  C", font=font_url, fill=(180, 180, 180), anchor="lm")

    # 6. URL 입력창 (둥근 모서리)
    url_box_x1, url_box_y1 = 210, 95
    url_box_x2, url_box_y2 = 940, 130
    draw.rounded_rectangle([(url_box_x1, url_box_y1), (url_box_x2, url_box_y2)], radius=15, fill=(255, 255, 255), outline=(230, 230, 230))
    
    # 별표 (우측 끝)
    draw.text((900, 112), "☆", font=font_url, fill=(250, 190, 50), anchor="mm")
    draw.text((230, 112), "https://blog.naver.com/miritoday", font=font_url, fill=(100, 100, 100), anchor="lm")
    
    # V 꺾쇠 아이콘 (맨 우측 상단)
    draw.text((950, 52), "V", font=font_url, fill=(180, 180, 180), anchor="mm")

    # 7. 하단 검색창 (모서리 둥근 회색 박스)
    # 키워드가 들어갈 자리 배경
    search_width, search_height = 540, 60
    search_x = 500
    search_y = 850
    draw.rounded_rectangle([
        (search_x - search_width//2, search_y - search_height//2),
        (search_x + search_width//2, search_y + search_height//2)
    ], radius=30, fill=(245, 245, 245), outline=(230, 230, 230))
    
    # 왼쪽 노란 플러스 원
    plus_r = 25
    plus_x = search_x - search_width//2
    draw.ellipse([(plus_x-plus_r, search_y-plus_r), (plus_x+plus_r, search_y+plus_r)], fill=(250, 210, 80))
    draw.text((plus_x, search_y), "+", font=font_logo, fill=(255, 255, 255), anchor="mm")
    
    # 우측 돋보기 모양 (Q 처럼 그림)
    mag_x = search_x + search_width//2 - 30
    draw.text((mag_x, search_y), "Q", font=font_logo, fill=(150, 150, 150), anchor="mm")

    # 결과물 저장
    final_img = img.convert("RGB")
    final_img.save(output_path)
    print(f"템플릿을 생성했습니다: {output_path}")

if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.png")
    create_base_template(output_path)
