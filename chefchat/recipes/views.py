import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from recipes.serializers import ChatRequestSerializer
from recipes.services.llm_services import call_llm
from recipes.models import ChatLog
from recipes.services.prompt_generator import build_prompt

log = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_interaction(request):
    serializer = ChatRequestSerializer(data=request.data)
    if serializer.is_valid():
        user_message = serializer.validated_data['message']
        prompt = build_prompt(request.user, user_message)
        try:
            bot_response = call_llm(messages=prompt)
        except Exception as e:
            return Response({"error": "LLM call failed: " + str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Log conversation for context
        ChatLog.objects.create(user=request.user if request.user.is_authenticated else None,
                               user_message=user_message,
                               bot_response=bot_response)

        return Response({"response": bot_response}, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    request.user.auth_token.delete()
    return Response({"detail": "Successfully logged out."},
                    status=status.HTTP_200_OK)