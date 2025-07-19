from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import os

load_dotenv()
model = ChatGoogleGenerativeAI(model=os.getenv("LLM_MODEL"))

mysql_prompt = PromptTemplate(
    input_variables=["schema", "chat_history", "question"],
    template="""Given the following database schema and conversation history, generate a SQL query to answer the user's new question.

Database schema:
{schema}

Conversation history:
{chat_history}

New question: {question}

Please provide only the SQL query without any explanation."""
)

final_response_prompt = PromptTemplate(
    input_variables=["chat_history", "query", "results"],
    template="""Given the conversation history, the SQL query that was executed, and the query results, formulate a natural language response to the user's question. Do not mention the SQL query or the database tables in your response.

Conversation history:
{chat_history}

SQL query: {query}

Query results: {results}

Response:"""
)

mysql_chain = mysql_prompt | model
final_response_chain = final_response_prompt | model

def generate_query(schema: str, chat_history: str, question: str):
    query_raw = mysql_chain.invoke({"schema": schema, "chat_history": chat_history, "question": question}).content
    query = query_raw.replace("```sql\n", "").replace("```", "").strip()
    return query

def generate_response(chat_history: str, query: str, results: str):
    response = final_response_chain.invoke({"chat_history": chat_history, "query": query, "results": results}).content
    return response