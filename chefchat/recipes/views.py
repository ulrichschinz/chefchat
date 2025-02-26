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
from recipes.services.prompt_generator import generate_prompt_messages
from recipes.services.query_classifier import classify_query
import openai
client = openai

log = logging.getLogger(__name__)

# Make sure your OpenAI API key is set
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_interaction(request):
    log.debug(f"Authorized user: {request.user}")
    log.debug(f"Authorization header: {request.headers.get('Authorization')}")
    log.debug(f"Is authenticated: {request.user.is_authenticated}")

    serializer = ChatRequestSerializer(data=request.data)
    if serializer.is_valid():
        user_message = serializer.validated_data['message']

        # Todo classify is not working
        query_type = classify_query(user_message)
        log.debug(f"Query type: {query_type}")

        # Retrieve relevant recipes from the FAISS index
        try:
            recipe_ids, distances = query_index_with_context(user_message, k=7)
            recipes = Recipe.objects.filter(id__in=recipe_ids)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        # Build the context with the retrieved recipes
        messages = generate_prompt_messages(user_message, recipes)
        log.debug(messages)

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