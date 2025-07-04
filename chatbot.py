import os
import requests
from vector_store import VectorStore

class BWTSChatbot:
    def __init__(self, groq_api_key=None, model_name="llama3-8b-8192"):
        self.vector_store = VectorStore()
        self.api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = model_name

    def answer_query(self, query: str):
        # Step 1: Retrieve relevant documents
        results = self.vector_store.search(query, n_results=3)

        documents = [res["content"] for res in results]
        metadatas = [res["metadata"] for res in results]

        context = "\n\n".join(documents)

        if not context.strip():
            return "I couldn’t find anything relevant in the documents.", []

        # Step 2: Build the prompt
        user_prompt = f"""You are a technical assistant for Ballast Water Treatment System (BWTS) manuals.

Use the context below to answer the user's question.

Context:
{context}

Question:
{query}

Answer:"""

        # Step 3: Call Groq API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 700
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            answer = result["choices"][0]["message"]["content"].strip()
            return answer, metadatas

        except requests.exceptions.HTTPError as e:
            return f"❌ HTTP Error {e.response.status_code}: {e.response.text}", []

        except Exception as e:
            return f"❌ Unexpected error: {str(e)}", []
