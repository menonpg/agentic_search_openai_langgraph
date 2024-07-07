

"""
Certainly! If you're encountering rate limit issues with DuckDuckGo, you can switch to another search engine. One alternative is to use the Bing Search API provided by Microsoft Azure.

Steps to Use Bing Search API:
Sign Up for an API Key:

Go to the Microsoft Azure portal.
Create a new Azure account if you don't have one.
Search for the "Bing Search" service and create a new resource to get your API key.
Install Required Libraries:

You might need the requests library to make HTTP requests. If it's not already installed, you can install it using:
pip install requests

Update tools.py to Use Bing Search API:

Here's how you can update your tools.py to use the Bing Search API:

import requests
from langchain.tools import tool
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

BING_API_KEY = os.getenv("BING_API_KEY")
BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"

@tool("internet_search", return_direct=False)
def internet_search(query: str) -> str:
  # Searches the internet using Bing Search API.
  headers = {
      "Ocp-Apim-Subscription-Key": BING_API_KEY
  }
  params = {
      "q": query,
      "count": 5
  }
  response = requests.get(BING_SEARCH_URL, headers=headers, params=params)
  response.raise_for_status()
  search_results = response.json()

  results = []
  for result in search_results.get("webPages", {}).get("value", []):
      results.append({
          "name": result["name"],
          "url": result["url"],
          "snippet": result["snippet"]
      })

  return results if results else "No results found."

@tool("process_content", return_direct=False)
def process_content(url: str) -> str:
  #Processes content from a webpage.
  response = requests.get(url)
  soup = BeautifulSoup(response.content, 'html.parser')
  return soup.get_text()

def get_tools():
  return [internet_search, process_content]

Explanation:
BING_API_KEY: This should be set in your .env file. Add a new entry like BING_API_KEY=your_bing_api_key_here.
BING_SEARCH_URL: The endpoint for the Bing Search API.
internet_search Function: This function makes a GET request to the Bing Search API with the query and headers. It processes the response to extract relevant information (like the title, URL, and snippet) from the search results.
Update Your .env File:
Make sure your .env file contains your Bing API key:

LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=
OPENAI_API_KEY=
BING_API_KEY=your_bing_api_key_here

With these changes, your application should now use the Bing Search API for internet searches, potentially avoiding the rate limit issues you experienced with DuckDuckGo.

"""

import requests

from langchain.tools import tool
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup


@tool("internet_search_DDGO", return_direct=False)
def internet_search_DDGO(query: str) -> str:

  """Searches the internet using DuckDuckGo."""

  with DDGS() as ddgs:
    results = [r for r in ddgs.text(query, max_results=5)]
    return results if results else "No results found."

@tool("process_content", return_direct=False)
def process_content(url: str) -> str:

    """Processes content from a webpage."""

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()

# def get_tools():
#   return [internet_search_DDGO, process_content]

import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
import streamlit as st
load_dotenv()

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

@tool("internet_search", return_direct=False)
def internet_search(query: str) -> str:
    """Searches the internet using Tavily."""
    search_tool = TavilySearchResults(api_key=TAVILY_API_KEY, max_results=5)
    results = search_tool.invoke(query)

    # Log the raw results for debugging purposes
    print("Raw results:", results)

    if isinstance(results, list) and all(isinstance(result, dict) for result in results):
        formatted_results = ""
        references = []
        for i, result in enumerate(results):
            title = result.get('title', 'No Title')
            url = result.get('url', 'No URL')
            snippet = result.get('snippet', 'No Snippet')
            formatted_results += f"{i+1}. {title}\n{snippet} [^{i+1}]\n\n"
            references.append(f"[^{i+1}]: [{title}]({url})")

        references_section = "\n**References:**\n" + "\n".join(references)
        return formatted_results + references_section

    else:
        return "Unexpected result format. Please check the Tavily API response structure."

def get_tools():
    # return [internet_search, internet_search_DDGO]
    # return [internet_search]
    return [internet_search_DDGO, process_content]