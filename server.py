from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import os
from pypdf import PdfReader
from spire.doc import Document, FileFormat
from spire.doc.common import *
import asyncio
from dotenv import load_dotenv
from brave_search_python_client import (
    BraveSearch,
    CountryCode, 
    LanguageCode,
    WebSearchRequest
)

# Load environment variables
load_dotenv()
api_key = os.getenv('BRAVE_SEARCH_API_KEY')
if not api_key:
    msg = "BRAVE_SEARCH_API_KEY not found in environment"
    raise ValueError(msg)

mcp = FastMCP('FileSystem')
LECTURES_PATH = './resourses/'
subjects_folders = os.listdir('./resourses')


# helpers
def read_pdf(path):
    '''
    Read PDF file and return text.
    '''
    pdf = PdfReader(path)
    text = ''
    for page in pdf.pages:
        text += page.extract_text()
    return text

async def search(query: str) -> None:
    '''
    Search the query using Brave Search API.

    Argruments:
    query (str): Searching query.

    Returns (str): List of results links.
    '''
    
    # Initialize the BraveSearch client
    brave_search = BraveSearch(api_key= api_key)

    # Perform a web search
    response = await brave_search.web(
        WebSearchRequest(
            q= query,
            count= 10, 
            country= CountryCode.US,
            search_lang=LanguageCode.EN,
        )
    )
    results = []
    web = {}
    for _result in response.web.results if response.web else []:
        web['title'] = _result.title
        web['url'] = _result.url
        web['description'] = _result.description
        results.append(web)

    return results

# Resourses
@mcp.resource('dm://Lectures')
def read_DM_Lecturs():
    '''
    Digital Multimedia lectures text content.
    '''
    lectures = {}
    for i, file in enumerate(os.listdir('./resourses/'+ subjects_folders[subjects_folders.index('Digital Multimedia')])):
        if file.endswith('.pdf'):
            lectures[f'Lecture {i+1}'] = read_pdf(os.path.join(LECTURES_PATH, subjects_folders[subjects_folders.index('Digital Multimedia')], file))
    return lectures

@mcp.resource('dsp://Lectures')
def read_DM_Lecturs():
    '''
    Digital Signal Processing lectures text content.
    '''
    lectures = {}
    for i, file in enumerate(os.listdir('./resourses/'+ subjects_folders[subjects_folders.index('Digital Signal Processing')])):
        if file.endswith('.pdf'):
            lectures[f'Lecture {i+1}'] = read_pdf(os.path.join(LECTURES_PATH, subjects_folders[subjects_folders.index('Digital Signal Processing')], file))
    return lectures

@mcp.resource('ie://Lectures')
def read_DM_Lecturs():
    '''
    Information Egnineering lectures text content.
    '''
    lectures = {}
    for i, file in enumerate(os.listdir('./resourses/'+ subjects_folders[subjects_folders.index('Information Engineering')])):
        if file.endswith('.pdf'):
            lectures[f'Lecture {i+1}'] = read_pdf(os.path.join(LECTURES_PATH, subjects_folders[subjects_folders.index('Information Engineering')], file))
    return lectures

@mcp.resource('os2://Lectures')
def read_DM_Lecturs():
    '''
    Operating System 2 lectures text content.
    '''
    lectures = {}
    for i, file in enumerate(os.listdir('./resourses/'+ subjects_folders[subjects_folders.index('Operating System 2')])):
        if file.endswith('.pdf'):
            lectures[f'Lecture {i+1}'] = read_pdf(os.path.join(LECTURES_PATH, subjects_folders[subjects_folders.index('Operating System 2')], file))
    return lectures

@mcp.resource('pr://Lectures')
def read_DM_Lecturs():
    '''
    Pattern Recognition lectures text content.
    '''
    lectures = {}
    for i, file in enumerate(os.listdir('./resourses/'+ subjects_folders[subjects_folders.index('Pattern Recognition')])):
        if file.endswith('.pdf'):
            lectures[f'Lecture {i+1}'] = read_pdf(os.path.join(LECTURES_PATH, subjects_folders[subjects_folders.index('Pattern Recognition')], file))
    return lectures

# ------- 
# Prompts
# summarizr lecture
@mcp.prompt()
def summarize_lecture(subject_name: str, lecture_number: int) -> list[base.Message]:
    '''
    Summarize lecture text content.

    Argruments:
    subject_name (str): Subject name the lecture belongs to.
    lecture_number (int): Lecture number that will summarized.

    Rerturns (str): Summarized lecture text content. 
    '''
    return [
        base.UserMessage('I want to summarize the lecture text content of {lecture_number} at {subject_name} course.'),
        base.AssistantMessage('Here is the summarized lecture {lecture_number} at {subject_name} course.'),
    ] 

# study plan:
@mcp.prompt()
def study_plan(subject_name: str, lecture_number: int) -> list[base.Message]:
    '''
    Create a study plan for the lecture.

    Argruments:
    subject_name (str): Subject name the lecture belongs to.
    lecture_number (int): Lecture number that will be studied.

    Rerturns (str): Study plan for the lecture. 
    '''
    return [
        base.UserMessage('I want to create a study plan for the lecture text content of {lecture_number} at {subject_name} course.'),
        base.AssistantMessage('Here is the study plan for the lecture {lecture_number} at {subject_name} course.'),
    ]

# explain lecture content
@mcp.prompt()
def explain_lecture(subject_name: str, lecture_number: int) -> list[base.Message]:
    '''
    Explain lecture text content.

    Argruments:
    subject_name (str): Subject name the lecture belongs to.
    lecture_number (int): Lecture number that will be explained.

    Rerturns (str): Explained lecture text content. 
    '''
    return [
        base.UserMessage('I want to explain the lecture text content of {lecture_number} at {subject_name} course.'),
        base.AssistantMessage('Here is the explained lecture {lecture_number} at {subject_name} course.'),
    ]

# create markdown summary
@mcp.prompt()
def create_markdown_summary(subject_name: str, lecture_number: int) -> list[base.Message]:
    '''
    Create a markdown summary conntent for the lecture.

    Argruments:
    subject_name (str): Subject name the lecture belongs to.
    lecture_number (int): Lecture number that will be summarized.

    Rerturns (str): Summarized lecture markdown content. 
    '''
    return [
        base.UserMessage('I want to summarize the lecture text content of  {lecture_number} at {subject_name} course.'),
        base.UserMessage('Create summarization using markdown format.'),
        base.AssistantMessage('Here is the markdown file for the lecture {lecture_number} at {subject_name} course.'),
    ]

# generate lecture searching queries
@mcp.prompt()
def generate_lecture_searching_queries(subject_name: str, lecture_number: int) -> list[base.Message]:
    '''
    Generate searching queries for the lecture.

    Argruments:
    subject_name (str): Subject name the lecture belongs to.
    lecture_number (int): Lecture number that will be searched.

    Rerturns (str): Searching queries for the lecture. 
    '''
    return [
        base.UserMessage('I want to generate list of searching queries for the lecture text content of {lecture_number} at {subject_name} course.'),
        base.AssistantMessage('Here is the list of the searching queries for the lecture {lecture_number} at {subject_name} course.'),
    ]

# -----------
# Tools
# create markdown summary file
@mcp.tool()
def create_markdown_summary(markdown_summarization: str) -> str:
    '''
    Create a markdown file for the lecture.

    Argruments:
    markdown_summarization (str): Summarized lecture text content in markdown format.
    '''
    
    with open('./outputs/lecture_summary.md', 'w') as f:
        f.write(markdown_summarization)
    
    return 'file saved at /outputs/lecture_summary.md'


# Create summarized pdf
@mcp.tool()
def save_markdown_summarized_pdf() -> str:
    '''
    Save a summarized PDF file for the lecture.

    Argruments:
    path(str): Path to the summarized markdown file.
    '''
    if os.path.exists('./outputs/lecture_summary.md'):
        # Convert the markdown file to PDF
        document = Document()
        document.LoadFromFile('./outputs/lecture_summary.md')
        document.SaveToFile("./outputs/lecture_summary.pdf", FileFormat.PDF)
        return 'file saved at /outputs/lecture_summary.pdf'
    else:   
        return 'file not found at /outputs/lecture_summary.md'
    
# web search
@mcp.tool()
def web_search(queries: list) -> str:
    '''
    Search the web for the query.

    Argruments:
    queries (str): List of queries to search the web.
    '''

    responeses = []
    for q in queries:
        response = asyncio.run(search(q))
        responeses.append(response)
    return responeses

