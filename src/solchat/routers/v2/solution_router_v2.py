from fastapi import APIRouter, Depends, Header, HTTPException, status
from src.solchat.schemas.v2.solution_schema_v2 import SolutionRequest, SolutionResponse
from src.solchat.services.v2.solution_service_v2 import explain_solution
from src.solchat.config import SERVICE_API_KEY

router = APIRouter()

# API 키 검증 함수
# - 요청 헤더에서 API 키를 추출하고, 서비스 설정에 정의된 API 키와 비교
# - 일치하지 않으면 401 예외 발생
def verify_api_key(x_api_key: str = Header(...)):
    print("API Key:", x_api_key)
    if x_api_key != SERVICE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )


# 백준 문제 해설 생성 엔드포인트
# - 요청 본문: SolutionRequest 스키마 (문제 정보 포함)
# - 응답: SolutionResponse 스키마 (해설, 정답 코드 포함)

# POST /api/ai/v2/solution
@router.post(
    "/solution",
    response_model=SolutionResponse,
    dependencies=[Depends(verify_api_key)]
)
async def solution_endpoint(body: SolutionRequest):
    return await explain_solution(body)
