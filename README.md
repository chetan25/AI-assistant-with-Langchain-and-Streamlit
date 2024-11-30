---
Title: AI assistant with Langchain and Streamlit.
Excerpt: Simple AI assistant that can talk to Google Drive docs and create tasks in Asana.
Tech: "Streamlit, Python, Langchain, Asana API, Google API"
---

# AI assistant to read Google docs and create tasks in Asana

Simple AI assistant built with Python backend and Streamlit UI talking to Open AI model via Langchain.

## Prerequisite

- Rename the `.env.example` to `.env`.

- [Google Cloud](https://cloud.google.com/) Credentials:

  - Set up Google Cloud Console credentials.
  - Download OAuth credentials JSON file.
  - Update the `/credentials.json` file content with the downloaded file content.

- [Asana Account](https://asana.com/create-account):

  - Create Asana account.
  - Follow this [Doc](https://developers.asana.com/docs/personal-access-token) to create the API token and update the `.env` file.

- [Open AI](https://platform.openai.com):

  - Create an Open AI account if you don't have one.
  - Get the API key and update the `env` file.

## Local Development

This is built using Python virtual environment. Assuming python is installed, I have provided the `requirement.txt` with all the dependencies. You can either create a new virtual env or install the deps directly.

```py
# install dependencies
pip install -r requirements.txt

# run locally
streamlit run main-langchian.py
```

---

NOTE:
The first time you run the script, you'll need to authenticate to google.
You need to provide the permissions to access the Google drive.

---

## Workflows Tools

We have 3 Langchain tools created:

- `create_asana_task` - Tool for creating task in Asana. This uses Asana APIs.
- `google_doc_tool` - This tool is use to read content of the Google Document.
- `google_drive_lister` - This tool is use for listing the folders/files of a Google drive folder.

## User Flow

User can perform certain task:

- Read content of Google Drive folder.
- Read the content of Google document.
- Can summarize or create task from the document in Asana.
- Or create new task in Asana.

### Common MIME types for filtering:

- Google Docs: 'application/vnd.google-apps.document'
- Google Sheets: 'application/vnd.google-apps.spreadsheet'
- Google Slides: 'application/vnd.google-apps.presentation'
- PDFs: 'application/pdf'
