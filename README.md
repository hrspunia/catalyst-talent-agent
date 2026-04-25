# ⚡ Catalyst AI: Autonomous Talent Sourcing & Engagement Pipeline

**A solo hackathon submission for Deccan AI Catalyst**

## 📖 Overview
Catalyst AI is an autonomous, end-to-end agentic workflow designed to eliminate the manual overhead of technical recruiting. It takes a raw Job Description as input, parses the core requirements, queries a local vector database of candidate profiles, and simulates a personalized outreach conversation to gauge genuine candidate interest. 

The final output is a ranked shortlist based on a composite score of **Skill Match (60%)** and **Interest Level (40%)**.

## 🏗 Architecture & Workflow

1. **Phase 1: JD Extraction Agent**
   - **Input:** Unstructured Job Description text.
   - **Action:** Processed by Groq (Llama-3.1-8b-instant) using strict JSON mode to extract the Target Role, Required Skills, and Years of Experience.
2. **Phase 2: Vector Discovery Engine**
   - **Action:** Parses the structured requirements into a semantic query. Searches a local `ChromaDB` instance containing dummy candidate profiles.
   - **Explainability:** For the top 3 matches, Llama-3 evaluates the candidate's JSON profile against the parsed JD, generating a deterministic **Match Score (0-100)** and a 2-sentence rationale explaining the fit or missing gaps.
3. **Phase 3: Conversational Engagement Simulator**
   - **Action:** To simulate real-world outreach without spamming emails, the system injects the candidate's "Hidden Interest Level" (a hidden JSON trait) into a roleplay prompt.
   - **Evaluation:** Llama-3 drafts an initial recruiter pitch, simulates the candidate's response based on their hidden persona, and evaluates the transcript to output an **Interest Score (0-100)**.

## ⚙️ Technical Stack
* **Frontend:** Streamlit (Chosen for rapid UI prototyping and state management).
* **LLM Engine:** Groq API / Llama-3.1-8b-instant (Chosen for sub-second inference speed and reliable JSON output).
* **Vector Database:** ChromaDB (Persistent local instance, utilizing Hugging Face sentence-transformers for fast, free embeddings).
* **Language:** Python 3.10+

## ⚖️ Trade-offs & Design Decisions
* **Local vs. Cloud Vector DB:** Opted for a persistent local ChromaDB instance rather than a managed cloud service to ensure zero latency during the demo and adhere strictly to free-tier constraints.
* **Simulated Outreach vs. Multi-Agent Framework:** Decided against using heavy multi-agent frameworks (like CrewAI/AutoGen) for the engagement simulator. Instead, I used chained LLM prompts with strict JSON schema enforcement via Groq. This reduced token overhead, eliminated infinite conversation loops, and drastically improved the pipeline's execution speed.
* **Scoring Weights:** Weighted the Match Score heavier (60%) than the Interest Score (40%) to ensure highly qualified but passive candidates still rank above highly interested but under-qualified candidates.

## 🚀 Run It Locally

### Prerequisites
* Python 3.10 or higher
* A free [Groq API Key](https://console.groq.com/keys)

### Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/hrspunia/catalyst-talent-agent.git](https://github.com/hrspunia/catalyst-talent-agent.git)
   cd catalyst-talent-agent