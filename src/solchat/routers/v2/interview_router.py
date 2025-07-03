from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.solchat.schemas.v2.interview_schema import InterviewStartRequest, InterviewfollowRequest
from src.solchat.services.v2.interview_service import (
    handle_interview_start,
    handle_interview_answer, 
    interview_end_status
)

router = APIRouter()

@router.post("/interview/start")
async def interview_start(req: InterviewStartRequest):
    stream = await handle_interview_start(req)
    return StreamingResponse(stream, media_type="text/event-stream")

@router.post("/interview/answer")
async def interview_answer(req: InterviewfollowRequest):
    stream = await handle_interview_answer(req)
    return StreamingResponse(stream, media_type="text/event-stream")

@router.get("/interview/end/status")
def get_interview_end_status(sessionId: str):
    return {
        "sessionId": sessionId,
        "isFinished": interview_end_status.get(sessionId, False)
    }