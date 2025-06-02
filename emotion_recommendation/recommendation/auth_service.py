import requests

AUTH_SERVICE_URL = "http://auth-service:8001/auth"

def verify_access_token(token: str) -> int:
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/internal/verify/",
            json={"token": token},
            timeout=3
        )
        if response.status_code == 200:
            return response.json().get("user_id")
        else:
            try:
                return_detail = response.json().get('detail', response.text)
            except Exception:
                return_detail = response.text
            raise Exception(f"Token verification failed: {return_detail}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Auth service connection failed: {str(e)}")

# def verify_access_token(token: str) -> int:
#     print(f"[MOCK] 토큰 검증 시도: {token}")
#     if token == "mock-token-123":  # ← 여기를 현재 Postman에서 보낸 값으로 맞춤
#         return 1  # 테스트용 user_id
#     else:
#         raise Exception("Invalid mock token")
