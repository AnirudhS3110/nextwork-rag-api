from fastapi import FastAPI
import chromadb
import ollama
import uuid

client = chromadb.PersistentClient(path="./db")
container = client.get_collection("docs")
ollama_client = ollama.Client(host="http://127.0.0.1:11434")

app = FastAPI()

@app.post("/query")
def query(q: str):
    res = container.query(query_texts=[q], n_results=1, include=["documents"])
    context = res["documents"][0][0] if res["documents"] else ""

    answer = ollama_client.generate(
        model="tinyllama",
        prompt=f"Context:\n{context}\n\nQuestion: {q}\n\nAnswer clearly and concisely:",
        options={
            "num_predict": 2000
        }
    )

    return {"answer": answer["response"]}

@app.post("/add")
def addNew(description: str):
    try:
        id = str(uuid.uuid4)
        container.add(documents=[description], ids=[id])
        return {
            "status":201,
            "message":"Successfully added context!",
            "id":id
        }
    except Exception as e:
        return {
            "status":500,
            "message": f"Error: {e}"
        }