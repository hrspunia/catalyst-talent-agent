import json
import chromadb

print("🚀 Starting Database Setup...")

# Create a permanent database folder on your hard drive
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="candidates_db")

try:
    with open("data/candidates.json", "r") as file:
        candidates = json.load(file)
        
    docs, metas, ids = [], [], []
    for idx, c in enumerate(candidates):
        docs.append(f"Role: {c.get('current_role', '')}. Skills: {', '.join(c.get('skills', []))}. Experience: {c.get('years_of_experience', 0)} years.")
        metas.append(c)
        ids.append(str(c.get('id', f"cand_{idx}")))

    print("🧠 Embedding candidates into vector space (This might take a minute)...")
    collection.add(documents=docs, metadatas=metas, ids=ids)
    print(f"✅ Success! {len(candidates)} candidates embedded and saved to the 'chroma_db' folder.")
    
except Exception as e:
    print(f"❌ Error: {e}")