import os
from typing import Optional, List

from langchain_core.documents import Document
from langchain_core.tools import BaseTool
# from langchain_core.pydantic_v1 import BaseModel, Field
from pydantic import BaseModel, Field
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

import json
import io
import re
import PyPDF2
import docx
import pandas as pd

from getCredentials import getCredentials

class GoogleDocumentLoaderTool(BaseTool):
    """
    Langchain tool to extract content from a Google Drive document
    """
    name: str = "google_document_loader"
    description: str = (
        "Useful for loading and extracting text content from a Google Drive document. "
        "Input should be the Google Drive file ID. "
        "Returns the full text content of the document."
    )

    def _run(
        self, 
        file_id: str, 
        mime_type: Optional[str] = None, 
        clean_text: bool = True
    ) -> str:
        """
        Extract text content from a Google Drive document
        
        Args:
            file_id (str): The unique identifier of the file in Google Drive
            mime_type (str, optional): Specific MIME type to export as
            clean_text (bool, optional): Whether to clean up the text
        
        Returns:
            str: Full text content of the document
        """
        try:
            # Build the Drive v3 API client
            service = build('drive', 'v3', credentials=getCredentials())
            
            # Get the file metadata
            file_metadata = service.files().get(fileId=file_id).execute()
            
            # Determine export MIME type based on file type
            if mime_type is None:
                mime_types = {
                    'application/vnd.google-apps.document': 'application/pdf',
                    'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'application/vnd.google-apps.presentation': 'application/pdf',
                }
                mime_type = mime_types.get(file_metadata.get('mimeType'), 'application/pdf')
            
            # Prepare the export request
            request = service.files().export_media(
                fileId=file_id, 
                mimeType=mime_type
            )
            
            # Download the file to memory
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            # Reset file pointer to the beginning
            file_content.seek(0)
            
            # Extract text based on file type
            if mime_type == 'application/pdf':
                pdf_reader = PyPDF2.PdfReader(file_content)
                full_text = " ".join([page.extract_text() for page in pdf_reader.pages])
            
            elif mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                df = pd.read_excel(file_content)
                full_text = df.to_string()
            
            elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                doc = docx.Document(file_content)
                full_text = " ".join([para.text for para in doc.paragraphs])
            
            else:
                return "Unsupported file type for text extraction"
            
            # Clean text if requested
            if clean_text:
                full_text = re.sub(r'\s+', ' ', full_text).strip()
            
            return json.dumps(full_text, indent=2)
        
        except HttpError as error:
            return f"An error occurred: {error}"

    async def _arun(
        self, 
        file_id: str, 
        mime_type: Optional[str] = None, 
        clean_text: bool = True
    ) -> str:
        """
        Async version of the document loader
        """
        return self._run(file_id, mime_type, clean_text)

# Optional: Pydantic input model for more structured input
class GoogleDocumentLoaderInput(BaseModel):
    """
    Schema for Google Document loader tool
    """
    file_id: str = Field(..., description="Google Drive file ID")
    mime_type: Optional[str] = Field(None, description="Optional MIME type to export as")
    clean_text: bool = Field(True, description="Whether to clean up the text")

# Example usage in a Langchain agent
def create_google_document_tool():
    """
    Create and return the Google Document Loader Tool
    """
    return GoogleDocumentLoaderTool(
        name="google_document_loader",
        description="Load text content from a Google Drive document",
        args_schema=GoogleDocumentLoaderInput
    )