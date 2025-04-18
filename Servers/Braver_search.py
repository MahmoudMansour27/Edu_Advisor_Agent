# import libraries
from brave import Brave


# client
brave = Brave()

# helping functions
def search_queries() -> list:
    """Generate list of web search queries that can help user reach
    the desired content.
    """
    queries = []
    return queries


def query() -> str:
    """Create query from use prompt
    extract keyword that most related to user prompt
    state them into mean
    """
    