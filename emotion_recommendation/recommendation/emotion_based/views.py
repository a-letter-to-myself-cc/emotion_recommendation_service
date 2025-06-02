# emotion_recommendation/emotion_based/views.py
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import openai, os
from dotenv import load_dotenv
import re
from django.contrib.auth.models import User
#from recommendation.utils import log_recommendation, generate_recommendations
from rest_framework.permissions import AllowAny
from ..utils import log_recommendation, generate_recommendations

# ✅ 정확한 전체 경로로 바꿔야 합니다
from emotion_recommendation.recommendation.auth_service import verify_access_token

from django.views.decorators.csrf import csrf_exempt



dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

openai.api_key = os.getenv("OPENAI_API_KEY")




import os
# openai.api_key = os.getenv("OPENAI_API_KEY")

@api_view(["POST"])
def recommend_movies_and_music(request):
    # 1. 인증 처리
    auth_header = request.headers.get("Authorization", "")
    if not auth_header or not auth_header.startswith("Bearer "):
        return Response({"detail": "Authorization header missing"}, status=401)
    
    token = auth_header.split("Bearer ")[1]
    try:
        user_id = verify_access_token(token)
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "사용자가 존재하지 않습니다."}, status=404)
    except Exception as e:
        return Response({"detail": str(e)}, status=401)

    # 2. 추천 생성
    mood = request.data.get("most_frequent_mood")
    lines = generate_recommendations(mood, user=user)
    log_recommendation(user_id, mood, lines)

    return Response({"recommendations": "\n".join(lines)})



def split_recommendations(recommendations_text):
    movie_lines = []
    music_lines = []
    current_block = None

    for line in recommendations_text.splitlines():
        line = line.strip()
        if "영화 추천" in line:
            current_block = "movie"
        elif "음악 추천" in line:
            current_block = "music"
        elif line and not line.startswith("###"):
            cleaned_line = re.sub(r'^\d+\.\s*', '', line)
            if current_block == "movie":
                movie_lines.append(cleaned_line)
            elif current_block == "music":
                music_lines.append(cleaned_line)

    return movie_lines, music_lines

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommendation_result_view(request):
    # ✅ Authorization 헤더에서 토큰 추출
    auth_header = request.headers.get("Authorization", "")
    if not auth_header or not auth_header.startswith("Bearer "):
        return Response({"detail": "Authorization header missing or malformed"}, status=401)

    token = auth_header.split("Bearer ")[1]

    # ✅ JWT 토큰 인증 → user_id 반환
    try:
        user_id = verify_access_token(token)
    except Exception as e:
        return Response({"detail": str(e)}, status=401)

    # ✅ 실제 사용자 객체 가져오기
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "사용자가 존재하지 않습니다."}, status=404)

    # ✅ 추천 생성
    recommendations = generate_recommendations(mood="기쁨", user=user)

    return Response({"recommendations": recommendations})