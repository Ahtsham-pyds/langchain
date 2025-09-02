import os
from openai import OpenAI
import requests
import json
from pydantic import BaseModel,Field
from typing import Optional

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


class EventExtraction(BaseModel):
    description :str=Field(description="Raw description of the event")
    is_calender :bool=Field(description='Whether this text describes a calender event')
    confidence_score :float=Field(description='confidence scofre between 0 and 1')
    

def event_extraction(user_input:str)->EventExtraction:
    messages = [{"role":"system","content": "Yo are an helpful AI assistant"},
                {"role":"user","content":f"User input : {user_input}"}]
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=messages,
        response_format=EventExtraction
    
    )
    res = completion.choices[0].message.parsed
    return res

class EventDetails(BaseModel):
    name:str=Field(
        description="Name of the event if information is present otherwise None")
    
    event_date:str=Field(
        description="Date and Time of the event. Use ISO 8601 format if information is present otherwise None")
    
    event_duration:int=Field(
        description='Expected duration of the event in hours if information is present otherwise None')
    
    event_location:str=Field(
        description="Location of the event if information is present otherwise None")
    
    participants:list[str]=Field(
        description="List of the participant attending this event if information is present otherwise None")
    
    
def event_details(description:str)->EventDetails:
    messages = [{"role":"system","content":"You are an helpful AI assitant"},
                {"role":"user","content":f"the user query : {description}"}]
    completion = client.beta.chat.completions.parse(
        model ='gpt-4o',
        messages=messages,
        response_format=EventDetails
    )
    res = completion.choices[0].message.parsed
    return res

class EventConfirmation(BaseModel):
    confirmation_message:str=Field(
        description="A natural language confirmation message")
    
    calendar_link:Optional[str]=Field(
        description="Generate calender link if applicable")
    
    
def event_confirmation(event_details:EventDetails)->EventConfirmation:
    messages = [{
        "role":"system","content":"Generate a natural language confirmation email and sign off with your name Ahtsham Hussain, Lead Data Scientist",
        "role":"user","content":str(event_details.model_dump())
    },]
    
    completion = client.beta.chat.completions.create(
        model ="gpt-4o",
        messages=messages,
        response_format=EventConfirmation
    )
    response = completion.choices[0].message.parsed
    return response


    
def calling_everything(user_input:str)->Optional[EventConfirmation]:
    initial_confirmation = event_extraction(user_input)
    if initial_confirmation.is_calender and initial_confirmation.confidence_score>.75:
        event_detail = event_details(initial_confirmation.description)
        confirmation = event_confirmation(event_detail)
        return confirmation #res2.name,res2.event_date,res2.event_duration,res2.event_duration,res2.participants
    else:
        return None
        
    

#calling_everything('Ahmed and Ayesha are going for a science fest called Innovtor hub On Saturday, 25 July,It is an all day camp starting from 6 a.m. till 4p.m.')

user_input = "Let's schedule a 1h team meeting next Tuesday at 2pm with Alice and Bob to discuss the project roadmap"


final_result = calling_everything(user_input)

if final_result:
    print(f'Confirmation message',{final_result.confirmation_message})
    if final_result.calendar_link:
        print("Calendar link",f'{final_result.calendar_link}')
else:
    "This doest appear a calender event"