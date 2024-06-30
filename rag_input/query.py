import openai
import os
from dotenv import load_dotenv
import pinecone
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

openai.api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

load_dotenv()

# Initialize the client

pc = Pinecone(
    api_key=os.environ.get("PINECONE_API_KEY")
)


# Connect to your index
index = pc.Index('wikipedia-small')

def get_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding

def get_document_content(doc_id, results):
    for match in results['matches']:
        if match['id'] == doc_id:
            return match['metadata']['text']
    return "Document not found."

def generate_response_with_documents(query, documents):
    context = "\n\n".join(documents)
    prompt = f"Context: {context}\n\nQuery: {query}\n\nResponse:"
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=200
    )
    return response.choices[0].text.strip()


query = "What are Elon Musk's view on technology?"

# Generate embedding for the query
query_embedding = get_embedding(query)

# Query Pinecone
results = index.query(vector=query_embedding, top_k=5,include_metadata=True)

# Retrieve document contents
document_ids = [match['id'] for match in results['matches']]
documents = [get_document_content(doc_id, results) for doc_id in document_ids]


response_text = generate_response_with_documents(query, documents)
print(response_text)
