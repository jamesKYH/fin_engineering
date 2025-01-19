import openai
from dotenv import load_dotenv
import os
import streamlit as st
# .env 파일 로드
load_dotenv()



openai.api_key = os.getenv("OPENAI_API_KEY")



def fetch_region_info(region):
    """
    특정 지역의 특색 정보를 OpenAI GPT-4로 가져오는 함수
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "지역 정보를 제공하는 전문가 역할입니다."},
                {"role": "user", "content":f"'{region}' 지역의 특색 있는 정보를 간결하게 한 문장으로 작성해 주세요. "
                        "구체적이고 흥미로운 내용을 포함해주세요."}
            ],
            temperature=0.7,
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"정보를 가져오는 데 실패했습니다: {e}"
