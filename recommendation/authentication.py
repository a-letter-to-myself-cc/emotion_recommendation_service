import requests
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

class RemoteJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            response = requests.post(
                "http://accounts:8000/accounts/internal/verify/",  # Docker에서는 서비스명, 외부에서는 도메인/IP
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code != 200:
                raise AuthenticationFailed("유효하지 않은 토큰입니다.")
            
            user_data = response.json()
            return (user_data, None)

        except requests.exceptions.RequestException:
            raise AuthenticationFailed("인증 서버와의 통신 실패")
