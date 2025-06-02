# authentication.py

import requests
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class AuthenticatedUser:
    def __init__(self, user_id, username="", email=""):
        self.id = user_id
        self.username = username
        self.email = email
        self.is_authenticated = True


class RemoteJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None  # 인증 시도 안 함 → AnonymousUser 처리됨

        token = auth_header.split(' ')[1]
        verify_url = getattr(settings, "AUTH_VERIFY_URL", "http://auth-service:8001/auth/internal/verify/")

        try:
            response = requests.post(
                verify_url,
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code != 200:
                raise AuthenticationFailed(f"유효하지 않은 토큰입니다. (응답 코드: {response.status_code})")

            user_data = response.json()

            user = AuthenticatedUser(
                user_id=user_data.get("user_id"),
                username=user_data.get("username", ""),
                email=user_data.get("email", "")
            )

            return (user, None)

        except requests.exceptions.RequestException as e:
            raise AuthenticationFailed(f"인증 서버 요청 실패: {str(e)}")


# from rest_framework.authentication import BaseAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# import requests

# # ✅ mock 인증용 유저 클래스
# class MockUser:
#     is_authenticated = True
#     id = 999  # 테스트용 user_id

# class RemoteJWTAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         auth_header = request.headers.get('Authorization')
#         if not auth_header or not auth_header.startswith('Bearer '):
#             return None

#         token = auth_header.split(' ')[1]

#         # ✅ mock 토큰 처리
#         if token == "mock-token-123":
#             print("✅ MOCK TOKEN 인증 통과")
#             return (MockUser(), None)

#         try:
#             response = requests.post(
#                 "http://auth-service:8001/auth/internal/verify/",
#                 headers={"Authorization": f"Bearer {token}"}
#             )
#             if response.status_code != 200:
#                 raise AuthenticationFailed("유효하지 않은 토큰입니다.")
#             user_data = response.json()

#             # ✅ 인증 서버가 유저 객체를 dict로 반환하면 필요시 래핑
#             class AuthenticatedUser:
#                 is_authenticated = True
#                 id = user_data.get("user_id")

#             return (AuthenticatedUser(), None)

#         except requests.exceptions.RequestException:
#             raise AuthenticationFailed("인증 서버와의 연결 실패")
