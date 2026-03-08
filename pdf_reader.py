from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.ollama import Ollama

llm = Ollama(model="llama3")

documents = SimpleDirectoryReader("documents").load_data()

index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()


def ask_pdf(question):
    response = query_engine.query(question)
    return str(response)