import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

# Gemini 모델 설정 
class Settings(BaseSettings):
    model_solution: str = "gemini-2.5-flash"
    temperature_solution: float = 0.3
    max_tokens_solution: int = 65000

    model_chat: str = "solar-pro"
    temperature_chat: float = 0.3
    
    max_tokens_feedback_start: int = 4096
    max_tokens_feedback_answer: int = 1024
    max_tokens_interview_start: int = 768
    max_tokens_interview_answer: int = 1024
    max_tokens_interview_end: int = 4096
    max_tokens_summary: int = 768

    max_summary_sentences_problem: int = 4
    max_summary_sentences_chat: int = 10
    max_recent_messages: int = 10
    max_summary_messages: int = 10

    model_config = {"protected_namespaces": ("settings_",)}

settings = Settings() 

# 백앤드 설정
BACKEND_SOLUTION_URL = os.getenv("BACKEND_SOLUTION_URL")
BAEKJUN_BACKEND_URL = os.getenv("BAEKJUN_BACKEND_URL")
BACKEND_INTERVIEW_URL = os.getenv("BACKEND_INTERVIEW_URL")
GETPROBLEM_BACKEND_URL = os.getenv("GETPROBLEM_BACKEND_URL")
RECOMMEND_BACKEND_URL = os.getenv("RECOMMEND_BACKEND_URL")
BACKEND_TIMEOUT = float(os.getenv("BACKEND_TIMEOUT", "30.0"))

# 서비스 설정
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY")
