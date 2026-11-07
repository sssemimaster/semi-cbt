import os
import json
import random
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

topics = ["반도체 8대 공정", "포토 공정", "식각 공정", "증착 및 이온주입", "HBM 및 TSV 패키징", "반도체 공정 데이터 분석"]
selected_topic = random.choice(topics)

# 한 번에 5문제를 배열 형태로 요구
PROMPT = f"""
당신은 삼성전자 및 SK하이닉스의 반도체 공정기술 직무 면접관입니다.
오늘의 주제는 '{selected_topic}'입니다. 이 주제와 관련된 직무 면접용/전공 필기용 고품질 객관식 문제를 한 번에 **5개** 생성해 주세요.

반드시 아래 형식을 가진 JSON 배열(Array)로만 응답해야 하며, 마크다운(```json)을 포함하지 말고 순수 JSON 텍스트만 출력하세요.
[
  {{
    "id": "AUTO-{random.randint(10000,99999)}",
    "category": "{selected_topic}",
    "topic": "구체적인 세부 주제",
    "difficulty": "중급",
    "question": "문제 지문",
    "options": ["보기1", "보기2", "보기3", "보기4"],
    "answer": 0,
    "explanation": "객관식 상세 해설",
    "flashcard_keywords": ["키워드1", "키워드2"],
    "interview_answer": "두괄식 형태의 2~3문장 구술형 모범 답변 스크립트"
  }}
]
"""

def generate_bulk_questions():
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that strictly outputs a JSON array."},
            {"role": "user", "content": PROMPT}
        ],
        temperature=0.7
    )
    
    raw_text = response.choices[0].message.content
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
    
    new_questions = json.loads(raw_text)
    
    file_path = "data/questions.json"
    with open(file_path, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
        
    updated_data = new_questions + existing_data
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
        
    print(f"새로운 문제 {len(new_questions)}개 대량 생성 완료!")

if __name__ == "__main__":
    generate_bulk_questions()
