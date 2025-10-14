from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def delete_user(request, user_id):
    """
    Deletes a user account and triggers post_delete signal.
    """
    if request.method == "DELETE":
        try:
            user = User.objects.get(pk=user_id)
            user.delete()  # This triggers the post_delete signal
            return JsonResponse({"message": "User and related data deleted successfully."}, status=200)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=404)
    return JsonResponse({"error": "Invalid request method."}, status=405)
