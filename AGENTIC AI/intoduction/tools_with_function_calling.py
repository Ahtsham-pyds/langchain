
#https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"


import os
from openai import OpenAI
import requests
import json
from pydantic import BaseModel,Field

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
location = input('text')

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
    }
]

def get_weather(latitude,longitude):
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    res = response.json()
    return res['current']


messages  = [
    {'role':'system','content':'You are helpful AI assistant'},
        {'role':'user','content':f'What is the current temperature in {location}'}
        ]

 
completion = client.chat.completions.create(
    model= "gpt-4o",
    messages =messages,
    tools=tools,
)


completion.model_dump()
# resp = completion.choice[0].message.tools_calls
# resp

for tool_call in completion.choices[0].message.tool_calls:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    messages.append(completion.choices[0].message)
    result = get_weather(**args)
    messages.append(
        {"role":"tool", "tool_call_id":tool_call.id, "content":json.dumps(result)}
    )
    
class WeatherResponse(BaseModel):
    temperature : float = Field(description = 'The current temperature in celcius of the given location'),
    response : str = Field(description = 'A natural language respose to the user query')

completion2 = client.beta.chat.completions.parse(
    model='gpt-4o',
    messages=messages,
    tools=tools,
    response_format=WeatherResponse
)

final = completion2.choices[0].message.parsed
final.temperature
final.response
