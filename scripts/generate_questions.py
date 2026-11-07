import os
import json
import random
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 보편적이고 표준화된 반도체 카테고리로 리스트 개편
topics = [
    {"category": "반도체 기초 이론", "subject": "반도체 물리 및 트랜지스터 동작 원리"},
    {"category": "반도체 8대 공정", "subject": "포토 및 식각 공정 (미세화 트렌드)"},
    {"category": "반도체 8대 공정", "subject": "증착 및 금속 배선 공정 (CVD, ALD 등)"},
    {"category": "차세대 첨단 기술", "subject": "최신 패키징(HBM, TSV) 및 소자 구조(GAA)"}
]
selected = random.choice(topics)
sel_category = selected["category"]
sel_subject = selected["subject"]

# 프롬프트를 범용적이고 정석적인 기준으로 변경
PROMPT = f"""
당신은 삼성전자, SK하이닉스 등 주요 반도체 기업의 공식 직무 면접관이자 전공 교수입니다.
오늘 출제할 대분류는 '{sel_category}'이며, 상세 주제는 '{sel_subject}'입니다. 
이 주제와 관련된 학부 전공자 및 취업 준비생을 위한 정석적이고 범용적인 객관식 문제를 한 번에 5개 생성해 주세요.

반드시 아래 형식을 가진 JSON 배열(Array)로만 응답해야 하며, 마크다운 없이 순수 JSON 텍스트만 출력하세요.
[
  {{
    "id": "AUTO-{random.randint(10000,99999)}",
    "category": "{sel_category}",
    "topic": "{sel_subject} 내부의 세부 토픽 (예: EUV, MOSFET 등)",
    "difficulty": "초급/중급/고급 중 택 1",
    "question": "깔끔하고 정석적인 문제 지문",
    "options": ["보기1", "보기2", "보기3", "보기4"],
    "answer": 0,
    "explanation": "해당 개념을 완벽히 이해할 수 있는 범용적인 상세 해설",
    "flashcard_keywords": ["키워드1", "키워드2"],
    "interview_answer": "실무 면접에서 답변하기 좋은 두괄식 형태의 2~3문장 모범 스크립트"
  }}
]
"""

def generate_bulk_questions():
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You strictly output a valid JSON array of questions."},
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
