import sys
import google.generativeai as genai

def test_api(api_key):
    try:
        genai.configure(api_key=api_key)
        print("--- 사용 가능한 모델 목록 ---")
        models = genai.list_models()
        count = 0
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
                count += 1
        print(f"\n총 {count}개의 모델을 사용할 수 있습니다.")
    except Exception as e:
        print(f"API 검증 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_api(sys.argv[1])
    else:
        print("API 키를 인자로 전달하세요.")
