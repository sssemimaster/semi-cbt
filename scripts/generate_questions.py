import os
import json
import random
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_hynix_news_text():
    """SK하이닉스 뉴스룸에서 최신 기사 텍스트를 크롤링해오는 함수"""
    rss_url = "https://news.skhynix.co.kr/feed"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        # 1. RSS 피드(최신글 목록) 가져오기
        response = requests.get(rss_url, headers=headers)
        root = ET.fromstring(response.content)
        items = root.findall('.//item')
        
        # 2. 최근 15개 기사 중 하나를 랜덤으로 선택 (다양성 확보)
        selected_item = random.choice(items[:15])
        article_url = selected_item.find('link').text
        article_title = selected_item.find('title').text
        
        # 3. 해당 기사 페이지 접속하여 본문(<p> 태그) 텍스트만 추출
        art_res = requests.get(article_url, headers=headers)
        soup = BeautifulSoup(art_res.content, 'html.parser')
        paragraphs = soup.find_all('p')
        article_text = " ".join([p.get_text() for p in paragraphs])
        
        print(f"크롤링 성공: {article_title}")
        # GPT 토큰 제한을 고려해 최대 4000자까지만 자르기
        return article_title, article_text[:4000]
    except Exception as e:
        print(f"크롤링 실패: {e}")
        return None, None

def generate_contents_from_news():
    title, article_text = get_hynix_news_text()
    
    if not article_text:
        print("기사 텍스트가 없어 기본 모드로 1문제만 생성합니다.")
        return # 크롤링 실패 시 안전종료 (필요시 기존 로직 대체 가능)

    # 4. GPT에게 기사를 주고 JSON 포맷으로 문제와 이론을 요구
    PROMPT = f"""
    당신은 SK하이닉스의 공정기술 수석 엔지니어입니다.
    아래 제공된 [공식 뉴스룸 기사 본문]을 읽고, 이 내용을 바탕으로 '모의고사 문제 3개'와 '이론 요약 카드 1개'를 생성해 주세요.
    
    반드시 아래의 구조를 가진 단일 JSON 객체(Object)로만 응답해야 하며, 마크다운(```json)을 포함하지 마세요.
    {{
      "questions": [
        {{
          "id": "AUTO-{random.randint(10000,99999)}",
          "category": "반도체 8대 공정 (기사 내용에 맞게 구체화)",
          "topic": "기사 핵심 주제",
          "difficulty": "중급",
          "question": "문제 지문",
          "options": ["보기1", "보기2", "보기3", "보기4"],
          "answer": 0,
          "explanation": "해설",
          "flashcard_keywords": ["키워드1", "키워드2"],
          "interview_answer": "두괄식 2~3문장 면접용 답변"
        }},
        // ... (문제 총 3개)
      ],
      "theories": [
        {{
          "category": "반도체 8대 공정 등 대분류",
          "subject": "반도체 8대 공정 등",
          "title": "{title} (요약)",
          "content": "기사의 핵심 기술 원리와 특징을 3~4문단으로 요약한 텍스트. 문단 바꿈은 \\n 으로 처리.",
          "tags": ["기술키워드1", "기술키워드2"]
        }}
      ]
    }}

    [공식 뉴스룸 기사 본문]
    {article_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that strictly outputs a JSON object."},
            {"role": "user", "content": PROMPT}
        ],
        temperature=0.7
    )
    
    raw_text = response.choices[0].message.content
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
    
    try:
        new_data = json.loads(raw_text)
        new_questions = new_data.get("questions", [])
        new_theories = new_data.get("theories", [])
        
        # --- questions.json 업데이트 ---
        q_file = "data/questions.json"
        if os.path.exists(q_file):
            with open(q_file, "r", encoding="utf-8") as f:
                existing_q = json.load(f)
        else:
            existing_q = []
        updated_q = new_questions + existing_q
        with open(q_file, "w", encoding="utf-8") as f:
            json.dump(updated_q, f, ensure_ascii=False, indent=2)
            
        # --- theories.json 업데이트 ---
        t_file = "data/theories.json"
        if os.path.exists(t_file):
            with open(t_file, "r", encoding="utf-8") as f:
                existing_t = json.load(f)
        else:
            existing_t = []
        updated_t = new_theories + existing_t
        with open(t_file, "w", encoding="utf-8") as f:
            json.dump(updated_t, f, ensure_ascii=False, indent=2)
            
        print(f"업데이트 완료: 문제 {len(new_questions)}개, 이론 {len(new_theories)}개 추가됨.")
        
    except json.JSONDecodeError:
        print("JSON 파싱 에러: GPT 응답 형식이 잘못되었습니다.")

if __name__ == "__main__":
    generate_contents_from_news()
