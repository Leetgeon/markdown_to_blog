from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

def create_thumbnail(
    template_path: str,
    output_path: str,
    font_path: str,
    title: str,
    subtitle: str,
    keyword: str,
    hashtags: str,
    coords: dict = None,
    fonts: dict = None,
    sizes: dict = None
):
    """
    빈 썸네일 템플릿에 4가지 텍스트를 합성하여 새로운 이미지를 생성합니다.
    """
    if not coords:
        coords = {
            'title': (500, 400),
            'subtitle': (500, 650),
            'keyword': (500, 850),
            'hashtag': (950, 950)
        }
    if not fonts:
        fonts = {k: font_path for k in coords.keys()}
    if not sizes:
        sizes = {'title': 60, 'subtitle': 40, 'keyword': 30, 'hashtag': 35}
        
    try:
        img = Image.open(template_path).convert("RGBA")
    except FileNotFoundError:
        print(f"템플릿을 찾을 수 없어 임시 배경을 생성합니다: {template_path}")
        img = Image.new('RGBA', (1000, 1000), color=(255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([(20, 20), (980, 980)], outline=(245, 195, 60), width=30)
        draw.rectangle([(20, 20), (980, 100)], fill=(240, 240, 240))
        
    draw = ImageDraw.Draw(img)

    def get_font(key):
        try:
            return ImageFont.truetype(fonts[key], sizes[key])
        except IOError:
            return ImageFont.load_default()

    # (1) 주제목
    wrapped_title = textwrap.fill(title, width=16)
    draw.multiline_text(
        coords['title'],
        wrapped_title,
        font=get_font('title'),
        fill=(50, 50, 50),
        align="center",
        spacing=20,
        anchor="mm"
    )

    # (2) 부제목
    wrapped_subtitle = textwrap.fill(subtitle, width=22)
    draw.multiline_text(
        coords['subtitle'],
        wrapped_subtitle,
        font=get_font('subtitle'),
        fill=(100, 100, 100),
        align="center",
        spacing=15,
        anchor="mm"
    )

    # (3) 검색창 키워드
    draw.text(
        coords['keyword'],
        keyword,
        font=get_font('keyword'),
        fill=(150, 150, 150),
        anchor="mm"
    )

    # (4) 해시태그
    draw.text(
        coords['hashtag'],
        hashtags,
        font=get_font('hashtag'),
        fill=(230, 80, 120),
        anchor="rm"
    )

    output_img = img.convert("RGB")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    output_img.save(output_path)
    return output_path
