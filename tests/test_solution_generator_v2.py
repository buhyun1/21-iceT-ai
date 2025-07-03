# 테스트 코드
# 실행 방법 : python -m pytest -s tests/test_solution_generator_v2.py

import pytest
from src.solchat.schemas.v2.solution_schema_v2 import SolutionRequest
from src.crawler.v2.solution_generater_v2 import generate_explanation
from src.crawler.v2.post_client_v2 import post_to_backend

@pytest.mark.asyncio
async def test_explain_solutions():
    # 처리할 문제들을 dict 형태로 리스트에 나열
    raw_problems = [
        {
            "problem_number": 1171,
            "title": "사오정",
            "description": (
                "민식이는 다른 사람이 말한 N비트 이진수를 2진수로 듣되, 원본의 i번째 비트가 인식된 이진수의 j번째 비트로 옮겨질 때 |j - i| ≤ D를 항상 만족하도록 왜곡되어 인식한다. "
                "이렇게 얻을 수 있는 모든 N비트 이진수 후보의 개수와, 그 후보들을 오름차순으로 정렬했을 때 K번째로 작은 이진수를 구하라."
            ),
            "input": (
                "첫째 줄에 이진수 비트의 개수 N, 왜곡 허용 최대 거리 D, 정수 K가 공백으로 구분되어 주어진다. "
                "둘째 줄에 상대방이 말한 N비트 이진수가 주어진다."
            ),
            "output": (
                "첫째 줄에 후보 이진수의 총 개수를 100,000,000으로 나눈 나머지를 출력하고, "
                "둘째 줄에 후보 중 K번째로 작은 이진수를 출력한다."
            ),
            "input_example": (
                "4 1 3\n"
                "0110\n"
            ),
            "output_example": (
                "4\n"
                "1001\n"
            )
        },
    ]

    for prob in raw_problems:
        request = SolutionRequest(**prob)
        response = await generate_explanation(request)
        if response is None:
            print("test - LLM 응답 없음")
            return None
        if not hasattr(response, "model_dump"):
            print("test - Pydantic 응답 아님:", type(response))
            return None
        success = post_to_backend(request.problem_number, response)
        assert success, f"백엔드 전송에 실패했습니다: {request.problem_number}"

        print("문제 개요:\n", response.problem_check.problem_description)
        print("사용 알고리즘:\n", response.problem_check.algorithm)
        print("풀이 단계:\n", response.problem_solving)
        print("정답 코드 (Python):\n", response.solution_code.python)