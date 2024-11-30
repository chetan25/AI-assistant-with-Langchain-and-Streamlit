from datetime import datetime
import os
import json
from asana.rest import ApiException
import asana
from langchain_core.tools import tool

# Function to create and return a single instance of TasksApi
def get_tasks_api_instance():
    """Creates and returns a single instance of TasksApi."""
    # Use a static variable to store the instance
    if not hasattr(get_tasks_api_instance, "_instance"):
        # Configuration for Asana API
        configuration = asana.Configuration()
        configuration.access_token = os.getenv("ASANA_ACCESS_TOKEN", "")  # Fetch token from environment
        
        # Create ApiClient
        api_client = asana.ApiClient(configuration)
        
        # Initialize TasksApi and store it as a static variable
        get_tasks_api_instance._instance = asana.TasksApi(api_client)
    
    # Return the singleton instance
    return get_tasks_api_instance._instance

@tool
def create_asana_task(task_name, due_on="today"):
    """
    Create a task in Asana given the name of the task and when it is due

    Example call:

    create_asana_task('Test task', '2024-07-22')
    Args:
        task_name (str): The name of the taks in Asana
        due_on (str): The date the task is due in the format of: YYYY-MM-DD, if not given the current day is used
    Returns:
        str: The Api response of adding the task to Asana or an error message if the API calls threw an error    
    """

    tasks_api_instance = get_tasks_api_instance()
    if due_on == 'today':
        due_on = str(datetime.now().date())

    # asana payload
    task_body = {
        "data": {
            "name": task_name,
            "due_on": due_on,
            "projects": [os.getenv("ASANA_PROJECT_ID", "")]
        }
    }

    try:
        api_response = tasks_api_instance.create_task(task_body, {})
        return json.dumps(api_response, indent=2)
    except ApiException as e:
        return f"Exception when calling TaskApi: {e}"