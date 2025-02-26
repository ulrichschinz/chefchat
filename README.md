# ChefChat


## Overview

ChefChat is a recipe management application that allows users to save cooking recipes, create shopping lists, and interact with the application through a chatbot interface. The application leverages an external Large Language Model (LLM) to analyze and structure recipe data, provide personalized suggestions, and manage user interactions.

## Features

- **Recipe Management**: Save and manage cooking recipes with fields such as title, ingredients, recipe steps, Cookidoo integration, freezing options, number of servings, preparation and total duration, and images.
- **Chatbot Interaction**: Interact with the application using a chatbot to add recipes, get cooking suggestions, and generate shopping lists.
- **Context Preservation**: Save conversation history to provide personalized, context-aware suggestions and avoid repeating recipes.
- **Hybrid Storage Approach**: Store full chat logs and generate summary points for efficient context retrieval.
- **User-Defined Retention Policy**: Allow users to control how long their history is stored, with options for automatic deletion.
- **User Interface for History Management**: Provide a UI to view, search, filter, manage, edit, or delete past interactions.
- **Weekly Meal Planning**: Suggest dishes for a week and allow users to swap recipes easily.
- **Shopping List Generation**: Create shopping lists based on selected recipes.

## Getting Started

To set up the development environment, follow these steps:

1. Create a virtual environment:
    ```bash
    # python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

2. Configure your API key for OpenAI.
```markdown
2. Configure your API key for OpenAI:

    ```bash
    export OPENAI_API_KEY='your-api-key-here'
    ```

3. Run the application:

    ```bash
    python manage.py runserver
    ```
```
4. Navigate to the frontend directory and install dependencies:
    ```bash
    cd chefchat-frontend
    npm install
    ```

5. Start the frontend development server:
    ```bash
    npm run dev
    ```

## ChatWindow Component

The ChatWindow component is built using React and provides the main interface for user interactions. It consists of a chat history section and an input section for sending messages. The component maintains the state of the chat messages and handles sending messages to the backend.

## Questions and Feedback

If you have any questions or need further clarification, please feel free to ask. The goal is to ensure a clear understanding of the product and its features before diving into the technical implementation.

## Contribution

Contributions are welcome! Please follow the standard GitHub workflow for submitting pull requests and ensure your code adheres to the project's coding standards.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries or support, please contact the project maintainer.





```bash
# python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```



# Prompt to start with

That is how the story began:

```text
Hello. You are my programming assistant with extensive experience in software development and planning. You have been hired to help plan and implement a project: the development of a recipe app that helps create shopping lists.
                                                                                                                                                                                                                                                                                 Specifically, it should include the following features:

I can save cooking recipes there. These should consist of the fields:
title: Name of the recipe / meal
ingredients: ingredients for the recipe. unstructured text. llm can analyze and build structured data from it and save the structured format.
recipe: what to do in what order
Cookidoo: is it a cookidoo recipe. If yes, then recipe is not mandatory, as cookidoo will guide you through the thermomix
freeze: can that meal be precooked and can i then freez it to just warm it up some day
number of people: for how many people is that revipe
duration (work): how many minutes do you have to do something
duration (total, from a-z): how long does it take to start with an empty kitchen and having the meal on the table in the end
picture: an image of the meal.                                                                                                                                                                                                                                                   For all the fields: you sould be able to interact with a chatbot to save a recipe and the bot should guide the user to provide information needed. the llm then in the end discovers the fields and the corresponding values and then we can save the genereated structured data.

I want to be able to interact with the application like a chatbot. An external LLM may be used. I have an API key for OpenAI.
Context Preservation:
Saving conversation history enhances the chatbot's ability to provide personalized, context-aware suggestions (e.g., avoiding recipes already used recently).
                                                                                                                                                                                                                                                                                 Hybrid Storage Approach:

Full Logs: Store complete chat logs for traceability and detailed records. It can then be used for RAG purposes.
Summary Points: Generate concise summaries capturing key decisions and user preferences. Also makes maybe RAG easier and reduces needed tokens.
This hybrid approach allows efficient context retrieval without overwhelming the LLM's token limits.                                                                                                                                                                             User-Defined Retention Policy: Users should have control over how long their history (both, summary and full logs, no differentiation) is stored, whether indefinitely or for a set period (e.g., one week or one month), with options for automatic deletion.                                                                                                                                                                                                                                                                                                    User Interface for History Management:
Provide a dedicated UI where users can:

View both full chat logs and summarized history.
Search, filter, and manage past interactions.
Edit or delete entries as needed.

This already makes clear, that we need a user management.

When I tell the chatbot to suggest dishes for a week, I want the application to find the desired recipes and suggest them day by day. Now it should be easy for me to say that I want to swap one or another recipe from the list. Then a list will be suggested that has swapped the desired recipes.


Once the list is generated, I will ask if it can create a shopping list for me. This should then be output in a specific format (to be defined later).

Overall, the goal is to communicate with the app only via the chatbot, for example, to add recipes. However, not everything has to be achieved at once; it should be done incrementally and step by step. In the meantime, classic forms can also be used...

The LLM should be used for every case, that is helpfull and makes the implementation of the app easier, but most important, the usability of the app very good.

I'd like to proceed very incremental. So do not directly make a full plan for the project now. Better help me to think about the plan. Ask questions, which you think are not clear to you. If we have a good idea, how the result should look like, we can start tinking about, what the technologies could be to use. Do we go with an RAG approach, as originally I thought it is just a prompt job, give list of recipes and let llm build a list with shopping list. but it turns out, that the prompt is too big, so that is what my next thought was: then let's partition the recipes and use rag to pull the right context for questions. But I'm not sure, if this approach is the right approach, so then again: Let's really go step by step. Start with Product / Result perspective and then drill in and think how to build it.-

Do you have any questions so far? Dont be to specific now. Is the general product goal clear? Again, let's start on the product level and from there drill incrementally in the implementation.
```
