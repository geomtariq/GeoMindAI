from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama

# This is a placeholder for a real LLM. In a production environment,
# this would be a more robust model like GPT-4, Claude 3, etc.
# For local development, we can use a local model via Ollama.
llm = Ollama(model="llama2")

class AIOrchestrator:
    def __init__(self):
        # Using the new LangChain Expression Language (LCEL) syntax
        # This is more stable and the modern way to build chains.
        
        query_prompt = PromptTemplate.from_template(
            "You are an expert in Oracle SQL. Convert the following natural language query into a SQL statement:\n\n{query}\n\nSQL:"
        )
        
        intent_prompt = PromptTemplate.from_template(
            "Given the query '{query}', is the user's intent to 'read' or 'write' data? Respond with only one word."
        )
        
        output_parser = StrOutputParser()
        
        # Define the chains using the | operator (LCEL)
        self.query_chain = query_prompt | llm | output_parser
        self.intent_chain = intent_prompt | llm | output_parser

    def process_query(self, query: str) -> dict:
        """
        Takes a natural language query and returns a dictionary with the SQL statement and intent.
        """
        # Use .invoke() instead of the deprecated .run()
        intent = self.intent_chain.invoke({"query": query}).strip().lower()
        sql = self.query_chain.invoke({"query": query}).strip()
        
        return {"intent": intent, "sql": sql}

ai_orchestrator = AIOrchestrator()