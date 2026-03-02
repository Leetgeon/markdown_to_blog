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
                   - **[이모지/특수기호 엄격 제한 규정]**
                     1. **글의 제목(H1) 및 모든 소제목(H2, H3 등)에는 이모지를 절대 사용하지 마세요.** (예: "## 🚀 서론" -> 금지, "## 서론" -> 허용)
                     2. 본문 전체를 통틀어 이모지는 최대 1~2개까지만 사용을 허용합니다.
                     3. 기계적이고 인위적인 감탄사(🎉, 💡, ✨, 💖 등)는 AI가 쓴 글이라는 확신을 주므로 완전히 배제하세요.
                
                4. 🗣️ 감정적 공감과 대화체 (Conversational Tone)
                   - 인공지능 특유의 딱딱하거나 과하게 친절한 톤을 빼주세요. 실제 블로거가 카페에서 친구에게 이야기하듯 아주 자연스럽고 사람 냄새 나는 솔직한 어투(~했어요, ~거든요, ~잖아요?)를 사용하세요.
                   - 글의 중간과 끝에 독자의 생각이나 경험을 묻는 질문을 섞어 소통을 유도하세요.
                
                5. 🏷️ 깔끔한 마무리 및 해시태그 (Ending & Tags)
                   - 본문 작성을 마무리한 다음엔 반드시 아래의 위트 있는 고정 멘트를 추가하여 독자의 참여를 자연스럽게 유도해 주세요.
                     "끝까지 읽어주셔서 감사합니다! 여러분의 따뜻한 공감(❤️)과 댓글, 그리고 양 옆의 광고 클릭 한 번은 다음 포스팅을 준비하는 저에게 엄청난 힘이 된답니다 😘"
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
    # 배포(Linux) 환경에서도 안전하게 렌더링되도록 프로젝트 내장 폰트 사용
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_font = os.path.join(base_dir, "fonts", "NanumGothic.ttf")
    
    if 'font_files' not in st.session_state:
        st.session_state['font_files'] = {
            'title': default_font,
            'subtitle': default_font,
            'keyword': default_font,
            'hashtag': default_font
        }
    
    font_options = {
        "나눔고딕 (Nanum Gothic)": default_font
    }
    
    with col_edit:
        st.subheader("텍스트 및 서체 수정")
        
        with st.expander("📌 주제목 설정", expanded=True):
            new_title = st.text_area("텍스트 (\\n 입력시 줄바꿈)", value=st.session_state['thumb_title'], height=60, key='txt_title')
            col1, col2 = st.columns(2)
            with col1:
                f_title = st.selectbox("주제목 글꼴", list(font_options.keys()), index=0)
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
        # st_canvas가 Streamlit Cloud 환경에서 원본(1000x1000)을 전송할 때 백지화되는 WebSocket 데이터 한계 버그 방지
        # 캔버스 크기에 딱 맞춰 resize 하여 가벼운 상태로 넘겨줌
        bg_image = Image.open(template_path).resize((canvas_size, canvas_size))

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
        result_path = sys.modules['thumbnail_maker'].create_thumbnail(
             template_path=template_path,
             output_path=output_path,
             font_path=default_font, # 누락 파라미터 방지용 기본값
             title=new_title,
             subtitle=new_subtitle,
             keyword=new_keyword,
             hashtags=new_hashtags,
             coords=st.session_state['coords'],
             fonts=st.session_state['font_files'],
             sizes=st.session_state['font_sizes']
        )
        
        if result_path and os.path.exists(result_path):
             st.markdown("### 📸 최종 완성된 썸네일")
             st.markdown("👇 아래 이미지를 **[마우스 우클릭] -> [이미지 복사]** 하신 후 네이버 블로그에 바로 붙여넣기(Ctrl+V) 하셔도 됩니다!")
             st.image(output_path, use_column_width=True)
             with open(output_path, "rb") as file:
                 st.download_button(
                     label="📥 썸네일 파일로 다운로드 (원본 화질)",
                     data=file,
                     file_name="thumbnail.png",
                     mime="image/png",
                     type="primary",
                     use_container_width=True
                 )

    st.markdown("---")
    st.header("📝 완성된 블로그 포스트 (네이버 블로그 복사 최적화)")
    
    import markdown
    safe_content = markdown.markdown(st.session_state['blog_content'], extensions=['nl2br', 'sane_lists', 'extra'])
    
    # 네이버 블로그 스마트에디터는 Base64 인코딩 이미지를 보안상 차단하여 복사/붙여넣기를 허용하지 않음.
    # 따라서 안내 문구 박스로 대체하여 직접 다운로드한 이미지를 첨부하도록 유도.
    img_html = ""
    if os.path.exists(output_path):
        img_html = f'<div style="text-align: center; margin-bottom: 30px; padding: 40px; background-color: #f8f9fa; border: 2px dashed #cecece; border-radius: 8px; color: #888;"><b>📷 이곳에 방금 복사한 썸네일 이미지를 붙여넣기(Ctrl+V) 하거나 파일을 첨부해 주세요.</b><br><span style="font-size: 13px;">(네이버 블로그 보안 정책상, 웹사이트 내장 이미지의 한 번에 복사되기를 차단하므로 직접 붙여넣어야 합니다)</span></div>'
    
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
