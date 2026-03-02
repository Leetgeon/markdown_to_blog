import streamlit as st
import google.generativeai as genai
import requests
import io
import urllib.parse

# 페이지 설정
st.set_page_config(
    page_title="Markdown to Blog AI Generator",
    page_icon="✍️",
    layout="wide"
)

# 사이드바 설정 (API 키 및 옵션)
text_model = None
image_model = None

with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("API 키가 저장되었습니다.")
        
        try:
            models = genai.list_models()
            avail_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
            if avail_models:
                # 1. 텍스트용 모델의 기본값 (가장 똑똑한 flash나 pro)
                text_default = 0
                for i, m in enumerate(avail_models):
                    if 'flash' in m.lower() and 'vision' not in m.lower():
                        text_default = i
                        break
                        
                # 2. 이미지 프롬프트용 모델의 기본값 (나노바나나)
                image_default = 0
                for i, m in enumerate(avail_models):
                    if 'nano-banana' in m.lower():
                        image_default = i
                        break
                        
                st.markdown("### 🤖 인공지능 모델 세팅")
                text_model = st.selectbox("📝 블로그 본문 작성 모델", avail_models, index=text_default, help="논리적이고 긴 글 작성에 유리한 모델을 골라주세요. (예: gemini-2.5-flash)")
                image_model = st.selectbox("🎨 섬네일 그림 전담 모델", avail_models, index=image_default, help="그림 묘사를 찰떡같이 잘 해내는 모델을 골라주세요. (예: nano-banana)")
                
        except Exception as e:
            st.error(f"모델 목록을 불러오지 못했습니다: {str(e)}")
    else:
        st.warning("Google Gemini API 키가 필요합니다.")
        
    st.markdown("---")
    st.markdown("### 타겟 플랫폼")
    st.info("현재 **네이버 블로그** 스타일에 최적화되어 작동합니다.")
    st.markdown("---")
    st.markdown("*Made with Streamlit & Gemini API*")

# 메인 UI
st.title("✍️ Markdown to Blog AI Generator")
st.markdown("난잡한 마크다운(.md) 메모나 대화 기록을, 잘 정돈되고 눈길을 끄는 **네이버 블로그 포스트**로 변환해보세요! (섬네일 이미지도 자동 생성됩니다)")

st.markdown("### 1. 소스 마크다운 업로드 또는 텍스트 입력")

tab1, tab2 = st.tabs(["파일 업로드", "텍스트 직접 입력"])

with tab1:
    uploaded_file = st.file_uploader("변환할 마크다운(.md) 파일을 선택하세요", type=["md", "txt"])
    md_text = ""
    if uploaded_file is not None:
        md_text = uploaded_file.getvalue().decode("utf-8")
        with st.expander("원본 내용 보기"):
            st.text(md_text)

with tab2:
    text_input = st.text_area("변환할 텍스트를 붙여넣으세요", height=200)

source_text = md_text if md_text else text_input

if st.button("🚀 블로그 포스트 자동 생성하기", type="primary"):
    if not api_key:
        st.error("좌측 사이드바에 Gemini API 키를 먼저 입력해주세요!")
    elif not source_text.strip():
        st.error("입력된 마크다운 내용이 없습니다. 파일을 업로드하거나 텍스트를 입력해주세요.")
    else:
        try:
            with st.spinner("✨ AI가 멋진 블로그 포스트를 작성하고 있습니다... (약 10~20초 소요)"):
                # 1. 블로그 본문 작성 프롬프트 (고도화된 글쓰기 룰 적용)
                system_prompt = """
                당신은 월 방문자 100만 명을 자랑하는 한국 최고의 스타 블로거이자 매력적인 스토리텔러입니다.
                다음 제공된 난잡한 마크다운 메모나 대화 기록을, 독자가 시간 가는 줄 모르고 읽게 만드는 최고의 네이버 블로그 포스트로 변환해 주세요.
                
                [매력적인 글쓰기를 위한 5가지 절대 규칙 (Rules)]
                
                1. 🪝 후킹과 호기심 유발 (The Hook)
                   - 글의 첫 문단은 무조건 독자의 시선을 사로잡는 강력한 후킹(Hook)으로 시작하세요.
                   - 진부한 인사말("안녕하세요, 여러분!")은 절대 금지합니다. 대신, 독자가 공감할 만한 질문, 도발적인 문장, 흥미로운 통계, 혹은 극적인 상황으로 포문을 여세요.
                
                2. 📖 스토리텔링 중심 (Storytelling)
                   - 단순한 정보나 사실의 나열이 아니라, '나' 또는 '우리'가 겪은 하나의 서사(기승전결)가 있는 이야기로 풀어주세요.
                   - 추상적인 표현 대신 오감을 자극하는 구체적인 묘사(예: "답답했다" 대신 "가슴에 큰 돌덩이를 얹은 것 같았다")를 사용하세요.
                
                3. 🌊 시각적 호흡과 리듬감 (Pacing & Formatting)
                   - 스마트폰으로 읽는 독자를 배려하여, 한 문단은 절대 3문장을 넘지 않도록 짧게 짧게끊어 쓰세요.
                   - 중간중간 적절한 인용구(>), 명확한 소제목(##), 글머리 기호(-), 굵은 글씨(**)를 혼합하여 글의 강약을 조절하세요.
                   - 상황에 꼭 맞는 이모지를 너무 과하지 않게, 감정을 표현하는 포인트로만 활용하세요.
                
                4. 🗣️ 감정적 공감과 대화체 (Conversational Tone)
                   - 인공지능이 쓴 딱딱한 글처럼 보이지 않도록, 친한 친구나 멘토가 카페에서 수다를 떨며 조언해주는 듯한 편안하고 진솔한 어투(~했어요, ~거든요, ~잖아요?)를 사용하세요.
                   - 글의 중간과 끝에 독자의 생각이나 경험을 묻는 질문을 섞어 소통을 유도하세요.
                
                5. 🏷️ 깔끔한 마무리 및 해시태그 (Ending & Tags)
                   - 글의 마지막은 핵심 메시지를 여운 있게 정리하며 긍정적인 행동을 촉구(Call to Action)하세요.
                   - 문서 맨 끝에는 본문 내용과 밀접한, 유입이 잘 될 만한 네이버 블로그 전용 해시태그 5~7개를 추가하세요. (#태그 형식)
                
                반드시 위 규칙들을 모두 지켜서, 독자가 끝까지 읽을 수밖에 없는 마력의 마크다운(.md) 형식 포스트를 작성하세요.
                """
                
                if not text_model or not image_model:
                    st.error("좌측 사이드바에서 블로그 본문과 섬네일 작성용 AI 모델을 모두 선택해주세요.")
                    st.stop()
                
                st.info(f"📝 블로그 글 작성: `{text_model}` / 🎨 썸네일 작성: `{image_model}`")
                
                model_text = genai.GenerativeModel(text_model)
                full_prompt = f"{system_prompt}\n\n[원본 내용]\n{source_text}"
                
                response = model_text.generate_content(full_prompt)
                blog_content = response.text
                
            with st.spinner("🎨 포스트에 어울리는 썸네일 텍스트를 구성하고 이미지를 합성 중입니다..."):
                # 2. 썸네일용 텍스트 추출 (주제목, 부제목, 키워드, 해시태그)
                thumbnail_prompt = f"""
                다음 블로그 글 내용을 바탕으로, 썸네일 이미지에 들어갈 4가지 텍스트를 추출하거나 작성해 주세요.
                각 항목은 반드시 제공된 형식에 맞춰서 1줄씩 출력하세요.
                
                형식:
                주제목: [메인 제목 (가급적 15자 이내, 필요시 \\n으로 줄바꿈 포함 가능)]
                부제목: [서브 제목 또는 핵심 내용 요약 (가급적 20자 이내)]
                키워드: [검색창에 들어갈 짧은 핵심 키워드 1개]
                해시태그: [관련 해시태그 3개 (예: #태그1 #태그2 #태그3)]
                
                [블로그 글]
                {blog_content[:1500]}
                """
                model_text_thumbnail = genai.GenerativeModel(text_model)
                prompt_response = model_text_thumbnail.generate_content(thumbnail_prompt)
                extracted_texts = prompt_response.text.strip()
                
                # 추출된 텍스트 파싱
                title = "블로그 포스트 제목"
                subtitle = "핵심 내용 요약"
                keyword = "검색 키워드"
                hashtags = "#태그"
                
                for line in extracted_texts.split('\n'):
                    line = line.strip().replace('**', '')
                    if line.startswith("주제목:"): title = line.replace("주제목:", "").strip().replace("\\n", "\n")
                    elif line.startswith("부제목:"): subtitle = line.replace("부제목:", "").strip()
                    elif line.startswith("키워드:"): keyword = line.replace("키워드:", "").strip()
                    elif line.startswith("해시태그:"): hashtags = line.replace("해시태그:", "").strip()
                
                # 세션 상태에 저장하여 UI에서 편집 가능하게 함
                st.session_state['blog_content'] = blog_content
                st.session_state['thumb_title'] = title
                st.session_state['thumb_subtitle'] = subtitle
                st.session_state['thumb_keyword'] = keyword
                st.session_state['thumb_hashtags'] = hashtags
                st.session_state['generation_done'] = True
                
            st.success("🎉 초안 생성이 완료되었습니다! 아래에서 썸네일 문구를 수정할 수 있습니다.")
            st.rerun()

        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg:
                st.error("🔑 입력하신 Gemini API 키가 유효하지 않습니다. 키를 잘못 복사하셨거나 아직 활성화되지 않은 키일 수 있습니다. 다시 확인해 주세요!")
            else:
                st.error(f"오류가 발생했습니다: {error_msg}")

from streamlit_drawable_canvas import st_canvas
import json
import base64

# ---------------------------------------------------------
# 결과 표시 및 썸네일 편집 UI (생성 완료 후 표시)
# ---------------------------------------------------------
if st.session_state.get('generation_done', False):
    st.markdown("---")
    st.header("🎨 썸네일 커스텀 편집")
    st.markdown("텍스트를 자유롭게 드래그해서 위치를 맞추거나 모양을 변경해보세요.")
    
    col_edit, col_preview = st.columns([1, 2.2])
    
    # 세션 상태에 초기값
    if 'coords' not in st.session_state:
        st.session_state['coords'] = {
            'title': (500, 400),
            'subtitle': (500, 650),
            'keyword': (500, 850),
            'hashtag': (950, 950)
        }
    if 'font_sizes' not in st.session_state:
        st.session_state['font_sizes'] = {
            'title': 60,
            'subtitle': 40,
            'keyword': 30,
            'hashtag': 35
        }
    if 'font_files' not in st.session_state:
        st.session_state['font_files'] = {
            'title': "C:/Windows/Fonts/malgun.ttf",
            'subtitle': "C:/Windows/Fonts/malgun.ttf",
            'keyword': "C:/Windows/Fonts/malgun.ttf",
            'hashtag': "C:/Windows/Fonts/malgun.ttf"
        }
    
    # 윈도우 기본 폰트 목록 예시
    font_options = {
        "맑은 고딕 (Malgun Gothic)": "C:/Windows/Fonts/malgun.ttf",
        "맑은 고딕 굵게 (Malgun Gothic Bold)": "C:/Windows/Fonts/malgunbd.ttf",
        "바탕 (Batang)": "C:/Windows/Fonts/batang.ttc",
        "돋움 (Dotum)": "C:/Windows/Fonts/gulim.ttc",
        "궁서 (Gungsuh)": "C:/Windows/Fonts/gungsuh.ttc",
    }
    
    with col_edit:
        st.subheader("텍스트 및 서체 수정")
        
        with st.expander("📌 주제목 설정", expanded=True):
            new_title = st.text_area("텍스트 (\\n 입력시 줄바꿈)", value=st.session_state['thumb_title'], height=60, key='txt_title')
            col1, col2 = st.columns(2)
            with col1:
                f_title = st.selectbox("주제목 글꼴", list(font_options.keys()), index=1)
                st.session_state['font_files']['title'] = font_options[f_title]
            with col2:
                st.session_state['font_sizes']['title'] = st.number_input("크기", value=st.session_state['font_sizes']['title'], step=2, key='sz_title')
                
        with st.expander("📌 부제목 설정", expanded=False):
            new_subtitle = st.text_area("텍스트", value=st.session_state['thumb_subtitle'], height=60, key='txt_sub')
            col1, col2 = st.columns(2)
            with col1:
                f_sub = st.selectbox("부제목 글꼴", list(font_options.keys()), index=0)
                st.session_state['font_files']['subtitle'] = font_options[f_sub]
            with col2:
                st.session_state['font_sizes']['subtitle'] = st.number_input("크기 ", value=st.session_state['font_sizes']['subtitle'], step=2, key='sz_sub')
                
        with st.expander("📌 키워드 설정", expanded=False):
            new_keyword = st.text_input("텍스트", value=st.session_state['thumb_keyword'], key='txt_key')
            col1, col2 = st.columns(2)
            with col1:
                f_key = st.selectbox("키워드 글꼴", list(font_options.keys()), index=0)
                st.session_state['font_files']['keyword'] = font_options[f_key]
            with col2:
                st.session_state['font_sizes']['keyword'] = st.number_input("크기  ", value=st.session_state['font_sizes']['keyword'], step=2, key='sz_key')
                
        with st.expander("📌 해시태그 설정", expanded=False):
            new_hashtags = st.text_input("텍스트 ", value=st.session_state['thumb_hashtags'], key='txt_hash')
            col1, col2 = st.columns(2)
            with col1:
                f_hash = st.selectbox("해시태그 글꼴", list(font_options.keys()), index=0)
                st.session_state['font_files']['hashtag'] = font_options[f_hash]
            with col2:
                st.session_state['font_sizes']['hashtag'] = st.number_input("크기   ", value=st.session_state['font_sizes']['hashtag'], step=2, key='sz_hash')

        st.info("우측 캔버스에서 텍스트 위를 마우스로 드래그하여 자유롭게 이동하세요!")

    with col_preview:
        st.subheader("마우스 드래그 썸네일")
        
        import os
        import sys
        import importlib
        
        if 'thumbnail_maker' in sys.modules:
            importlib.reload(sys.modules['thumbnail_maker'])
        else:
            import thumbnail_maker
            
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "template.png")
        output_path = os.path.join(base_dir, "output_thumbnail.png")
        
        # 1000x1000 인 원본 템플릿을 화면 크기에 맞게 800x800으로 약간 축소 (기존 500보단 훨씬 큼)
        canvas_size = 800
        scale_ratio = 1000 / canvas_size
        
        # 캔버스에 그릴 초기 객체 설정 (텍스트박스)
        # 드로어블 캔버스는 초기 상태를 JSON 문자열로 받을 수 있음
        initial_drawing = {
            "version": "4.4.0",
            "objects": [
                {
                    "type": "i-text",
                    "version": "4.4.0",
                    "originX": "center",
                    "originY": "center",
                    "left": st.session_state['coords']['title'][0] / scale_ratio,
                    "top": st.session_state['coords']['title'][1] / scale_ratio,
                    "width": 600,
                    "height": 100,
                    "fill": "rgba(50, 50, 50, 1)",
                    "text": new_title,
                    "fontSize": st.session_state['font_sizes']['title'] / scale_ratio,
                    "fontFamily": "sans-serif",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "id": "title_text"
                },
                {
                    "type": "i-text",
                    "version": "4.4.0",
                    "originX": "center",
                    "originY": "center",
                    "left": st.session_state['coords']['subtitle'][0] / scale_ratio,
                    "top": st.session_state['coords']['subtitle'][1] / scale_ratio,
                    "width": 600,
                    "height": 50,
                    "fill": "rgba(100, 100, 100, 1)",
                    "text": new_subtitle,
                    "fontSize": st.session_state['font_sizes']['subtitle'] / scale_ratio,
                    "fontFamily": "sans-serif",
                    "textAlign": "center",
                    "id": "subtitle_text"
                },
                {
                    "type": "i-text",
                    "version": "4.4.0",
                    "originX": "center",
                    "originY": "center",
                    "left": st.session_state['coords']['keyword'][0] / scale_ratio,
                    "top": st.session_state['coords']['keyword'][1] / scale_ratio,
                    "width": 400,
                    "height": 50,
                    "fill": "rgba(150, 150, 150, 1)",
                    "text": new_keyword,
                    "fontSize": st.session_state['font_sizes']['keyword'] / scale_ratio,
                    "fontFamily": "sans-serif",
                    "textAlign": "center",
                    "id": "keyword_text"
                },
                {
                    "type": "i-text",
                    "version": "4.4.0",
                    "originX": "right",
                    "originY": "center",
                    "left": st.session_state['coords']['hashtag'][0] / scale_ratio,
                    "top": st.session_state['coords']['hashtag'][1] / scale_ratio,
                    "width": 400,
                    "height": 50,
                    "fill": "rgba(230, 80, 120, 1)",
                    "text": new_hashtags,
                    "fontSize": st.session_state['font_sizes']['hashtag'] / scale_ratio,
                    "fontFamily": "sans-serif",
                    "fontWeight": "bold",
                    "textAlign": "right",
                    "id": "hashtag_text"
                }
            ]
        }
        from PIL import Image
        bg_image = Image.open(template_path)

        # Drawable Canvas 렌더링 (드래그, 리사이징 가능)
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            background_image=bg_image,
            update_streamlit=True,
            height=canvas_size, # 화면 공간 절약을 위해 축소 표시
            width=canvas_size,
            drawing_mode="transform",
            initial_drawing=initial_drawing,
            key="thumb_canvas",
        )
            
        # 캔버스에서 변경된 좌표 가져와서 원본 해상도(x2)에 맞게 백엔드 이미지 생성
        if canvas_result.json_data is not None:
            objects = canvas_result.json_data["objects"]
            for obj in objects:
                # 캔버스상 축소된 좌표를 다시 원래 해상도로 확대
                new_x = int(obj["left"] * scale_ratio)
                new_y = int(obj["top"] * scale_ratio)
                
                if obj.get("id") == "title_text": st.session_state['coords']['title'] = (new_x, new_y)
                elif obj.get("id") == "subtitle_text": st.session_state['coords']['subtitle'] = (new_x, new_y)
                elif obj.get("id") == "keyword_text": st.session_state['coords']['keyword'] = (new_x, new_y)
                elif obj.get("id") == "hashtag_text": st.session_state['coords']['hashtag'] = (new_x, new_y)

        # 백엔드에 고해상도 최종 이미지 렌더링 저장
        windows_font = "C:/Windows/Fonts/malgun.ttf"
        result_path = sys.modules['thumbnail_maker'].create_thumbnail(
             template_path=template_path,
             output_path=output_path,
             font_path=windows_font, # 여기서 누락되었던 파라미터 추가
             title=new_title,
             subtitle=new_subtitle,
             keyword=new_keyword,
             hashtags=new_hashtags,
             coords=st.session_state['coords'],
             fonts=st.session_state['font_files'],
             sizes=st.session_state['font_sizes']
        )
        
        if result_path and os.path.exists(result_path):
             with open(output_path, "rb") as file:
                 st.download_button(
                     label="📥 최종 썸네일 고화질 저장",
                     data=file,
                     file_name="thumbnail.png",
                     mime="image/png",
                     type="primary",
                     use_container_width=True
                 )

    st.markdown("---")
    st.header("📝 완성된 블로그 포스트 (네이버 블로그 복사 최적화)")
    
    # 네이버 블로그 복사용 최적화 렌더링 (흰색 배경, 검정 글씨 강제, 썸네일 포함)
    safe_content = st.session_state['blog_content'].replace('\n', '<br>')
    
    # 썸네일 이미지를 Base64로 인코딩하여 HTML에 포함
    img_html = ""
    if os.path.exists(output_path):
        with open(output_path, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read()).decode("utf-8")
            # 네이버 블로그 가로폭 최적화 (보통 800~900px 내외)
            img_html = f'<div style="text-align: center; margin-bottom: 30px;"><img src="data:image/png;base64,{b64_string}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" alt="썸네일 이미지"></div>'
    
    html_content = f'<div style="background-color: #FFFFFF; color: #000000; padding: 30px; border-radius: 10px; border: 1px solid #E0E0E0; font-family: \'Malgun Gothic\', \'Apple SD Gothic Neo\', sans-serif; line-height: 1.8; font-size: 16px;">{img_html}{safe_content}</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("💾 본문 파일로 다운로드")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📝 마크다운(.md) 파일로 다운로드",
            data=st.session_state['blog_content'],
            file_name="blog_post.md",
            mime="text/markdown"
        )
    with col2:
        st.info("👆 위 네이버 블로그 전용 박스 안의 텍스트를 드래그해서 네이버 블로그 글쓰기 창에 바로 붙여넣으세요! (배경 흰색 고정)")
