import openai
from dotenv import load_dotenv
from openai import OpenAI
import os
from langchain.prompts import PromptTemplate
from datetime import datetime, timedelta
from nicegui import ui
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

env_loaded = load_dotenv()
print("Environment loaded:", env_loaded)



client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('calendar', 'v3', credentials=creds)



def get_conv(chat):
    
    chat_string = ''
    for message in chat:            
        chat_string += f"{message['timestamp']} - {message['user']}: {message['text']} \n"
    
    return chat_string


context = """ 

You are an AI agent working for {user}. You take actions if needed based on the conversation provided.    

conversation: {chat}
"""

auto_res = """ 

You are an auto respond agent working for the user {user}. 
You observe the user's writing style and auto responds like the user. 

conversation: {chat}


{user}: 

"""

answer_prompt = PromptTemplate(template=context, input_variables=['chat', 'user'])

auto_respond_prompt = PromptTemplate(template=auto_res, input_variables=['chat','user'])
#formatted_prompt = answer_prompt.format(chat=get_conv(chat) )

def create_event(start_time, description, conference=False, end_time=30, location=None, summary=None):
    """
    Creates a Google Calendar event given the start_time and description as args.
    Also takes in kwargs like end_time, location, summary.
    end_time is by default set to 30mins after start time. 
    location and summary default to None.
    """

    
    
    # Parse the start time to a datetime object
    start_datetime = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
    
    # Calculate the end time by adding the duration to the start time
    end_datetime = start_datetime + timedelta(minutes=end_time)

    # Create the event body
    event = {
        'description': description,
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'CET',  # Adjust time zone as needed
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'CET',  # Adjust time zone as needed
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    # Add location if provided
    if location:
        event['location'] = location
    
    # Add summary if provided
    if summary:
        event['summary'] = summary
    else:
        event['summary'] = 'New event'
    
    # Add conference data if conference is set to True
    if conference:
        event['conferenceData'] = {
            'createRequest': {
                'requestId': 'sample123', 
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet'
                },
            }
        }

    # Print the event for debugging
    print(event)
        
    if start_datetime < datetime.now() - timedelta(minutes=5):
        return "Start time cannot be in the past"
    else:
        event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1 if conference else 0).execute()
        
        if conference:
            meet_link = event.get('conferenceData').get('entryPoints')[0].get('uri')
            return f"Join the meeting - Google Meet link: {meet_link}"
        else:
            return f"Event created: {event.get('htmlLink')}"
        

def run_conversation(query):
    
    
    
    messages=[
                {"role": "system", "content": "You are an AI agent"},
                {"role": "user", "content": query}
            ]
    
    tools = [
        
        
        {
            "type": "function",
            "function": {
                
                "name": "create_event",
                "description": "Creates a google calander event given the start_time and description as args. Also takes in kwargs like end_time, location, summary. end_time is by default set to 30. location and summary defaults to None",
                "parameters": {
                    
                    "type": "object",
                    "properties": {
                        
                        "start_time": {
                            
                            "type": "string",
                            "description": "Start time of the event, in a datetime format string, you need current time to adjust this event ",
                        },
                        
                        "description": {
                            
                            "type": "string",
                            "description": "Description of the event",
                        },
                        
                        "end_time": {
                            
                            "type": "integer",
                            "description": "duration of the event, by default set to 30",
                        },
                        
                        "location": {
                            
                            "type": "string",
                            "description": "location of the event, by default set to None",
                        },
                        
                        "conference": {
                            
                            "type": "boolean",
                            "description": "Gives a google meet link for the meeting if it's virtual"
                            
                        },
                        
                        "summary": {
                            
                            "type": "string",
                            "description": "summary of the event, with time and place (this will be sent to the user)"
                        },
                        
                        
                        
                    }
                }
            }
            
        }    
    ]
    
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