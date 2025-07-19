
# from langchain import LLMChain
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

load_dotenv()
model = ChatGoogleGenerativeAI(model=os.getenv("LLM_MODEL"))

mysql_prompt=PromptTemplate(
    input_variables=["schema", "question"],
    template="Given the following database schema: {schema}\n\nGenerate a SQL query to answer the question: {question}",
    
)
final_response_prompt=PromptTemplate(
    input_variables=["query", "results"],
    template="Given the SQL query: {query}\n\nAnd the results: {results}\n\nFormulate a natural language response that answers the user's question without mentioning the mysql query or the database tables.",
    
)

mysql_chain = mysql_prompt | model 
final_response_chain = final_response_prompt | model 

def generate_query(schema: str, question: str):
    query_raw =  mysql_chain.invoke({"schema": schema, "question": question}).content
    query = query_raw.replace("```sql\n", "").replace("```", "").strip()
    return query

def generate_response(query: str, results: str):
    response = final_response_chain.invoke({"query": query, "results": results}).content
    return response