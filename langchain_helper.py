from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql  import SQLDatabaseChain
from model import llm
from langchain.prompts.prompt import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from few_shots import few_shots
from langchain_community.vectorstores import Chroma
from langchain.prompts import SemanticSimilarityExampleSelector
from langchain.chains.sql_database.prompt import PROMPT_SUFFIX, _mysql_prompt
from langchain.prompts import FewShotPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",
                              sample_rows_in_table_info=3)


# prompt = PromptTemplate(
#     input_variables=["input", "table_info", "top_k"],
#     template="""
# Based on the table schema below, write a valid MySQL query that answers the user's question.
# Return ONLY the SQL query — do NOT include any markdown, backticks, or formatting. Just plain SQL.

# Schema:
# {table_info}

# Question: {input}
# SQL Query:
# """,
# )
# db_chain = SQLDatabaseChain.from_llm(llm,db,prompt=prompt,verbose=True) 
# qnsl = db_chain.invoke("how many white color thshirt of brand nike we have?")

# embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
# to_vectorize = [" ".join(example.values()) for example in few_shots]


# vectorestore = Chroma.from_texts(to_vectorize,embedding=embeddings,metadatas=few_shots)

# example_selector=SemanticSimilarityExampleSelector(vectorstore=vectorestore,k=2)

# a=example_selector.select_examples({"question":"how many  Adidas tshirt i have left in my store?"})
# print(a)

# mysql_prompt = """You are a MySQL expert. Given an input question, first create a syntactically correct MySQL query to run, then look at the results of the query and return the answer to the input question.
#     Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per MySQL. You can order the results to return the most informative data in the database.
#     Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in backticks (`) to denote them as delimited identifiers.
#     Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
#     Pay attention to use CURDATE() function to get the current date, if the question involves "today".
    
#     Use the following format:
    
#     Question: Question here
#     SQLQuery: Query to run with no pre-amble
#     SQLResult: Result of the SQLQuery
#     Answer: Final answer here
    
#     No pre-amble.
#     """
    
# example_prompt = PromptTemplate(
#         input_variables=["Question", "SQLQuery", "SQLResult","Answer",],
#         template="\nQuestion: {Question}\nSQLQuery: {SQLQuery}\nSQLResult: {SQLResult}\nAnswer: {Answer}",
#     )

# few_shot_prompt = FewShotPromptTemplate(
#         example_selector=example_selector,
#         example_prompt=example_prompt,
#         prefix=mysql_prompt,
#         suffix=PROMPT_SUFFIX,
#         input_variables=["input", "table_info", "top_k"],
#     )

def get_few_shot_db_chain():
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    to_vectorize = [" ".join(example.values()) for example in few_shots]


    vectorestore = Chroma.from_texts(
        to_vectorize,
        embedding=embeddings,
        metadatas=few_shots,
        persist_directory="./chroma_db"  
    )

    example_selector=SemanticSimilarityExampleSelector(vectorstore=vectorestore,k=2)
        
    example_prompt = PromptTemplate(
            input_variables=["Question", "SQLQuery", "SQLResult","Answer",],
            template="\nQuestion: {Question}\nSQLQuery: {SQLQuery}\nSQLResult: {SQLResult}\nAnswer: {Answer}",
        )
    mysql_prompt = """
        You are a MySQL expert. Given an input question, first create a syntactically correct MySQL query to run, then look at the results of the query and return the answer to the input question.
    Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per MySQL. You can order the results to return the most informative data in the database.
    Never query for all columns from a table. You must query only the columns that are needed to answer the question. 
    Wrap only each column name in backticks (`) to denote them as delimited identifiers not whole query.
    Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    Pay attention to use CURDATE() function to get the current date, if the question involves "today".There must be not "```sql","```" etc.
    If your tells you to delete or update stock or alter table and anything tell them you don't have right to do this and return query SELECT -999 + 0 AS result;
    if the SQLResult=[(-999,)] then as a answer return -999 
    
    Question: Question here
    SQLQuery: SQL Query to run(without ```sql and ```. I will manage by my self just do not include ```)
    SQLResult: Result of the SQLQuery
    Answer: Final answer here (in natural lanaguage like answer of the question "how many Adidas tshirt i have left in my store?" should be "There are 23 tshirts available in the store.If the SQLResult=[(-999,)] then as a answer return -999 "
    
    """
    few_shot_prompt = FewShotPromptTemplate(
            example_selector=example_selector,
            example_prompt=example_prompt,
            prefix=mysql_prompt,
            suffix=PROMPT_SUFFIX,
            input_variables=["input", "table_info", "top_k"],
        )
    
    print(few_shot_prompt)
    chain = SQLDatabaseChain.from_llm(llm,db,prompt=few_shot_prompt,verbose=True) 
    return chain

if __name__ == "__main__" :
    chain=get_few_shot_db_chain()
    print(chain.invoke("how many  Adidas tshirt i have left in my store?"))