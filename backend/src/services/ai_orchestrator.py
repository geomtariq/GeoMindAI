from langchain.chains import LLMChain
from langchain_community.llms import Ollama # Using Ollama as a placeholder for a local LLM
from langchain.prompts import PromptTemplate

# This is a placeholder for a real LLM. In a production environment,
# this would be a more robust model like GPT-4, Claude 3, etc.
# For local development, we can use a local model via Ollama.
llm = Ollama(model="llama2")

class AIOrchestrator:
    def __init__(self):
        # TODO: Develop a more sophisticated prompt that includes schema info, examples, etc.
        self.query_prompt = PromptTemplate(
            input_variables=["query"],
            template="You are an expert in Oracle SQL. Convert the following natural language query into a SQL statement:\n\n{query}\n\nSQL:",
        )
        self.intent_prompt = PromptTemplate(
            input_variables=["query"],
            template="Given the query '{query}', is the user's intent to 'read' or 'write' data? Respond with only one word.",
        )
        self.query_chain = LLMChain(llm=llm, prompt=self.query_prompt)
        self.intent_chain = LLMChain(llm=llm, prompt=self.intent_prompt)


    def process_query(self, query: str) -> dict:
        """
        Takes a natural language query and returns a dictionary with the SQL statement and intent.
        """
        intent = self.intent_chain.run(query).strip().lower()
        sql = self.query_chain.run(query).strip()
        
        return {"intent": intent, "sql": sql}


ai_orchestrator = AIOrchestrator()

