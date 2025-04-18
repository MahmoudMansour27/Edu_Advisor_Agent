from mcp.server.fastmcp import FastMCP
import os
from pypdf import PdfReader


mcp = FastMCP('FileSystem')
subjects_folders = os.listdir('./resourses')
lectures = os.listdir('./resourses/'+subjects_folders[0])
print(lectures)
print(lectures.sort())


#Resourses
@mcp.resource('dm://Lectures')
def read_DM_Lecturs():
    '''
    
    '''
    lectures = []
    for file in os.listdir('./resourses/'+ subjects_folders[subjects_folders.index('Digital Multimedia')]):
        pass