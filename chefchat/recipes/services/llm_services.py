import json
import logging
import openai
from openai import OpenAI
from chefchat.config import OPENAI_API_KEY

log = logging.getLogger(__name__)
client = openai

def call_llm(messages: list,
             model: str = "gpt-3.5-turbo",
             max_tokens: int = 3000,
             temperature: float = 0.7) -> str:
    """
    Call the LLM with the given messages and return the response.

    :param
    messages: list of messages to send to the LLM
    model: the model to use, default is "gpt-3.5-turbo"
    max_tokens: the maximum number of tokens to generate, default is 3000
    """
    # Call OpenAI's ChatCompletion API
    try:
        response = client.chat.completions.create(model=model,
                                                   messages=messages,
                                                   max_tokens=max_tokens,
                                                   temperature=temperature)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"LLM call failed: {str(e)}"

def build_structured_data(raw_data: str) -> dict:
    context = """
    Build structured data from unstructured text.
    You will recieve a string that contains unstructured data.
    You generate structured data from it.
    Example:
    Input:
    Zutaten:
    1.500 g Gulasch vom Schwein
    6 EL Butterschmalz
    1 ½ TL Senf
    3 EL Tomatenmark
    3 große Zwiebeln, gehackt
    3 Knoblauchzehen, gepresst
    3 Karotten, gerieben
    600 ml Bier (Sorte nach Wahl)
    1.800 ml Gemüsebrühe
    Salz und Pfeffer (nach Geschmack)
    3 TL Paprikapulver, edelsüß
    3 EL Crème fraîche
    Saucenbinder (nach Bedarf)
    Output:
    [
      {
        "Gulasch": {
          "Menge": 1500,
          "Einheit": "g",
          "Fleischsorte": "Schwein"
        },
        "Butterschmalz": {
          "Menge": 6,
          "Einheit": "EL"
        },
        "Senf": {
          "Menge": 1.5,
          "Einheit": "TL"
        },
        "Tomatenmark": {
          "Menge": 3,
          "Einheit": "EL"
        },
        "Zwiebeln": {
          "Menge": 3,
          "Einheit": "Stück",
          "Zubereitung": "gehackt"
        },
        "Knoblauch": {
          "Menge": 3,
          "Einheit": "Zehen",
          "Zubereitung": "gepresst"
        },
        "Karotten": {
          "Menge": 3,
          "Einheit": "Stück",
          "Zubereitung": "gerieben"
        },
        "Bier": {
          "Menge": 600,
          "Einheit": "ml",
          "Sorte": "nach Wahl"
        },
        "Gemüsebrühe": {
          "Menge": 1800,
          "Einheit": "ml"
        },
        "Gewürze": [
          {
            "Name": "Salz",
            "Menge": "nach Geschmack"
          },
          {
            "Name": "Pfeffer",
            "Menge": "nach Geschmack"
          },
          {
            "Name": "Paprikapulver",
            "Menge": 3,
            "Einheit": "TL",
            "Sorte": "edelsüß"
          }
        ],
        "Crème fraîche": {
          "Menge": 3,
          "Einheit": "EL"
        },
        "Saucenbinder": {
          "Menge": "nach Bedarf",
          "Einheit": ""
        }
      }
    ]
    Leave away categories in the input. Only try to concentrate on the items,
    in the example the ingredients.
    Generate a structure that I can feed you later and you can easily understand
    it and generate e.g. sums of how many eggs you need overall.
    """

    prompt = [
            {"role": "system",
             "content": context,
            },
            {"role": "assistant", "content": f"here is the unstructured data: {raw_data}"},
            {"role": "user",
            "content": (
                "only answer the structured data, like the json, no other text."
                )
            },
            {"role": "user", "content": "Please provide the structured data. No surrounding markdown or anything else. Only the structured data."},
        ]

    structured_data_str = call_llm(prompt) 
    log.debug(f"Structured data: {structured_data_str}")
    return json.loads(structured_data_str)
    

    