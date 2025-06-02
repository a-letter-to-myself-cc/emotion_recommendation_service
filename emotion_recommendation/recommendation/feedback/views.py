from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from ..feedback.models import Feedback
from ..auth_service import verify_access_token


@csrf_exempt
@require_POST
def save_feedback(request):
    # ✅ 헤더에서 JWT 토큰 추출
    auth_header = request.headers.get("Authorization", "")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JsonResponse({"detail": "Authorization header missing or malformed"}, status=401)

    token = auth_header.split("Bearer ")[1]
    try:
        user_id = verify_access_token(token)
    except Exception as e:
        return JsonResponse({"detail": str(e)}, status=401)

    # ✅ POST 데이터 받기
    item_title = request.POST.get("item_title")
    item_type = request.POST.get("item_type")
    feedback = request.POST.get("feedback")

    if not all([item_title, item_type, feedback]):
        return JsonResponse({"detail": "모든 필드가 필요합니다."}, status=400)

    # ✅ 저장
    Feedback.objects.update_or_create(
        user_id=user_id,
        item_title=item_title,
        item_type=item_type,
        defaults={"feedback": feedback}
    )

    return JsonResponse({
        "message": f"{'좋아요' if feedback == 'like' else '별로예요'}로 저장되었습니다."
    })
