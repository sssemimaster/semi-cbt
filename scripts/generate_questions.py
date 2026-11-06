import os
import json
import random
from openai import OpenAI

# GitHub Secrets에서 가져온 OpenAI API 키 설정
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

topics = ["반도체 8대 공정", "포토 공정", "식각 공정", "증착 및 이온주입", "HBM 및 TSV 패키징", "반도체 공정 데이터 분석"]
selected_topic = random.choice(topics)

PROMPT = f"""
당신은 삼성전자 및 SK하이닉스의 반도체 공정기술 직무 면접관입니다.
오늘의 주제는 '{selected_topic}'입니다. 이 주제와 관련된 직무 면접용 또는 전공 필기용 객관식 문제를 1개 생성해 주세요.

반드시 아래 JSON 형식으로만 응답해야 하며, 마크다운(```json)을 포함하지 말고 순수 JSON 텍스트만 출력하세요.
{{
  "id": "AUTO-{random.randint(1000,9999)}",
  "category": "{selected_topic}",
  "topic": "구체적인 세부 주제",
  "difficulty": "중급",
  "question": "문제 지문을 작성하세요.",
  "options": ["보기1", "보기2", "보기3", "보기4"],
  "answer": 0,
  "explanation": "정답인 이유와 오답인 이유를 포함한 상세한 해설을 작성하세요.",
  "flashcard_keywords": ["핵심키워드1", "핵심키워드2", "핵심키워드3"]
}}
""

def generate_new_question():
    # gpt-4o-mini 모델 호출
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that strictly outputs JSON format."},
            {"role": "user", "content": PROMPT}
        ],
        temperature=0.7
    )
    
    # 응답 텍스트에서 JSON 파싱 (마크다운 찌꺼기 안전 제거)
    raw_text = response.choices[0].message.content
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
    new_data = json.loads(raw_text)
    
    # 기존 questions.json 파일 읽기
    file_path = "data/questions.json"
    with open(file_path, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
        
    # 새 문제를 리스트의 맨 앞(최신순)에 추가
    existing_data.insert(0, new_data)
    
    # 다시 파일로 저장
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
    print(f"새로운 문제 생성 완료: {new_data['topic']}")

if __name__ == "__main__":
    generate_new_question()
