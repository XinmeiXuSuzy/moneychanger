from typing import Tuple, Dict
import os
import dotenv
from dotenv import load_dotenv
import requests as r 
from datetime import datetime 
from zoneinfo import ZoneInfo 
import streamlit as st

load_dotenv() # read .env file and add to my environment 
EXCHANGERATE_API = os.getenv('EXCHANGERATE_API_KEY') # retrieve a variable's value from my current environment (os.environ)

base_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API}/pair"

# Create app layout 
st.title("Multilingual Money Changer")
user_input = st.text_area("Enter the amount of currency to change:")

if st.button("Submit"):
    st.write("**You entered:**")
    st.write(user_input)


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
        last_date_time = parse_time(result_dict['time_last_update_utc'])
        print(f"{base} to {target} rate: {result_dict['conversion_rate']}, lastly updated on {last_date_time}.")
        conversion_result = round(result_dict['conversion_result'], 2) # round to two decimal places 
        return (base, target, amount, conversion_result)
    
    else:
        return f"Failed to fetch data {response.status_code}"

print(get_exchange_rate('USD', 'CNY', '20'))

# Processed prompt into appropriate format 
def call_llm(textbox_input) -> Dict:
    """Make a call to the LLM with the textbox_input as the prompt.
       The output from the LLM should be a JSON (dict) with the base, amount and target"""
    try:
        completion = ...
    except Exception as e:
        print(f"Exception {e} for {text}")
    else:
        return completion

def run_pipeline():
    """Based on textbox_input, determine if you need to use the tools (function calling) for the LLM.
    Call get_exchange_rate(...) if necessary"""

    if True: #tool_calls
        # Update this
        st.write(f'{base} {amount} is {target} {exchange_response["conversion_result"]:.2f}')

    elif True: #tools not used
        # Update this
        st.write(f"(Function calling not used) and response from the model")
    else:
        st.write("NotImplemented")