import httpx, asyncio
from datetime import datetime
from typing import AsyncGenerator
from src.solchat.config import settings, BACKEND_INTERVIEW_URL
from src.solchat.core.utils.history_utils import build_context_text
from src.solchat.adapters.v2.llm_interview import call_agent
from src.solchat.schemas.v2.interview_schema import InterviewStartRequest, InterviewfollowRequest
from src.solchat.core.v2.chat_prompt_templates import INTERVIEW_START_PROMPT, INTERVIEW_FLOW_DECIDER_PROMPT, QUESTION_AGENT_PROMPT, FOLLOWUP_AGENT_PROMPT, EVALUATION_AGENT_PROMPT
import logging

logger = logging.getLogger(__name__)

#  백엔드 인터뷰 종료 알림 비동기 POST 함수 (2-2)
interview_end_status = {}

async def notify_interview_end(session_id: str, finished: bool):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                BACKEND_INTERVIEW_URL,
                json={"sessionId": session_id, "finished": finished},
            )
            interview_end_status[session_id] = response.status_code == 200 and finished
            print(f"[notify_interview_end] session_id={session_id}, finished={finished}")
            if response.status_code != 200:
                logging.warning(f"[notify_interview_end] 상태코드 {response.status_code}: {response.text}")
    except Exception as e:
        interview_end_status[session_id] = False
        print(f"[notify_interview_end] 호출 실패: session_id={session_id}, finished={finished}")
        logging.warning(f"[notify_interview_end] 호출 실패: {e}")

#  /interview/start
async def handle_interview_start(req: InterviewStartRequest):

    problem_text = f"{req.title}\n{req.description}\n입력: {req.inputDescription}\n출력: {req.outputDescription}\n예시: {req.inputExample} → {req.outputExample}"
    prompt = INTERVIEW_START_PROMPT.format(problem=problem_text, language=req.codeLanguage)
    return await call_agent(
        prompt,
        stream=True,
        max_tokens=settings.max_tokens_interview_start,
        session_id=req.sessionId, 
    )

async def handle_interview_answer(req: InterviewfollowRequest) -> AsyncGenerator[str, None]:
    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    context_text = build_context_text(messages, summary=req.summary)

    # assistant가 질문한 횟수 세기
    assistant_questions = [m for m in messages if m["role"] == "assistant"]
    if len(assistant_questions) >= 8:
        # 5번 이상이면 강제 종료 및 총평
        evaluation_stream = await call_agent(
            EVALUATION_AGENT_PROMPT.format(context=context_text),
            stream=True,
            max_tokens=settings.max_tokens_interview_end,
            session_id=req.sessionId,
        )
        asyncio.create_task(notify_interview_end(req.sessionId, finished=True))
        return evaluation_stream

    # 대화 흐름 판단 (followup / question / end)
    flow_decision = await call_agent(
        INTERVIEW_FLOW_DECIDER_PROMPT.format(context=context_text),
        stream=False,
        max_tokens=10
    )
    decision = flow_decision.strip().lower()

    # 종료 판단 → 총평 스트리밍
    if decision == "end":
        evaluation_stream = await call_agent(
            EVALUATION_AGENT_PROMPT.format(context=context_text),
            stream=True,
            max_tokens=settings.max_tokens_interview_end,
            session_id=req.sessionId,
        )
        asyncio.create_task(notify_interview_end(req.sessionId, finished=True))
        return evaluation_stream

    # 종료가 아닐 때도 상태 전달
    asyncio.create_task(notify_interview_end(req.sessionId, finished=False))

    # followup or question → 스트리밍 질문 생성
    if decision == "followup":
        previous_question = messages[-2]["content"] if len(messages) >= 2 and messages[-2]["role"] == "assistant" else ""
        user_response = messages[-1]["content"] if len(messages) >= 1 and messages[-1]["role"] == "user" else ""

        followup_stream = await call_agent(
            FOLLOWUP_AGENT_PROMPT.format(
                previous_question=previous_question,
                user_response=user_response
            ),
            stream=True,
            max_tokens=settings.max_tokens_interview_start,
            session_id=req.sessionId,
        )
        return followup_stream

    else:  # "question" 또는 fallback
        avoid_list = "\n".join(f"- {m['content']}" for m in messages if m["role"] == "assistant")

        question_stream = await call_agent(
            QUESTION_AGENT_PROMPT.format(
                context=context_text,
                avoid_list=avoid_list
            ),
            stream=True,
            max_tokens=settings.max_tokens_interview_answer,
            session_id=req.sessionId,
        )
        return question_stream