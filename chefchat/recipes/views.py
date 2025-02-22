from openai import OpenAI
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from recipes.serializers import ChatRequestSerializer
from recipes.vector.index import query_index
from recipes.models import ChatLog, Recipe
import os

# Make sure your OpenAI API key is set
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@api_view(['POST'])
def chat_interaction(request):
    serializer = ChatRequestSerializer(data=request.data)
    if serializer.is_valid():
        user_message = serializer.validated_data['message']

        # Retrieve relevant recipes from the FAISS index
        try:
            distances, indices = query_index(user_message, k=3)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Convert indices to list
        indices_list = [index for sublist in indices for index in sublist]

        print(f"Indices: {indices_list}")
        
        # Retrieve the actual recipes using the indices
        recipes = Recipe.objects.filter(id__in=indices_list)

        # Build the context with the retrieved recipes
        context_text = "Relevant recipes:\n"
        for recipe in recipes:
            context_text += f"- {recipe.title}\n"
            context_text += f"  Ingredients (raw): {recipe.ingredients_raw}\n"
            context_text += f"  Ingredients (structured): {recipe.ingredients_structured}\n"
            context_text += f"  Instructions: {recipe.instructions}\n"
            context_text += f"  Is Cookidoo: {recipe.is_cookidoo}\n"
            context_text += f"  Can Freeze: {recipe.can_freeze}\n"
            context_text += f"  Number of People: {recipe.number_of_people}\n"
            context_text += f"  Work Duration: {recipe.duration_work} minutes\n"
            context_text += f"  Total Duration: {recipe.duration_total} minutes\n"

        # Construct the prompt for the LLM
        messages = [
            {"role": "system", "content": "You are a helpful cooking assistant. Only use information from the context provided. If there is nothing useful, respond with: 'Sorry, but I could not find anything related to your request.'"},
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": context_text},
            {"role": "user", "content": "Analyze the language of the user content and answer in the same language. For example if the user writes in German, respond in German."},
            {"role": "user", "content": "Please provide a helpful response or suggestion based on the above."}
        ]

        # Call OpenAI's ChatCompletion API
        try:
            response = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
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
