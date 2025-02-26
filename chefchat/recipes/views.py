import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from chefchat.config import OPENAI_API_KEY
from recipes.serializers import ChatRequestSerializer
from recipes.vector.index import query_index_with_context
from recipes.models import ChatLog, Recipe
from recipes.services.prompt_generator import detailed_plan_prompt, planning_propmpt
from recipes.services.query_classifier import classify_query
import openai
client = openai

log = logging.getLogger(__name__)

# Make sure your OpenAI API key is set
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_interaction(request):
    serializer = ChatRequestSerializer(data=request.data)
    if serializer.is_valid():
        user_message = serializer.validated_data['message']

        # Todo classify is not working
        query_type = classify_query(user_message)
        log.info(f"Classified query as: {query_type}")
        messages = []
        # if "" in classification:
        #     return "planning_request"
        # elif "planning_change_request" in classification:
        #     return "planning_change_request"
        # elif "use_plan_request" in classification:
        #     return "use_plan_request"
        # elif "clarify if you want to create a new plan" in classification:
        #     return "clarify_request"

        if query_type == "planning_request":
            messages = planning_propmpt(user_message)
        elif query_type == "detailed_request":
            messages = detailed_plan_prompt(user_message)

        # Call OpenAI's ChatCompletion API
        try:
            response = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.7)
            bot_response = response.choices[0].message.content.strip()
        except Exception as e:
            return Response({"error": "LLM call failed: " + str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Optionally, log the conversation
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