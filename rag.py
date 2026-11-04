
import os
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer


# 1. Load embedding model
print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")


# 2. Study material folder
DATA_FOLDER = "study_materials"


# 3. Read and split documents
def load_documents():

    chunks = []

    for filename in os.listdir(DATA_FOLDER):

        if filename.endswith(".txt"):

            path = os.path.join(DATA_FOLDER, filename)

            with open(path, "r", encoding="utf-8") as file:
                content = file.read()

            # Split content into smaller chunks
            paragraphs = [
                p.strip()
                for p in content.split("\n\n")
                if p.strip()
            ]

            for paragraph in paragraphs:

                chunks.append({
                    "text": paragraph,
                    "source": filename
                })

    return chunks


# 4. Create FAISS vector database
def create_vector_store(chunks):

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    return index


# 5. Retrieve relevant study materials
def retrieve_documents(question, chunks, index, top_k=3):

    query_embedding = model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    k = min(top_k, len(chunks))

    scores, indices = index.search(query_embedding, k)

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx >= 0:
            results.append({
                "text": chunks[idx]["text"],
                "source": chunks[idx]["source"],
                "score": float(score)
            })

    return results


# 6. Run RAG system
if __name__ == "__main__":

    chunks = load_documents()

    if not chunks:
        raise ValueError(
            "No study materials found in study_materials folder."
        )

    print("Documents loaded:", len(chunks))

    index = create_vector_store(chunks)

    print("FAISS vector database created successfully.")

    question = input("\nAsk your study question: ")

    results = retrieve_documents(
        question,
        chunks,
        index
    )

    print("\n===== RETRIEVED STUDY MATERIALS =====")

    for i, result in enumerate(results, 1):

        print(f"\nResult {i}")
        print("Source:", result["source"])
        print("Similarity:", round(result["score"], 3))
        print("Content:", result["text"])


# 7. Reusable knowledge base for LangGraph

_cached_chunks = None
_cached_index = None


def retrieve_for_question(question, top_k=3):
    global _cached_chunks, _cached_index

    if _cached_chunks is None:
        _cached_chunks = load_documents()

        if not _cached_chunks:
            raise ValueError("No study materials found.")

        _cached_index = create_vector_store(_cached_chunks)

    return retrieve_documents(
        question,
        _cached_chunks,
        _cached_index,
        top_k
    )

