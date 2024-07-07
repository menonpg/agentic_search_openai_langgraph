import functools, operator
from typing import Annotated, Sequence, TypedDict

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser

from tools import get_tools

load_dotenv()

# llm = ChatOpenAI(
#   model="gpt-4-turbo-preview",
#   temperature=0,
#   verbose=True
# )
llm = ChatOpenAI(
  model="gpt-4o",
  temperature=0,
  verbose=True
)
tools = get_tools()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str):
  prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
  ])
  agent = create_openai_tools_agent(llm, tools, prompt)
  executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

  return executor

def agent_node(state, agent, name):
  result = agent.invoke(state)
  return {"messages": [HumanMessage(content=result["output"], name=name)]}

def get_members():
  return ["Web_Searcher", "Insight_Researcher"]

def create_supervisor():
  members = get_members()
  system_prompt = (
    f"""As a supervisor, your role is to oversee a dialogue between these"
    " workers: {members}. Based on the user's request,"
    " determine which worker should take the next action. Each worker is responsible for"
    " executing a specific task and reporting back their findings and progress. Once all tasks are complete,"
    " indicate with 'FINISH'.
    """
  )
  options = ["FINISH"] + members

  function_def = {
    "name": "route",
    "description": "Select the next role.",
    "parameters": {
        "title": "routeSchema",
        "type": "object",
        "properties": {"next": {"title": "Next", "anyOf": [{"enum": options}] }},
        "required": ["next"],
    },
  }

  prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("system", "Given the conversation above, who should act next? Or should we FINISH? Select one of: {options}"),
  ]).partial(options=str(options), members=", ".join(members))

  supervisor_chain = (prompt | llm.bind_functions(functions=[function_def], function_call="route") | JsonOutputFunctionsParser())

  return supervisor_chain

def create_search_agent():
  search_agent = create_agent(llm, tools, "You are a web searcher. Search the internet for information.")
  search_node = functools.partial(agent_node, agent=search_agent, name="Web_Searcher")

  return search_node

def create_insights_researcher_agent():
  insights_research_agent = create_agent(llm, tools,
    """You are a Insight Researcher. Do step by step.
    Based on the provided content first identify the list of topics,
    then search internet for each topic one by one
    and finally find insights for each topic one by one.
    Include the insights and sources in the final response
    """)
  insights_researcher_node = functools.partial(agent_node, agent=insights_research_agent, name="Insight_Researcher")

  return insights_researcher_node