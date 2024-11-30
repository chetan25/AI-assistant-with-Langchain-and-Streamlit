from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import json
import os
import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage

from GoogleDocumentLoaderTool import create_google_document_tool
from GoogleGetFolerTool import google_drive_lister
from CreateTaskAsana import create_asana_task

load_dotenv()

client = OpenAI()
model = os.getenv("OPEN_AI_MODEL", "gpt-4o")


# configuration = asana.Configuration()
# configuration.access_token = os.getenv("ASANA_ACCESS_TOKEN", "")
# api_client = asana.ApiClient(configuration)

# tasks_api_instance = asana.TasksApi(api_client)


# Create the tool
google_doc_tool = create_google_document_tool()

def ask_ai(messages, nested_calls = 0):
    """
        This function invokes the AI Agent
        Example call:

        ask_ai(messages, nested_calls)

        Args:
            messages (List): List of Messages containing the Human and AI responses.
            nested_calls (int): Count to keep track how many times the LLM is invoked.
        Returns:
            str: The Api response in chunks for streaming    
    """
    if nested_calls > 5:
        raise Exception("AI is tool calling too much")
    
    # first prompt ai with latest user message
    tools = [create_asana_task, google_doc_tool, google_drive_lister]
    ai_chatbot = ChatOpenAI(model=model)
    ai_chatbot_with_tools = ai_chatbot.bind_tools(tools)
   
    # ai_response = ai_chatbot_with_tools.invoke(messages)

    stream = ai_chatbot_with_tools.stream(messages)
    
    first = True
    for chunk in stream:
        if first:
            gathered = chunk
            first = False
        else:
            gathered = gathered + chunk

        yield chunk       

    has_tool_calls = len(gathered.tool_calls) > 0
     
    if has_tool_calls:
        available_tools = {
          "create_asana_task": create_asana_task,
          "google_doc_tool": google_doc_tool,
          "google_drive_lister": google_drive_lister,
          "google_document_loader": google_doc_tool, 
        } 
        # messages.append(ai_response)
        messages.append(gathered)

        for tool_call in gathered.tool_calls:
            tool_name = tool_call["name"].lower()
            tool_to_call = available_tools[tool_name]
            try:
                tool_output = tool_to_call.invoke(tool_call["args"])

                # Append a ToolMessage with the tool output and associate it with tool_call_id
                messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))

            except Exception as e:
                print(f"Error invoking tool {tool_name}: {e}")
                raise Exception("failed")

        # ai_response = ask_ai(messages, nested_calls + 1)
        additional_stream = ask_ai(messages, nested_calls + 1)
        for additional_chunk in additional_stream:
            yield additional_chunk

    # return ai_response


def main():
    st.title("AI Chatbot")
    
    # initialize chat history once as st will re run on every change
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content=f"You are a personal assistant who helps manage interaction with Google Drive and create taska in Asana. The current date is {datetime.now().date()}")
        ]

    # display messages from history in ui
    for message in st.session_state.messages:
        message_json = json.loads(message.json())
        with st.chat_message(message_json["type"]):
            st.markdown(message_json["content"])
    
    if prompt := st.chat_input("What would you like to do today"):
        # display user message in chat message container
        st.chat_message("user").markdown(prompt)

        st.session_state.messages.append(HumanMessage(content=prompt))

        #display assistant respone in chat
        with st.chat_message("assistant"):
            # ai_response = ask_ai(st.session_state.messages)
            # st.markdown(ai_response.content)

            # stream
            stream = ask_ai(st.session_state.messages)
            response = st.write_stream(stream)

        st.session_state.messages.append(AIMessage(content=response))    



if __name__ == '__main__':
    main()    