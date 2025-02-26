"""
llm-services provides a set of services that are used to interact with an LLM.

In first iteration only with openapi, but maybe other models may be added in the future.
"""
from openai import OpenAI
from chefchat.config import OPENAI_API_KEY

client = OpenAI(OPENAI_API_KEY)


