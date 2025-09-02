
#https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"


import os
from openai import OpenAI
import requests
import json
from pydantic import BaseModel,Field

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
#location = input('text')

tools = [ 
         {  
    "type":"function",
    "function":{
        "name":"get_weather",
        "description":"Get the current temperature for provided location",
        "parameters":{
            "type":"object",
            "properties":{
                "latitude":{"type":"number"},
                "longitude":{"type":"number"},
            },
            "required":["latitude","longitude"],
            "additionalProperties":False,
        },
    "strict":True,
         },
    },
         {
    "type":"function",
    "function":{
        "name":"get_kb",
        "description":"Get answer to the question by searching the knowledge base",
        "parameters":{
            "type":"object",
            "properties":{
                "question":{"type":"string"}
            },
            "required":["question"],
            "additionalProperties":False,
        },
    "strict":True
        },
    }
]

def get_weather(latitude,longitude):
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    res = response.json()
    return res['current']

def get_kb(question:str):
    '''Load the whole json file'''
    with open ("kb.json" , "r") as f:
        return json.load(f)
    


messages  = [
    {'role':'system','content':'You are helpful AI assistant'},
        {'role':'user','content':'What is the return policy'}
        ]

 
completion = client.chat.completions.create(
    model= "gpt-4o",
    messages =messages,
    tools=tools,
)


completion.model_dump()
# resp = completion.choice[0].message.tools_calls
# resp

def call_function(name,args):
    if name=="get_weather":
        return get_weather(**args)
    elif name=="get_kb":
        return get_kb(**args)

for tool_call in completion.choices[0].message.tool_calls:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    messages.append(completion.choices[0].message)
    result = call_function(name,args)
    messages.append(
        {"role":"tool", "tool_call_id":tool_call.id, "content":json.dumps(result)}
    )
    
class WeatherResponse(BaseModel):
    temperature : float = Field(description = 'The current temperature in celcius of the given location'),
    response : str = Field(description = 'A natural language respose to the user query')

class KbResponse(BaseModel):
    answer:str=Field(description="The answer to the user question"),
    source:str=Field(description="The record id of the answer")

completion2 = client.beta.chat.completions.parse(
    model='gpt-4o',
    messages=messages,
    tools=tools,
    response_format=KbResponse
    # response_format=[{"type":"json_object","schema": WeatherResponse.model_json_schema()},
    # {"type":"json_object","schema": KbResponse.model_json_schema()}
    # ]
)

final = completion2.choices[0].message.parsed

