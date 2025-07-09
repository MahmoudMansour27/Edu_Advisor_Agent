import sys
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import os
from PyPDF2 import PdfReader
from pptx import Presentation
from docx import Document
import mcp.types as types
from mcp.shared.exceptions import McpError
import shutil
import pathspec
import asyncio
import os
from dotenv import load_dotenv
from brave_search_python_client import (
    BraveSearch,
    CountryCode, 
    ImagesSearchRequest, 
    LanguageCode, 
    NewsSearchRequest,
    VideosSearchRequest, 
    WebSearchRequest
)
import requests
from bs4 import BeautifulSoup
import mysql.connector




# get root path argument
# try:
#     ROOT_PATH = sys.argv[1]
# except Exception as e:
#     print("Error: ", e, file=sys.stderr)
#     sys.exit(1)
ROOT_PATH = "/home/mahmoud/Documents/Work/Freelance/Upwork/Edu_Advisor_Agent/resourses"

# Brave Search API
load_dotenv()
api_key = os.getenv('BRAVE_SEARCH_API_KEY')
if not api_key:
    msg = "BRAVE_SEARCH_API_KEY not found in environment"
    raise ValueError(msg)

# Database connection
db_conn = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '',
    database = 'edu_adv_db'
)

cursor = db_conn.cursor()


# Server
mcp = FastMCP('FileSystem')


# helpers
def get_MIME_type(path: str) -> str:
    '''
    Get the MIME type of a file based on its extension.

    Args:
    path (str): The file path.

    Returns:
    str: The MIME type of the file.
    '''

    ext = os.path.splitext(path)[1].lower()
    mime_types = {
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".py": "text/x-python",
        ".js": "text/javascript",
        ".json": "application/json",
        ".html": "text/html",
        ".css": "text/css",
        ".csv": "text/csv",
        ".xml": "application/xml",
        ".yaml": "application/x-yaml",
        ".yml": "application/x-yaml",
        '.pdf': 'application/pdf',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    }
    return mime_types.get(ext, "application/octet-stream")


def is_safe_path(path: str, root_path: str) -> bool:
    """
    Check if the given path is a safe path within the root path.

    Args:
    path (str): The path to check.
    root_path (str): The root path.

    Returns:
    bool: True if the path is safe, False otherwise.
    """

    if not root_path:
        return False
    

    abs_path = os.path.abspath(os.path.join(root_path, path))
    if not abs_path.startswith(root_path):
        return False
    return True

def read_pdf(path: str) -> str:
    '''
    Read the content of a PDF file.
    
    Args:
    path (str): The path to the PDF file.

    Returns:
    str: The text content of the PDF file.
    '''
    pdf_loader = PdfReader(open(path, "rb"))
    pdf_text = ""
    for page_num in range(len(pdf_loader.pages)):
        pdf_page = pdf_loader.pages[page_num]
        pdf_text += pdf_page.extract_text()
    return pdf_text

def read_pptx(path: str) -> str:
    '''
    Read the content of a PowerPoint file.

    Args:
    path (str): The path to the PowerPoint file.

    Returns:
    str: The text content of the PowerPoint file.
    '''
    presentation = Presentation(path)
    text = ""
    for slide in presentation.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + "\n"
    return text

def read_docx(path: str) -> str:
    '''
    Read the content of a Word document.

    Args:
    path (str): The path to the Word document.

    Returns:
    str: The text content of the Word document.
    '''
    doc = Document(path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


# Resourses -----------------------
@mcp.resource("resources://ListOfResources")
def list_all_root_path_resources() -> list[types.Resource]:
    '''
    List all resources in the root path.
    Returns:
        list[types.Resource]: A list of resources in the root path.
    '''

    resources = []
    for root, _, files in os.walk(ROOT_PATH):
        for file in files:
            full_path = os.path.join(root, file)
            relpath = os.path.relpath(full_path, ROOT_PATH)
            uri = f'file://{relpath}'
            resources.append(types.Resource(
                uri=uri,
                name=relpath,
                description=f"File: {file}", 
                path=full_path,
                mimeType= get_MIME_type(full_path)
                ))
    return resources

@mcp.resource("resources://recouresTextContent")
def read_resources_content() -> dict[str, str]:
    '''
    Read the text content of all resources in the root path.

    Returns:
        dict[str, str]: A dictionary with resource names as keys and their content as values.
    '''
    resources = {}
    for root, _, files in os.walk(ROOT_PATH):
        for file in files:
            full_path = os.path.join(root, file)
            relpath = os.path.relpath(full_path, ROOT_PATH)
            mime_type = get_MIME_type(full_path)
            if mime_type == "application/pdf":
                content = read_pdf(full_path)
            elif mime_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                content = read_pptx(full_path)
            elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                content = read_docx(full_path)
            else:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            resources[relpath] = content
    return resources



# Prompts ---------------------------------
@mcp.prompt("summarize_file_content")
def summarize_file_content(file_path: str) -> list[base.Message]:
    '''
    Summarize the content of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        list[base.Message]: The summarized content of the file.
    '''
    if not is_safe_path(file_path, ROOT_PATH):
        return [base.Message("Error: File path is not safe.")]

    mime_type = get_MIME_type(file_path)
    content = ""
    if mime_type == "application/pdf":
        content = read_pdf(file_path)
    elif mime_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        content = read_pptx(file_path)
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        content = read_docx(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

    return [
        base.UserMessage('I want to summarize the content {content} of the file {file_path}.'),
        base.AssistantMessage('Here is the summarized content of the file {file_path}.'),
    ]

@mcp.prompt("create_a_study_plan")
def create_a_study_plan(file_path: str) -> list[base.Message]:
    '''
    Create a study plan for the content of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        list[base.Message]: The study plan for the content of the file.
    '''
    if not is_safe_path(file_path, ROOT_PATH):
        return [base.Message("Error: File path is not safe.")]

    mime_type = get_MIME_type(file_path)
    content = ""
    if mime_type == "application/pdf":
        content = read_pdf(file_path)
    elif mime_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        content = read_pptx(file_path)
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        content = read_docx(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

    return [
        base.UserMessage('I want to create a study plan for the content {content} of the file {file_path}.'),
        base.AssistantMessage('Here is the study plan for the content of the file {file_path}.'),
    ]



# Tools ---------------------------------
@mcp.tool('Write-file')
def Write_file(file_path: str, content: str, create_dirs: bool | None) -> bool:
    '''
    Write content to a file.

    Args:
        file_path (str): The path to the file.
        content (str): The content to write to the file.
        create_dirs (bool | None): Whether to create directories if they do not exist.

    Returns:
        bool: True if the file was written successfully, False otherwise.
    '''

    if not file_path or not content:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )
    
    full_path = os.path.join(ROOT_PATH, file_path)

    try:
        if create_dirs:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as file:
            file.write(content)
        
        return [
            types.TextContent(
                type= 'text',
                text= f"File {file_path} written successfully."
            )
        ]
    except Exception as e: 
        raise McpError(
            types.ErrorData(
                code= types.INTERNAL_ERROR, 
                message= f"Failed to write file {file_path}. Error: {str(e)}"
            )
        )
    

@mcp.tool('Delete-file')
def Delete_file(file_path: str) -> bool:
    '''
    Delete a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file was deleted successfully, False otherwise.
    '''

    if not file_path:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )

    full_path = os.path.join(ROOT_PATH, file_path)

    try:
        os.remove(full_path)
        return [
            types.TextContent(
                type= 'text',
                text= f"File {file_path} deleted successfully."
            )
        ]
    except Exception as e: 
        raise McpError(
            types.ErrorData(
                code= types.INTERNAL_ERROR, 
                message= f"Failed to delete file {file_path}. Error: {str(e)}"
            )
        )
    
@mcp.tool('Delete-directory')
def Delete_directory(directory_path: str) -> bool:
    '''
    Delete a directory.

    Args:
        directory_path (str): The path to the directory.

    Returns:
        bool: True if the directory was deleted successfully, False otherwise.
    '''

    if not directory_path:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )

    full_path = os.path.join(ROOT_PATH, directory_path)

    try:
        shutil.rmtree(full_path)
        return [
            types.TextContent(
                type= 'text',
                text= f"Directory {directory_path} deleted successfully."
            )
        ]
    except Exception as e: 
        raise McpError(
            types.ErrorData(
                code= types.INTERNAL_ERROR, 
                message= f"Failed to delete directory {directory_path}. Error: {str(e)}"
            )
        )
    
@mcp.tool('Searh-text-in-files')
def Search_file(search_text: str, file_pattern: str = '*') -> bool:
    '''
    Search for a text in all files.

    Args:
        search_text (str): The text to search for.
        file_pattern (str): The file pattern to search in. Default is '*'.

    Returns:
        bool: True if the text was found, False otherwise.
    '''

    if not search_text:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )

    results = []
    for root, _, files in os.walk(ROOT_PATH):
        for file in files:
            full_path = os.path.join(root, file)
            
            if not pathspec.Pattern(file_pattern).match_file(file):
                continue

            # search into file content
            try:
                if get_MIME_type(full_path) == 'application/pdf':
                    try:
                        content = read_pdf(full_path)
                        if search_text.lower() in content.lower():
                            rel_path = os.path.relpath(full_path, ROOT_PATH)
                            results.append(f'Found in {rel_path}')
                    except Exception as e:
                        raise McpError(
                            types.ErrorData(
                                code= types.INTERNAL_ERROR, 
                                message= f"Failed to read file: {full_path} for searching. Error: {str(e)}"
                            )
                        )
                elif get_MIME_type(full_path) == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
                    try:
                        content = read_pptx(full_path)
                        if search_text.lower() in content.lower():
                            rel_path = os.path.relpath(full_path, ROOT_PATH)
                            results.append(f'Found in {rel_path}')
                    except Exception as e:
                        raise McpError(
                            types.ErrorData(
                                code= types.INTERNAL_ERROR, 
                                message= f"Failed to read file: {full_path} for searching. Error: {str(e)}"
                            )
                        )
                elif get_MIME_type(full_path) == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    try:
                        content = read_docx(full_path)
                        if search_text.lower() in content.lower():  
                            rel_path = os.path.relpath(full_path, ROOT_PATH)
                            results.append(f'Found in {rel_path}')
                    except Exception as e:
                        raise McpError(
                            types.ErrorData(
                                code= types.INTERNAL_ERROR, 
                                message= f"Failed to read file: {full_path} for searching. Error: {str(e)}"
                            )
                        )
                else:
                    try:
                        with open(full_path, 'r') as file:
                            content = file.read()
                            if search_text.lower() in content.lower():
                                rel_path = os.path.relpath(full_path, ROOT_PATH)
                                results.append(f'Found in {rel_path}')
                    except Exception as e:
                        raise McpError(
                            types.ErrorData(
                                code= types.INTERNAL_ERROR, 
                                message= f"Failed to read file: {full_path} for searching. Error: {str(e)}"
                            )
                        )
            except Exception as e:
                raise McpError(
                    types.ErrorData(
                        code= types.INTERNAL_ERROR, 
                        message= f"Failed to search file {full_path}. Error: {str(e)}"
                    )
                )
            
            if not results:
                return [
                    types.TextContent(
                        type= 'text',
                        text= f"No files found matching the query '{search_text}' with pattern '{file_pattern}'."
                    )
                ]
            
            return [
                    types.TextContent(
                        type= 'text',
                        text= f"Files found matching the query '{search_text}' with pattern '{file_pattern}':\n" + "\n".join(results)
                    )
                ]

@mcp.tool('Move-file')
def Move_file(source_path: str, destination_path: str) -> bool:
    '''
    Move a file to a new location.

    Args:
        source_path (str): The path to the source file.
        destination_path (str): The path to the destination directory.

    Returns:
        bool: True if the file was moved successfully, False otherwise.
    '''

    if not source_path or not destination_path:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )

    full_source_path = os.path.join(ROOT_PATH, source_path)
    full_destination_path = os.path.join(ROOT_PATH, destination_path)

    try:
        if os.path.isdir(destination_path):
            shutil.move(full_source_path, full_destination_path)
            return [
                types.TextContent(
                    type= 'text',
                    text= f"File {source_path} moved to {destination_path} successfully."
                )
            ]
        else:
            raise McpError(
                        types.ErrorData(
                            code= types.INVALID_PARAMS, 
                            message= f"Invalid destination path: {destination_path}."
                        )
                    )
    except Exception as e: 
        raise McpError(
            types.ErrorData(
                code= types.INTERNAL_ERROR, 
                message= f"Failed to move file {source_path} to {destination_path}. Error: {str(e)}"
            )
        )
    
@mcp.tool('move-directory')
def Move_directory(source_path: str, destination_path: str) -> bool:
    '''
    Move a directory to a new location.

    Args:
        source_path (str): The path to the source directory.
        destination_path (str): The path to the destination directory.

    Returns:
        bool: True if the directory was moved successfully, False otherwise.
    '''

    if not source_path or not destination_path:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )

    full_source_path = os.path.join(ROOT_PATH, source_path)
    full_destination_path = os.path.join(ROOT_PATH, destination_path)

    try:
        if os.path.isdir(full_source_path) and os.path.isdir(full_destination_path):
            shutil.move(full_source_path, full_destination_path)
            return [
                types.TextContent(
                    type= 'text',
                    text= f"Directory {source_path} moved to {destination_path} successfully."
                )
            ]
        else:
            raise McpError(
                        types.ErrorData(
                            code= types.INVALID_PARAMS, 
                            message= f"Invalid destination path: {destination_path}."
                        )
                    )
    except Exception as e: 
        raise McpError(
            types.ErrorData(
                code= types.INTERNAL_ERROR, 
                message= f"Failed to move directory {source_path} to {destination_path}. Error: {str(e)}"
            )
        )
    
@mcp.tool('Copy-file')
def Copy_file(source_path: str, destination_path: str) -> bool:
    '''
    Copy a file to a new location.

    Args:
        source_path (str): The path to the source file.
        destination_path (str): The path to the destination directory.

    Returns:
        bool: True if the file was copied successfully, False otherwise.
    '''

    if not source_path or not destination_path:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )

    full_source_path = os.path.join(ROOT_PATH, source_path)
    full_destination_path = os.path.join(ROOT_PATH, destination_path)

    try:
        if os.path.isfile(full_source_path) and os.path.isdir(full_destination_path):
            shutil.copy(full_source_path, full_destination_path)
            return [
                types.TextContent(
                    type= 'text',
                    text= f"File {source_path} copied to {destination_path} successfully."
                )
            ]
        else:
            raise McpError(
                        types.ErrorData(
                            code= types.INVALID_PARAMS, 
                            message= f"Invalid destination path: {destination_path} or source path {source_path}."
                        )
                    )
    except Exception as e: 
        raise McpError(
            types.ErrorData(
                code= types.INTERNAL_ERROR, 
                message= f"Failed to copy file {source_path} to {destination_path}. Error: {str(e)}"
            )
        )
    
@mcp.tool('Copy-directory')
def Copy_directory(source_path: str, destination_path: str) -> bool:
    '''
    Copy a directory to a new location.

    Args:
        source_path (str): The path to the source directory.
        destination_path (str): The absolute path to the destination directory.

    Returns:
        bool: True if the directory was copied successfully, False otherwise.
    '''

    if not source_path or not destination_path:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )

    full_source_path = os.path.join(ROOT_PATH, source_path)
    full_destination_path = os.path.join(ROOT_PATH, destination_path)

    try:
        if os.path.isdir(full_source_path) and os.path.isdir(full_destination_path):
            shutil.copytree(full_source_path, full_destination_path)
            return [
                types.TextContent(
                    type= 'text',
                    text= f"Directory {source_path} copied to {destination_path} successfully."
                )
            ]
        else:
            raise McpError(
                        types.ErrorData(
                            code= types.INVALID_PARAMS, 
                            message= f"Invalid destination path: {destination_path} or source path {source_path}."
                        )
                    )
    except Exception as e: 
        raise McpError(
            types.ErrorData(
                code= types.INTERNAL_ERROR, 
                message= f"Failed to copy directory {source_path} to {destination_path}. Error: {str(e)}"
            )
        )
    


# ----------------------- Brave Search -----------------------

@mcp.tool('Brave-Search')
async def Brave_Search(query: str, count: int = 10) -> list:
    '''
    Search the query using Brave Search API.

    Arguments:
    query (str): Searching query.
    count (int): Number of results to return. Default is 10.

    Returns:
    list: List of results links.
    '''

    # Initialize the BraveSearch client
    brave_search = BraveSearch(api_key= api_key)


    print(brave_search)
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


@mcp.tool('Get-latest-unversity-news')
def Get_latest_unversity_news(count: int = 3) -> list:
    '''
    Get the latest news about universities using requests.

    Returns:
    count (int): Number of news articles to return.
    list: List of news articles.
    '''

    uni_news_url = 'https://su.edu.eg/index.php/homepage_read_all_news/'
    
    # request
    req = requests.get(uni_news_url)

    if req.status_code != 200:
        raise McpError(
            types.ErrorData(
                code= types.INTERNAL_ERROR, 
                message= f"Failed to fetch university news. Status code: {req.status_code}"
            )
        )
    
    # extract news articles
    soup = BeautifulSoup(req.text, 'html.parser')

    news_articles = []
    for article in soup.find_all('h3', class_='gdlr-core-blog-title gdlr-core-skin-title'):
        request_url = article.find('a')['href']
        new_req = requests.get(request_url)
        soup_article = BeautifulSoup(new_req.text, 'html.parser')
        new = {
            'url': article.find('a')['href'],
            'title': article.find('a').get_text(strip=True),
            'content': soup_article.find_all('p')
        }
        news_articles.append(new)

        if len(news_articles) >= count:
            break

    return news_articles


# --------------------------- Database connection ---------------------------
@mcp.tool('StudentProfile_retrieve')
def StudentProfile_retrieve(student_id: str) -> dict:
    '''
    StudentProfile table: Stores personal and academic information for each student, including ID, name, major, advisor, and current status.
    Retrieve a student profile from the database based on student id.

    Args:
        student_id (str): The ID of the student.

    Returns:
        dict: The student profile.
    '''

    columns = [
        'student_id',
        'name',
        'birthdate',
        'nationality',
        'contact', 
        'enrollment_date',
        'major',
        'advisor',
        'status'
    ]

    if not student_id:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )
    else:
        student_id = student_id.strip().upper()
        sql = f"SELECT * FROM StudentProfile WHERE student_id = '{student_id}'"
        cursor.execute(sql)
        result = cursor.fetchall()
        data = []
        for row in result:
            student = {
                columns[0]: row[0],
                columns[1]: row[1],
                columns[2]: row[2],
                columns[3]: row[3],
                columns[4]: row[4],
                columns[5]: row[5],
                columns[6]: row[6],
                columns[7]: row[7],
                columns[8]: row[8]
            }
            data.append(student)

    if not data:
        raise McpError(
            types.ErrorData(
                code= types.NOT_FOUND, 
                message= f"Student with ID {student_id} not found."
            )
        )
    
    # check for testing
    # elif len(data) > 1:
    #     raise McpError(
    #         types.ErrorData(
    #             code= types.INTERNAL_ERROR, 
    #             message= f"Multiple students found with ID {student_id}. Please check the database."
    #         )
    #     )

    return data[0]



@mcp.tool('Student_AcademicRecords_retrieve')
def Student_AcademicRecords_retrieve(student_id: str) -> list[dict]:
    '''
    AcademicRecords table: Stores academic records for each student, including course ID, course_code, couse_name, semester, credits, GPA.
    Retrieve academic records for a student from the database based on student id.

    Args:
        student_id (str): The ID of the student.

    Returns:
        list: A list of academic records for the student.
    '''

    columns = [
        'record_id', 
        'student_id', 
        'course_code', 
        'course_name', 
        'semester', 
        'grade', 
        'credits', 
        'GPA'
    ]

    if not student_id:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )
    else:
        student_id = student_id.strip().upper()
        sql = f"SELECT * FROM AcademicRecords WHERE student_id = '{student_id}'"
        cursor.execute(sql)
        result = cursor.fetchall()
        data = []
        for row in result:
            record = {
                columns[0]: row[0],
                columns[1]: row[1],
                columns[2]: row[2],
                columns[3]: row[3],
                columns[4]: row[4],
                columns[5]: row[5],
                columns[6]: row[6],
                columns[7]: row[7]
            }
            data.append(record)

    if not data:
        raise McpError(
            types.ErrorData(
                code= types.NOT_FOUND, 
                message= f"Academic records for student with ID {student_id} not found."
            )
        )

    return data

@mcp.tool('CourseCatalog_retrieve')
def CourseCatalog_retrieve(course_code: str) -> dict:  
    '''
    CourseCatalog table: Stores information about courses, including course code, name, credits, and department.
    Retrieve a course from the database based on course code.

    Args:
        course_code (str): The code of the course.

    Returns:
        dict: The course information.
    '''

    columns = [
        'course_code',
        'name',
        'credits',
        'department'
    ]

    if not course_code:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )
    else:
        course_code = course_code.strip().upper()
        sql = f"SELECT * FROM CourseCatalog WHERE course_code = '{course_code}'"
        cursor.execute(sql)
        result = cursor.fetchall()
        data = []
        for row in result:
            course = {
                columns[0]: row[0],
                columns[1]: row[1],
                columns[2]: row[2],
                columns[3]: row[3]
            }
            data.append(course)

    if not data:
        raise McpError(
            types.ErrorData(
                code= types.NOT_FOUND, 
                message= f"Course with code {course_code} not found."
            )
        )

    return data[0]

@mcp.tool('Student_courses_enrollment_retrieve')
def Student_courses_enrollment_retrieve(student_id: str) -> list[dict]:
    '''
    Enrollment table: Records students’ enrollment status in courses per semester, including student ID, course code, semester, enrollment status and attendance_percent.
    Retrieve enrollment information for a student in a course from the database based on student id.

    Args:
        student_id (str): The ID of the student.

    Returns:
        list: A list of enrollment records for the student.
    '''

    columns = [
        'enrollment_id',
        'student_id',
        'course_code',
        'semester',
        'enrollment_status',
        'attendance_percent'
    ]

    if not student_id:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required argument for tool."
            )
        )
    
    student_id = student_id.strip().upper()
    
    sql = f"SELECT * FROM Enrollment WHERE student_id = '{student_id}'"
    cursor.execute(sql)
    result = cursor.fetchall()
    data = []
    for row in result:
        enrollment = {
            columns[0]: row[0],
            columns[1]: row[1],
            columns[2]: row[2],
            columns[3]: row[3],
            columns[4]: row[4],
            columns[5]: row[5]
        }
        data.append(enrollment)

    if not data:
        raise McpError(
            types.ErrorData(
                code= types.NOT_FOUND, 
                message= f"Enrollment record for student with ID {student_id} in course {course_code} not found."
            )
        )

    return data


@mcp.tool('Students_AdvisingNotes_retrieve')
def Students_AdvisingNotes_retrieve(student_id: str) -> list[dict]:
    '''
    AdvisingNotes table: Stores advising notes for each student, including student ID, advisor ID, date, meeting summary, recommendations, and follow up date.
    Retrieve advising notes for a student from the database based on student id.

    Args:
        student_id (str): The ID of the student.

    Returns:
        list: A list of advising notes for the student.
    '''

    columns = [
        'note_id',
        'student_id',
        'advisor_id',
        'date',
        'meeting_summary',
        'recommendations',
        'follow_up_date'
    ]

    if not student_id:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )
    
    student_id = student_id.strip().upper()
    
    sql = f"SELECT * FROM AdvisingNotes WHERE student_id = '{student_id}'"
    cursor.execute(sql)
    result = cursor.fetchall()
    data = []
    for row in result:
        note = {
            columns[0]: row[0],
            columns[1]: row[1],
            columns[2]: row[2],
            columns[3]: row[3],
            columns[4]: row[4],
            columns[5]: row[5],
            columns[6]: row[6]
        }
        data.append(note)

    if not data:
        raise McpError(
            types.ErrorData(
                code= types.NOT_FOUND, 
                message= f"Advising notes for student with ID {student_id} not found."
            )
        )

    return data


@mcp.tool('Semester_AcademicCalendar_retrieve')
def Semester_AcademicCalendar_retrieve(semester: str) -> dict:
    '''
    AcademicCalendar table: Contains important academic dates for each semester, including semester name, start date, end date, registration deadline, and exam period.
    Retrieve the academic calendar for a specific semester from the database.

    Args:
        semester (str): The name of the semester.

    Returns:
        dict: The academic calendar for the specified semester.
    '''

    columns = [
        'semester',
        'start_date',
        'end_date',
        'registration_deadline',
        'exam_period'
    ]

    if not semester:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )
    
    semester = semester.strip().upper()
    
    sql = f"SELECT * FROM AcademicCalendar WHERE semester = '{semester}'"
    cursor.execute(sql)
    result = cursor.fetchall()
    data = []
    for row in result:
        calendar = {
            columns[0]: row[0],
            columns[1]: row[1],
            columns[2]: row[2],
            columns[3]: row[3],
            columns[4]: row[4]
        }
        data.append(calendar)

    if not data:
        raise McpError(
            types.ErrorData(
                code= types.NOT_FOUND, 
                message= f"Academic calendar for semester {semester} not found."
            )
        )

    return data[0]


@mcp.tool('Departments_information_retrieve')
def Departments_information_retrieve(department_name: str) -> dict:
    '''
    Departments table: Contains information about university departments, including department id, name, contact info, faculty members, and office hours.
    Retrieve information about a specific department from the database based on department name.

    Args:
        department_name (str): The name of the department.

    Returns:
        dict: The information about the specified department.
    '''

    columns = [
        'department_id',
        'name',
        'contact_info',
        'faculty_members',
        'office_hours'
    ]

    if not department_name:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )
    
    department_name = department_name.strip().title()
    
    sql = f"SELECT * FROM DepartmentFaculty WHERE name = '{department_name}'"
    cursor.execute(sql)
    result = cursor.fetchall()
    data = []
    for row in result:
        department = {
            columns[0]: row[0],
            columns[1]: row[1],
            columns[2]: row[2],
            columns[3]: row[3],
            columns[4]: row[4]
        }
        data.append(department)

    if not data:
        raise McpError(
            types.ErrorData(
                code= types.NOT_FOUND, 
                message= f"Department {department_name} not found."
            )
        )

    return data[0]


@mcp.tool('GraduationRequirements_per_major_retrieve')
def GraduationRequirements_per_major_retrieve(major: str) -> dict:
    '''
    GraduationRequirements table: Contains graduation requirements for each major, including major name, required credits, core courses, electives, and capstone project.
    Retrieve graduation requirements for a specific major from the database based on major name.

    Args:
        major (str): The name of the major.

    Returns:
        dict: The graduation requirements for the specified major.
    '''

    columns = [
        'major',
        'required_credits',
        'core_courses',
        'electives',
        'capstone_project'
    ]

    if not major:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )
    
    major = major.strip().title()
    
    sql = f"SELECT * FROM GraduationRequirements WHERE major = '{major}'"
    cursor.execute(sql)
    result = cursor.fetchall()
    data = []
    for row in result:
        requirements = {
            columns[0]: row[0],
            columns[1]: row[1],
            columns[2]: row[2],
            columns[3]: row[3],
            columns[4]: row[4]
        }
        data.append(requirements)

    if not data:
        raise McpError(
            types.ErrorData(
                code= types.NOT_FOUND, 
                message= f"Graduation requirements for major {major} not found."
            )
        )

    return data[0]


@mcp.tool('Internships_Opportunities_retrieve')
def Internships_Opportunities_retrieve() -> list[dict]:
    '''
    Internships table: Contains information about internship opportunities, including company, role, requirements, deadline, and status.
    Retrieve open internship opportunities at current time.

    Returns:
        list: A list of open internship opportunities.
    '''

    columns = [
        'opportunity_id',
        'company',
        'role',
        'requirements',
        'deadline',
        'status'
    ]
    
    sql = f"SELECT * FROM Internships WHERE status = 'Open'"
    cursor.execute(sql)
    result = cursor.fetchall()
    data = []
    for row in result:
        internship = {
            columns[0]: row[0],
            columns[1]: row[1],
            columns[2]: row[2],
            columns[3]: row[3],
            columns[4]: row[4],
            columns[5]: row[5]
        }
        data.append(internship)

    if not data:
        raise McpError(
            types.ErrorData(
                code= types.NOT_FOUND, 
                message= "No open internship opportunities found."
            )
        )

    return data


@mcp.tool('Students_FinancialRecords_retrieve')
def Students_FinancialRecords_retrieve(student_id: str) -> list[dict]:
    '''
    FinancialRecords table: Stores financial records for each student, including student ID, tuition fees, payments, scholarships, and outstanding balance.
    Retrieve financial records for a student from the database based on student id.

    Args:
        student_id (str): The ID of the student.

    Returns:
        list: A list of financial records for the student.
    '''

    columns = [
        'financial_id',
        'student_id',
        'tuition_fees',
        'payments',
        'scholarships',
        'outstanding_balance'
    ]

    if not student_id:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )
    
    student_id = student_id.strip().upper()
    
    sql = f"SELECT * FROM FinancialRecords WHERE student_id = '{student_id}'"
    cursor.execute(sql)
    result = cursor.fetchall()
    data = []
    for row in result:
        record = {
            columns[0]: row[0],
            columns[1]: row[1],
            columns[2]: row[2],
            columns[3]: row[3],
            columns[4]: row[4],
            columns[5]: row[5]
        }
        data.append(record)

    if not data:
        raise McpError(
            types.ErrorData(
                code= types.NOT_FOUND, 
                message= f"Financial records for student with ID {student_id} not found."
            )
        )

    return data


@mcp.tool('Students_ExtracurricularActivities_retrieve')
def Students_ExtracurricularActivities_retrieve(student_id: str) -> list[dict]:
    '''
    ExtracurricularActivities table: Contains information about extracurricular activities, including student ID, activity name, role, and hours.
    Retrieve extracurricular activities for a student from the database based on student id.

    Args:
        student_id (str): The ID of the student.

    Returns:
        list: A list of extracurricular activities for the student.
    '''

    columns = [
        'activity_id',
        'student_id',
        'activity_name',
        'role',
        'hours'
    ]

    if not student_id:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )
    
    student_id = student_id.strip().upper()
    
    sql = f"SELECT * FROM ExtracurricularActivities WHERE student_id = '{student_id}'"
    cursor.execute(sql)
    result = cursor.fetchall()
    data = []
    for row in result:
        activity = {
            columns[0]: row[0],
            columns[1]: row[1],
            columns[2]: row[2],
            columns[3]: row[3],
            columns[4]: row[4]
        }
        data.append(activity)

    if not data:
        raise McpError(
            types.ErrorData(
                code= types.NOT_FOUND, 
                message= f"Extracurricular activities for student with ID {student_id} not found."
            )
        )

    return data


@mcp.tool('Students_AttendanceBehavior_retrieve')
def Students_AttendanceBehavior_retrieve(student_id: str) -> list[dict]:
    '''
    AttendanceBehavior table: Records attendance rates and behavior notes per student for specific courses, including student ID, course code, attendance percent, and behavior notes.
    Retrieve attendance and behavior records for a student from the database based on student id.

    Args:
        student_id (str): The ID of the student.

    Returns:
        list: A list of attendance and behavior records for the student.
    '''

    columns = [
        'behavior_id',
        'student_id',
        'course_code',
        'attendance_percent',
        'behavior_notes'
    ]

    if not student_id:
        raise McpError(
            types.ErrorData(
                code= types.INVALID_PARAMS, 
                message= f"Missing required arguments for tool."
            )
        )
    
    student_id = student_id.strip().upper()
    
    sql = f"SELECT * FROM AttendanceBehavior WHERE student_id = '{student_id}'"
    cursor.execute(sql)
    result = cursor.fetchall()
    data = []
    for row in result:
        record = {
            columns[0]: row[0],
            columns[1]: row[1],
            columns[2]: row[2],
            columns[3]: row[3],
            columns[4]: row[4]
        }
        data.append(record)

    if not data:
        raise McpError(
            types.ErrorData(
                code= types.NOT_FOUND, 
                message= f"Attendance and behavior records for student with ID {student_id} not found."
            )
        )

    return data



    
    
