import os
import asyncio
import json
import mcp.types as types
import mcp.server.stdio
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.shared.exceptions import McpError
from pydantic import BaseModel, Field
from PyPDF2 import PdfReader
from pptx import Presentation
from docx import Document
from typing import Annotated
import shutil
import  sys
import pathspec



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
 

# Pydantic models
class WriteFile(BaseModel):
    '''Parameters for writing a file.'''

    path: Annotated[str, Field(description= 'The path to the file.')]
    content: Annotated[str, Field(description= 'The content to write to the file.')]
    create_dirs: Annotated[bool, Field(description= 'Whether to create directories if they do not exist.', default= False)]

class DeleteFile(BaseModel):
    '''Parameters for deleting a file.'''

    path: Annotated[str, Field(description= 'The path to the file.')]
    recursive: Annotated[bool, Field(description= 'Whether to delete directories recursively.', default= False)]

class SearchFile(BaseModel):
    '''Parameters for searching a file.'''

    query: Annotated[str, Field(description= 'The search query.')]
    file_pattern: Annotated[str, Field(description= 'The file pattern to search for.', default= '*')]

class MoveOper(BaseModel):
    '''Parameters for moving a file or folder.'''

    source_path: Annotated[str, Field(description= 'The source path of the file/ folder.')]
    destination_path: Annotated[str, Field(description= 'The destination path of the folder.')]





# Server initialization ---------------------------------
async def run_server(
        root_path: str,

) -> None:
    """
    Run the server with the given root path.
    
    Args:
    root_path (str): The root path for the server.
    """
    if not os.path.exists(root_path):
        raise ValueError(f"Root path {root_path} does not exist.")
    
    root_path = os.path.abspath(root_path)

    # server
    server = Server('filesystem')

    # resources
    @server.list_resources()
    async def list_server_resources() -> list[types.Resource]:
        """
        List all resources in the root path.
        
        Returns:
        list[types.Resource]: List of resources in the root path.
        """
        resources = []
        for root, _, files in os.walk(root_path):
            for file in files:
                full_path = os.path.join(root, file)
                relpath = os.path.relpath(full_path, root_path)
                uri = f'file://{relpath}'
                resources.append(types.Resource(
                    uri=uri,
                    name=relpath,
                    description=f"File: {file}", 
                    path=full_path,
                    mimeType= get_MIME_type(full_path)
                    ))
        return resources
    
    @server.read_resource()
    async def read_resources(uri: types.AnyUrl) -> str:
        """
        Read the content of a resource.
        
        Args:
        uri (types.AnyUrl): The URI of the resource.
        
        Returns:
        str: The content of the resource.

        Raises:
        McpError: If the resource does not exist.
        """

        if uri.scheme != 'file':
            raise McpError(
                types.ErrorData(
                    code= types.INVALID_PARAMS, 
                    message= f"Invalid URI scheme: {uri.scheme}. Expected 'file'."
                )
            )
        
        path = str(uri).replace('file://', '', 1)

        if not is_safe_path(path, root_path):
            raise McpError(
                types.ErrorData(
                    code= types.INVALID_PARAMS, 
                    message= f"Unsafe path: {path}. Path must be within the root path."
                )
            )
        
        full_path = os.path.join(root_path, path)
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            raise McpError(
                types.ErrorData(
                    code= types.INVALID_PARAMS, 
                    message= f"Resource does not exist: {full_path}."
                )
            )
        
        # read file content
        if get_MIME_type(full_path) == 'application/pdf':
            try:
                content = read_pdf(full_path)
                return content
            except Exception as e:
                raise McpError(
                    types.ErrorData(
                        code= types.INTERNAL_ERROR, 
                        message= f"Failed to read resource: {full_path}. Error: {str(e)}"
                    )
                )
        elif get_MIME_type(full_path) == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
            try:
                content = read_pptx(full_path)
                return content
            except Exception as e:
                raise McpError(
                    types.ErrorData(
                        code= types.INTERNAL_ERROR, 
                        message= f"Failed to read resource: {full_path}. Error: {str(e)}"
                    )
                )
        elif get_MIME_type(full_path) == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            try:
               content = read_docx(full_path)
               return content
            except Exception as e:
                raise McpError(
                    types.ErrorData(
                        code= types.INTERNAL_ERROR, 
                        message= f"Failed to read resource: {full_path}. Error: {str(e)}"
                    )
                )
        else:
            try:
                with open(full_path, 'r') as file:
                    content = file.read()
                    return content
            except Exception as e:
                raise McpError(
                    types.ErrorData(
                        code= types.INTERNAL_ERROR, 
                        message= f"Failed to read resource: {full_path}. Error: {str(e)}"
                    )
                )
            
    # prompts
    @server.list_prompts()
    async def list_server_prompts():
        '''List all prompts.'''
        summarize_file_content = types.Prompt(
            name = 'summarize_file_content',
            description = 'Summarize the content of a file.',
            arguments=[
                types.PromptArgument(
                    name='path',
                    description='The path to the file.',
                    required= True
                )
            ]
        )

        create_a_study_plan = types.Prompt(
            name= 'create_a_study_plan',
            description= 'Create a study plan for the file content.',
            arguments=[
                types.PromptArgument(
                    name='path',
                    description='The path to the file.',
                    required= True
                )
            ]
        )

        explain_file_content = types.Prompt(
            name= 'explain_file_content',
            description= 'Explain the content of a file.',
            arguments=[
                types.PromptArgument(
                    name='path',
                    description='The path to the file.',
                    required= True
                )
            ]
        )

        create_markdown_summary = types.Prompt(
            name= 'create_markdown_summary',
            description= 'Create a markdown summary of the file content.',
            arguments=[
                types.PromptArgument(
                    name='path',
                    description='The path to the file.',
                    required= True
                )
            ]
        )

        return [
            summarize_file_content,
            create_a_study_plan,
            explain_file_content,
            create_markdown_summary
        ]
    
    @server.get_prompt()
    async def get__specific_prompt(prompt_name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
        '''
        Get a specific prompt template.

        Arge:
        prompt_name (str): The name of the prompt.
        arguments (dict[str, str] | None): Optional arguments for the prompt.

        Returns:
        types.GetPromptResult: The prompt template with arguments filled in.

        Raises:
        McpError: If the prompt name is not found or if the arguments are invalid.
        '''

        if (
            prompt_name != 'summarize_file_content' or
            prompt_name != 'create_a_study_plan' or
            prompt_name != 'explain_file_content' or
            prompt_name != 'create_markdown_summary'
        ):
            raise McpError(
                types.ErrorData(
                    code= types.INVALID_PARAMS, 
                    message= f"Invalid prompt name: {prompt_name}. Expected 'summarize_file_content', 'create_a_study_plan', 'explain_file_content', or 'create_markdown_summary'."
                )
            )
        
        if not arguments or path not in arguments:
            raise McpError(
                types.ErrorData(
                    code= types.INVALID_PARAMS, 
                    message= f"Missing required argument 'path' for prompt {prompt_name}."
                )
            )
        
        path = arguments['path']
        if not is_safe_path(path, root_path):
            raise McpError(
                types.ErrorData(
                    code= types.INVALID_PARAMS, 
                    message= f"Unsafe path: {path}. Path must be within the root path."
                )
            )
        
        full_path = os.path.join(root_path, path)
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            raise McpError(
                types.ErrorData(
                    code= types.INVALID_PARAMS, 
                    message= f"Resource does not exist: {full_path}."
                )
            )
        
        if get_MIME_type(full_path) == 'application/pdf':
            try:
                content = read_pdf(full_path)
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role= 'user',
                            content= types.TextContent(
                                type= 'text',
                                text= f"Imagine yourself as an Educational Advisor wants to summarize a content of the file ({path}) to a student.\ncontent:\n{content}."
                            )
                        ),
                    ]
                )
            except Exception as e:
                raise McpError(
                    types.ErrorData(
                        code= types.INVALID_PARAMS, 
                        message= f"Failed to handle a resource: {full_path}. Error: {str(e)}"
                    )
                )
            
        elif get_MIME_type(full_path) == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
            try:
                content = read_pptx(full_path)
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role= 'user',
                            content= types.TextContent(
                                type= 'text',
                                text= f"Imagine yourself as an Educational Advisor wants to summarize a content of the file ({path}) to a student.\ncontent:\n{content}."
                            )
                        ),
                    ]
                )
            except Exception as e:
                raise McpError(
                    types.ErrorData(
                        code= types.INVALID_PARAMS, 
                        message= f"Failed to handle a resource: {full_path}. Error: {str(e)}"
                    )
                )
        
        elif get_MIME_type(full_path) == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            try:
                content = read_docx(full_path)
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role= 'user',
                            content= types.TextContent(
                                type= 'text',
                                text= f"Imagine yourself as an Educational Advisor wants to summarize a content of the file ({path}) to a student.\ncontent:\n{content}."
                            )
                        ),
                    ]
                )
            except Exception as e:
                raise McpError(
                    types.ErrorData(
                        code= types.INVALID_PARAMS, 
                        message= f"Failed to handle a resource: {full_path}. Error: {str(e)}"
                    )
                )
            
        else:
            try:
                with open(full_path, 'r') as file:
                    content = file.read()
                    return types.GetPromptResult(
                        messages=[
                            types.PromptMessage(
                                role= 'user',
                                content= types.TextContent(
                                    type= 'text',
                                    text= f"Imagine yourself as an Educational Advisor wants to summarize a content of the file ({path}) to a student.\ncontent:\n{content}."
                                )
                            ),
                        ]
                    )
            except Exception as e:
                raise McpError(
                    types.ErrorData(
                        code= types.INVALID_PARAMS, 
                        message= f"Failed to handle a resource: {full_path}. Error: {str(e)}"
                    )
                )
            
        # tools
        @server.list_tools()
        async def list_server_tools():
            '''lst all tools.'''

            return [
                types.Tool(
                    name= 'Write_file',
                    description= 'Write a file to the filesystem.',
                    inputSchema= WriteFile.model_json_schema()
                ),

                types.Tool(
                    name= 'Delete_file',
                    description= 'Delete a file from the filesystem.',
                    inputSchema= DeleteFile.model_json_schema()
                ),

                types.Tool(
                    name= 'Search_files',
                    description= 'Search for files in the filesystem.',
                    inputSchema= SearchFile.model_json_schema()
                ),
                types.Tool(
                    name= 'Move_oper',
                    description= 'Move a file or folder in the filesystem.',
                    inputSchema= MoveOper.model_json_schema()
                )
            ]
    
    @ server.call_tool()
    async def call_server_tool(
        name: str,
        arguments: dict[str, str] | None,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        
        '''
        Handel a tool call.
        Args:
        name (str): The name of the tool.
        arguments (dict[str, str] | None): The arguments for the tool.
        
        Returns:
        list[types.TextContent | types.ImageContent | types.EmbeddedResource]: The result of the tool call.
        '''

        if not arguments:
            raise McpError(
                types.ErrorData(
                    code= types.INVALID_PARAMS, 
                    message= f"Missing required arguments for tool {name}."
                )
            )
        
        if name == 'Write_file':
            try:
                args = WriteFile(**arguments)
            except Exception as e:
                raise McpError(
                    types.ErrorData(
                        code= types.INVALID_PARAMS, 
                        message= f"Invalid arguments for tool {name}. Error: {str(e)}"
                    )
                )
            
            full_path = os.path.join(root_path, args.path)

            try:
                if args.create_dirs:
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as file:
                    file.write(args.content)
                
                return [
                    types.TextContent(
                        type= 'text',
                        text= f"File {args.path} written successfully."
                    )
                ]
            except Exception as e: 
                raise McpError(
                    types.ErrorData(
                        code= types.INTERNAL_ERROR, 
                        message= f"Failed to write file {args.path}. Error: {str(e)}"
                    )
                )
            
        elif name == 'Delete_file':
            try:
                args = DeleteFile(**arguments)
            except Exception as e:
                raise McpError(
                    types.ErrorData(
                        code= types.INVALID_PARAMS, 
                        message= f"Invalid arguments for tool {name}. Error: {str(e)}"
                    )
                )
            
            full_path = os.path.join(root_path, args.path)

            try:
                if os.path.isdir(full_path):
                    if args.recursive:
                        shutil.rmtree(full_path)
                    else:
                        os.rmdir(full_path)
                else:
                    os.remove(full_path)
                
                return [
                    types.TextContent(
                        type= 'text',
                        text= f"File {args.path} deleted successfully."
                    )
                ]
            except Exception as e:
                raise McpError(
                    types.ErrorData(
                        code= types.INTERNAL_ERROR, 
                        message= f"Failed to delete file {args.path}. Error: {str(e)}"
                    )
                )
            
        elif name == 'Search_files':
            try:
                args = SearchFile(**arguments)
            except Exception as e:
                raise McpError(
                    types.ErrorData(
                        code= types.INVALID_PARAMS, 
                        message= f"Invalid arguments for tool {name}. Error: {str(e)}"
                    )
                )
            
            results = []
            for root, _, files in os.walk(root_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    
                    if not pathspec.Pattern(args.file_pattern).match_file(file):
                        continue

                    # search into file content
                    try:
                        if get_MIME_type(full_path) == 'application/pdf':
                            try:
                                content = read_pdf(full_path)
                                if args.query.lower() in content.lower():
                                    rel_path = os.path.relpath(full_path, root_path)
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
                                if args.query.lower() in content.lower():
                                    rel_path = os.path.relpath(full_path, root_path)
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
                                if args.query.lower() in content.lower():  
                                    rel_path = os.path.relpath(full_path, root_path)
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
                                    if args.query.lower() in content.lower():
                                        rel_path = os.path.relpath(full_path, root_path)
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
                            text= f"No files found matching the query '{args.query}' with pattern '{args.file_pattern}'."
                        )
                    ]
                
                return [
                    types.TextContent(
                        type= 'text',
                        text= f"Files found matching the query '{args.query}' with pattern '{args.file_pattern}':\n" + "\n".join(results)
                    )
                ]

        elif name == 'Move_oper':
            try:
                args = MoveOper(**arguments)
            except Exception as e:
                raise McpError(
                    types.ErrorData(
                        code= types.INVALID_PARAMS, 
                        message= f"Invalid arguments for tool {name}. Error: {str(e)}"
                    )
                )
            
            source_path = os.path.join(root_path, args.source_path)
            destination_path = os.path.join(root_path, args.destination_path)

            try:
                if os.path.isdir(destination_path):
                    shutil.move(source_path, destination_path)
                    
                    return [
                        types.TextContent(
                            type= 'text',
                            text= f"File moved from {args.source_path} to {args.destination_path} successfully."
                        )
                    ]
                else:
                    raise McpError(
                        types.ErrorData(
                            code= types.INVALID_PARAMS, 
                            message= f"Invalid destination path: {args.destination_path}."
                        )
                    )
            except Exception as e:
                raise McpError(
                    types.ErrorData(
                        code= types.INTERNAL_ERROR, 
                        message= f"Failed to move file from {args.source_path} to {args.destination_path}. Error: {str(e)}"
                    )
                )
            
        else:
            raise McpError(
                types.ErrorData(
                    code= types.INVALID_PARAMS, 
                    message= f"Invalid tool name: {name}. Expected 'Write_file' or 'Delete_file'."
                )
            )
        
    # start the server
    async with mcp.server.stdio.stdio_server() as (reader, writer):
        await server.run(
            reader,
            writer,
            InitializationOptions(
                server_name= 'filesystem',
                server_version= '1.0.0',
                capabilities= server.get_capabilities(
                    notification_options= NotificationOptions(),
                    experimental_capabilities= {}
                )
            )
        )


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python filesystem_server.py <root_path>")
        sys.exit(1)
    
    asyncio.run(run_server(sys.argv[1]))