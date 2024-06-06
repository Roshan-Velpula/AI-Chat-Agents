import openai
from dotenv import load_dotenv
from openai import OpenAI
import os

from datetime import datetime, timedelta
from nicegui import ui
import json
from utils import create_event,answer_prompt, auto_respond_prompt, tools_list,get_conv


env_loaded = load_dotenv()
print("Environment loaded:", env_loaded)



client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)









#formatted_prompt = answer_prompt.format(chat=get_conv(chat) )



def run_conversation(query):
    
    
    
    messages=[
                {"role": "system", "content": "You are an AI agent"},
                {"role": "user", "content": query}
            ]
    
    tools = tools_list
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    
 
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    return response_message

def auto_respond(chat, user):
    
    formatted_prompt = auto_respond_prompt.format(chat=get_conv(chat), user = user)
    
    response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant"},
                {"role": "user", "content": formatted_prompt}
            ],
            )
    return response.choices[0].message.content


def get_tasks(chat, user):
    
    tasks = []
    functions = {}
    
    formatted_prompt = answer_prompt.format(chat=get_conv(chat), user = user)
    
    response_message = run_conversation(formatted_prompt)
    
    tool_calls = response_message.tool_calls
    if tool_calls:
        
        for tool in tool_calls:
            
            summary = json.loads(tool.function.arguments)['summary']
            
            functions[summary] = tool.function
            
            tasks.append(summary)
        
        return tasks, functions
        
    else:
        return [],{}


def execute_tasks(task, dropdown, functions, text_box):
    
    available_functions = {
        ""
        "create_event": create_event,  
    }
    
    ui.notify(f"Executing {task}")
    
    fn = functions[task]
    
    fn_name = fn.name
    
    function_to_call = available_functions[fn_name]
    function_args = json.loads(fn.arguments)
    function_response = function_to_call(**function_args)
    
    if 'conference' in function_args.keys() and function_args['conference'] == True:
            text_box.value = function_response
    else:
            
        ui.notify(f"{function_response}")
    
    dropdown.visible = False