import os
import json
import google.generativeai as genai

# Gemini API 설정
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

PROMPT = """
당신은 삼성전자 및 SK하이닉스의 반도체 공정기술 직무 면접관입니다.
[주제: HBM 및 TSV 패키징 공정] 관련 직무 면접용 객관식 문제를 1개 생성해 주세요.

반드시 아래 JSON 형식으로만 응답해야 합니다:
{
  "id": "PKG-2026-AUTO",
  "category": "패키징/HBM",
  "topic": "TSV 및 하이브리드 본딩",
  "difficulty": "고급",
  "question": "문제 지문",
  "options": ["보기1", "보기2", "보기3", "보기4"],
  "answer": 0,  // 정답 인덱스 (0~3)
  "explanation": "해설 내용",
  "flashcard_keywords": ["키워드1", "키워드2"]
}
"""

def generate_new_question():
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(PROMPT)
    
    # JSON 파싱 및 파일 저장 로직
    raw_text = response.text.replace("```json", "").replace("```", "").strip()
    new_data = json.loads(raw_text)
    
    file_path = "data/packaging_hbm.json"
    with open(file_path, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
        
    existing_data.append(new_data)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    generate_new_question()
