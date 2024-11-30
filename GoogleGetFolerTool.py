# from typing import Optional
import json
# from langchain_core.tools import BaseTool
# from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from getCredentials import getCredentials

@tool
def google_drive_lister(folder_id=None, mime_type=None):
    """
        Useful for listing documents in Google Drive.
        Retrieves a list of documents with their IDs and names.

        Example call:

        google_drive_lister('12121212121') or google_drive_lister('12121212121', "csv")
    
        Args:
            folder_id (str, optional): ID of the folder to list documents from
            mime_type (str, optional): Filter by specific MIME type
        
        Returns:
            List of dictionaries with 'id' and 'name' keys
    """

    try:
        # Build the Drive v3 API client
        service = build('drive', 'v3', credentials=getCredentials())

        # Construct the query
        query_parts = []
        
        # Add folder filter if specified
        if folder_id:
            query_parts.append(f"'{folder_id}' in parents")
        
        # Add MIME type filter if specified
        if mime_type:
            query_parts.append(f"mimeType='{mime_type}'")
        
        # Add custom query if provided
        # if query:
        #     query_parts.append(query)
        
        # Combine query parts
        full_query = ' and '.join(query_parts) if query_parts else None
        
        # Execute the list request
        results = service.files().list(
            q=full_query,
            spaces='drive',
            fields='files(id, name)',
            # pageSize=max_results
        ).execute()
        
        # Extract files
        files = results.get('files', [])
        
        # Transform to list of dictionaries with id and name
        document_list = [
            {
                'id': file['id'], 
                'name': file['name']
            } for file in files
        ]
        
        return json.dumps(document_list, indent=2)
    
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


# More advance tool definition

# class GoogleDriveDocumentListerTool(BaseTool):
#     """
#     Langchain tool to list documents from Google Drive
#     """
#     name: str = "google_drive_document_lister"
#     description: str = (
#         "Useful for listing documents in Google Drive. "
#         "Retrieves a list of documents with their IDs and names. "
#         "Optional parameters for filtering by folder, file type, or search query."
#     )

#     def _run(
#         self, 
#         folder_id: Optional[str] = None, 
#         mime_type: Optional[str] = None,
#         query: Optional[str] = None,
#         max_results: int = 100
#     ) -> List[Dict[str, str]]:
#         """
#         List documents from Google Drive
        
#         Args:
#             folder_id (str, optional): ID of the folder to list documents from
#             mime_type (str, optional): Filter by specific MIME type
#             query (str, optional): Additional search query
#             max_results (int, optional): Maximum number of results to return
        
#         Returns:
#             List of dictionaries with 'id' and 'name' keys
#         """
#         try:
            
#             # Build the Drive v3 API client
#             service = build('drive', 'v3', credentials=getCredentials())
            
#             # Construct the query
#             query_parts = []
            
#             # Add folder filter if specified
#             if folder_id:
#                 query_parts.append(f"'{folder_id}' in parents")
            
#             # Add MIME type filter if specified
#             if mime_type:
#                 query_parts.append(f"mimeType='{mime_type}'")
            
#             # Add custom query if provided
#             if query:
#                 query_parts.append(query)
            
#             # Combine query parts
#             full_query = ' and '.join(query_parts) if query_parts else None
            
#             # Execute the list request
#             results = service.files().list(
#                 q=full_query,
#                 spaces='drive',
#                 fields='files(id, name)',
#                 pageSize=max_results
#             ).execute()
            
#             # Extract files
#             files = results.get('files', [])
            
#             # Transform to list of dictionaries with id and name
#             document_list = [
#                 {
#                     'id': file['id'], 
#                     'name': file['name']
#                 } for file in files
#             ]
            
#             return document_list
        
#         except HttpError as error:
#             print(f"An error occurred: {error}")
#             return []

#     async def _arun(
#         self, 
#         folder_id: Optional[str] = None, 
#         mime_type: Optional[str] = None,
#         query: Optional[str] = None,
#         max_results: int = 100
#     ) -> List[Dict[str, str]]:
#         """
#         Async version of the document lister
#         """
#         return self._run(folder_id, mime_type, query, max_results)

# # Pydantic input model for structured input
# class GoogleDriveDocumentListerInput(BaseModel):
#     folder_id: Optional[str] = Field(None, description="ID of the folder to list documents from")
#     mime_type: Optional[str] = Field(None, description="Filter by specific MIME type")
#     query: Optional[str] = Field(None, description="Additional search query")
#     max_results: int = Field(100, description="Maximum number of results to return")

# # Function to create the tool
# def create_google_drive_lister_tool():
#     """
#     Create and return the Google Drive Document Lister Tool
#     """
#     return GoogleDriveDocumentListerTool(
#         name="google_drive_document_lister",
#         description="List documents from Google Drive with their IDs and names",
#         args_schema=GoogleDriveDocumentListerInput
#     )
