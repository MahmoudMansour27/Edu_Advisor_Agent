
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

load_dotenv()
api_key = os.getenv('BRAVE_SEARCH_API_KEY')
if not api_key:
    msg = "BRAVE_SEARCH_API_KEY not found in environment"
    raise ValueError(msg)
print(api_key)

async def search(query: str) -> None:
    '''
    Search the query using Brave Search API.

    Argruments:
    query (str): Searching query.

    Returns (str): List of results links.
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


print(asyncio.run(search('gold prices in Egypt twoday')))
