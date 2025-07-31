from typing import Tuple, Dict
import os
import dotenv
from dotenv import load_dotenv
import requests as r 
from datetime import datetime 
from zoneinfo import ZoneInfo 
import streamlit as st
from openai import OpenAI
import json

load_dotenv() # read .env file and add to my environment 
EXCHANGERATE_API = os.getenv('EXCHANGERATE_API_KEY') # retrieve a variable's value from my current environment (os.environ)

base_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API}/pair"

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

# Convert UTC time to readable format in PST 
def parse_time(utc_time):
    dt = datetime.strptime(utc_time, "%a, %d %b %Y %H:%M:%S %z")
    dt_pst = dt.astimezone(ZoneInfo("America/Los_Angeles"))
    date_time = dt_pst.strftime("%Y-%m-%d %H:%M")
    return date_time

# Call exachange rate API and return answer 
def get_exchange_rate(base: str, target: str, amount: str) -> Tuple:
    """Return a tuple of (base, target, amount, conversion_result (2 decimal places))"""
    url = f"{base_url}/{base}/{target}/{amount}"
    response = r.get(url)

    if response.status_code == 200:
        result_dict = response.json()

        # Optional 
        last_date_time = parse_time(result_dict['time_last_update_utc'])

        conversion_result = result_dict['conversion_result'] # round to two decimal places 
        return (base, target, amount, f"{conversion_result:.2f}", last_date_time)
    
    else:
        return f"Failed to fetch data {response.status_code}"

# print(get_exchange_rate('USD', 'CNY', '20'))

# Processed prompt into appropriate format 
def call_llm(textbox_input) -> Dict:
    """Make a call to the LLM with the textbox_input as the prompt.
       The output from the LLM should be a JSON (dict) with the base, amount and target"""

    tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "exchange_rate_function",
                        "description": "Convert a given amount of money from one currency to another. \
                                        Each currency will be represented as a 3-letter code",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "base": {
                                    "type": "string",
                                    "description": "The base or original currency.",
                                },
                                "target": {
                                    "type": "string",
                                    "description": "The target or converted currency",
                                },
                                "amount": {
                                    "type": "string",
                                    "description": "The amount of money to convert from the base currency.",
                                },
                            },
                            "required": ["base", "target", "amount"],
                            "additionalProperties": False,
                        },
                    },
                }
            ]
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": textbox_input,
                }
            ],
            temperature=1.0,
            top_p=1.0,
            model=model,
            tools=tools
        )

    except Exception as e:
        print(f"Exception {e} for {text}")
    else:
        return response

def run_pipeline(user_input):
    """Based on textbox_input, determine if you need to use the tools (function calling) for the LLM.
    Call get_exchange_rate(...) if necessary"""

    response = call_llm(user_input)
    
    if response.choices[0].finish_reason == 'tool_calls': #tool_calls
        # Update this
        response_arguments = json.loads(call_llm(user_input).choices[0].message.tool_calls[0].function.arguments)
        (base, target, amount, conversion_result, last_update_time) = get_exchange_rate(response_arguments['base'], 
                                                                                    response_arguments['target'], 
                                                                                    response_arguments['amount'])
        st.write(f'{base} {amount} is {target} {conversion_result}')
        st.write(f"Exchange rate lastly updated on {last_update_time}.")

    elif response.choices[0].finish_reason == 'stop': #tools not used
        # Update this
        alt_reponse = response.choices[0].message.content
        st.write(f"(Function calling not used)")
        st.write(f"{alt_reponse}")
    else:
        st.write("NotImplemented")

# Create app layout 
st.title("Multilingual Money Changer")
user_input = st.text_area("**Enter the amount of currency to change:**\
                           \n &#128512; Base currency in three-letter code\
                           \n &#128512; Amount in base currency unit\
                           \n &#128512; Target currency in three-letter code")

if st.button("Submit"):
    run_pipeline(user_input)
    


