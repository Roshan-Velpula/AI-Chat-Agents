from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from langchain.prompts import PromptTemplate
import os

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def build_service():
    
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

    return service

def create_event(start_time, description, conference=False, end_time=30, location=None, summary=None, service = build_service()):
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
        


context = """ 

You are an AI agent working for {user}. You take actions if needed based on the conversation provided.   always provide a summary argument to the tools 

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


def get_conv(chat):
    
    chat_string = ''
    for message in chat:            
        chat_string += f"{message['timestamp']} - {message['user']}: {message['text']} \n"
    
    return chat_string


tools_list = [
        
        
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