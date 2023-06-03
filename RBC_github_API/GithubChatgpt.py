# -*- coding: utf-8 -*-
"""
Created on Sat Feb 18 12:06:09 2023

@author: willi
"""

import openai

# Define OpenAI API key 
openai.api_key = "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"

# Set up the model and prompt
model_engine = "text-davinci-003"
prompt = "Can you browse this link: https://github.com/ModelOriented/interpretable-ai, and tell me what is the last activity date"

# Generate a response
completion = openai.Completion.create(
    engine=model_engine,
    prompt=prompt,
    max_tokens=1024,
    n=1,
    stop=None,
    temperature=0.5,
)

response = completion.choices[0].text
print(response)