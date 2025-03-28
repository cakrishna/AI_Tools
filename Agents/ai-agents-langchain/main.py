from dotenv import load_dotenv
from pydantic import BaseModel
# from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
# from tools import search_tool, wiki_tool, save_tool
from tools import search_tool, wiki_tool, save_tool

load_dotenv()


# import LLAMA using Groq in langchain
from langchain_groq import ChatGroq
llm = ChatGroq(model="llama-3.3-70b-versatile")
# # llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
# responce = llm.invoke("tell me a joke")
# print(responce)


# createing prompt template using python class
# it is to specify the type of content we want llm to generate. .
class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

# parer for above model responce into python.
parser = PydanticOutputParser(pydantic_object=ResearchResponse)
# create the chat prompt Template for the LLM
# "system" message is the info we give to the llm like a instruction.
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a research assistant that will help generate a research paper.
            Answer the user query and use neccessary tools. 
            Wrap the output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())
# .partial is using our parser tp conver the basemodel in to a string and give it to the prompt.
# format_instructions can be any name


# create a simple AI Agent and execute it
tools = [search_tool, wiki_tool, save_tool]
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools,
    # tools=[],
)

# withoput tools.py
# agent_executor = AgentExecutor(agent=agent, tools=[], verbose=True)
# raw_response = agent_executor.invoke({"query": "What is the capital of england?"})
# print(raw_response)

# With tools.py
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
query = input("What can i help you research? ")
raw_response = agent_executor.invoke({"query": query})

try:
    structured_response = parser.parse(raw_response.get("output")[0]["text"])
    print(structured_response)
except Exception as e:
    print("Error parsing response", e, "Raw Response - ", raw_response)