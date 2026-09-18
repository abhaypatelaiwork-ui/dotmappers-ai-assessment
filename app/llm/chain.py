from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.llm.client import get_llm
from app.llm.prompts import SYSTEM_PROMPT

def build_sql_chain():
   
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain

def clean_sql(raw_sql: str) -> str:
   
    sql = raw_sql.strip()
   
    if sql.startswith("```"):
        sql = sql.split("```")[1]
        if sql.startswith("sql"):
            sql = sql[3:]
    sql = sql.strip().rstrip(";") + ";"
    return sql

def generate_sql(question: str) -> str:
    
    chain = build_sql_chain()
    raw = chain.invoke({"question": question})
    return clean_sql(raw)