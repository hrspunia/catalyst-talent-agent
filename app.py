import streamlit as st
import json
import os
from dotenv import load_dotenv
from groq import Groq
import chromadb

# Load environment variables silently
load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- Page Configuration & Custom CSS ---
st.set_page_config(page_title="Catalyst AI | Sourcing", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .skill-pill {
        display: inline-block;
        background-color: #1E1E1E;
        color: #FFFFFF;
        padding: 5px 12px;
        border-radius: 15px;
        margin: 3px;
        font-size: 14px;
        border: 1px solid #333;
    }
    .chat-recruiter { color: #4DA8DA; font-weight: bold; }
    .chat-candidate { color: #AEEA00; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- Initialize Vector DB ---
# Connect to the permanent database you just created
@st.cache_resource
def init_chromadb():
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="candidates_db")
    return collection

collection = init_chromadb()

# --- Header Section ---
st.title("⚡ Catalyst AI")
st.markdown("### Autonomous Talent Sourcing & Engagement Pipeline")
st.divider()

if not os.getenv("GROQ_API_KEY"):
    st.error("System Configuration Error. Please check backend environment variables.")
    st.stop()

# --- Agent Functions ---
def parse_jd(jd_text):
    prompt = f"""
    You are an expert technical recruiter. Extract the core requirements from the job description below.
    Return ONLY a valid JSON object with the following keys:
    - "job_title": (string)
    - "required_skills": (list of strings)
    - "years_of_experience": (integer, use 0 if not specified)

    Job Description:
    {jd_text}
    """
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
        response_format={"type": "json_object"},
        temperature=0
    )
    return json.loads(response.choices[0].message.content)

def evaluate_match(candidate, parsed_jd):
    prompt = f"""
    Evaluate this candidate against the job requirements.
    Job Requirements: {json.dumps(parsed_jd)}
    Candidate Profile: {json.dumps(candidate)}
    
    Return ONLY a valid JSON object with the exact keys:
    - "match_score": (integer between 0 and 100)
    - "explanation": (string, exactly 1 or 2 sentences explaining why they are a good fit or what they lack based on the skills)
    """
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
        response_format={"type": "json_object"},
        temperature=0
    )
    return json.loads(response.choices[0].message.content)

def simulate_engagement(candidate, jd_data):
    """Simulates a conversation and scores candidate interest based on their hidden traits."""
    prompt = f"""
    Simulate a brief 2-message outreach conversation.
    Role: {jd_data.get('job_title')}
    Candidate Name: {candidate.get('name')}
    Candidate's Secret Persona: {candidate.get('hidden_interest_level', 'Neutral')}

    Return ONLY a valid JSON object with the exact keys:
    - "recruiter_msg": (string, The AI recruiter's opening pitch)
    - "candidate_reply": (string, The candidate's reply, acting out their Secret Persona)
    - "interest_score": (integer between 0 and 100 based on the candidate's enthusiasm)
    """
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
        response_format={"type": "json_object"},
        temperature=0.3 
    )
    return json.loads(response.choices[0].message.content)

# --- Main UI Pipeline ---
st.markdown("#### 1. Define the Role")
job_description = st.text_area(
    "Paste the raw Job Description below:", 
    height=150, 
    label_visibility="collapsed", 
    placeholder="e.g., We are looking for a Data Analyst with 3 years of experience in Python, SQL..."
)

if st.button("🚀 Run Catalyst Pipeline", type="primary", use_container_width=True):
    if not job_description:
        st.warning("Please provide a job description to begin.")
    else:
        # --- Phase 1: JD Parsing ---
        with st.status("Analyzing Job Description...", expanded=True) as status:
            st.write("Extracting core requirements...")
            parsed_jd_data = parse_jd(job_description)
            status.update(label="Job Description Analyzed Successfully!", state="complete", expanded=False)
            
        st.markdown("### 🎯 Role Brief")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Target Role", parsed_jd_data.get("job_title", "N/A"))
        with col2:
            exp = parsed_jd_data.get('years_of_experience', 0)
            st.metric("Required Experience", f"{exp}+ Years" if exp > 0 else "Entry Level")
        
        st.markdown("**Core Skills Required:**")
        skills_html = "".join([f"<span class='skill-pill'>{skill}</span>" for skill in parsed_jd_data.get("required_skills", [])])
        st.markdown(skills_html, unsafe_allow_html=True)
        st.divider()

        # --- Phase 2 & 3: Discovery & Engagement ---
        st.markdown("### 🤖 Autonomous Outreach & Ranking")
        
        with st.status("Running Discovery & Engagement Simulator...", expanded=True) as status2:
            st.write("1. Searching Vector Database for semantic matches...")
            query_text = f"Looking for a {parsed_jd_data.get('job_title', '')} highly skilled in {', '.join(parsed_jd_data.get('required_skills', []))}"
            
            results = collection.query(query_texts=[query_text], n_results=3)
            retrieved_candidates = results['metadatas'][0]
            
            st.write("2. Evaluating matches and simulating outreach conversations...")
            
            # Process all candidates and store their final metrics
            final_shortlist = []
            for candidate in retrieved_candidates:
                match_data = evaluate_match(candidate, parsed_jd_data)
                engagement_data = simulate_engagement(candidate, parsed_jd_data)
                
                match_score = match_data.get('match_score', 0)
                interest_score = engagement_data.get('interest_score', 0)
                
                # The Golden Formula for Ranking
                combined_score = int((match_score * 0.6) + (interest_score * 0.4))
                
                candidate_package = {
                    "profile": candidate,
                    "match": match_data,
                    "engagement": engagement_data,
                    "final_score": combined_score
                }
                final_shortlist.append(candidate_package)
            
            # Sort the shortlist by the highest final combined score
            final_shortlist.sort(key=lambda x: x['final_score'], reverse=True)
            
            status2.update(label="Pipeline Complete! Candidates Ranked.", state="complete", expanded=False)

        # --- Final UI Display ---
        for rank, item in enumerate(final_shortlist):
            cand = item['profile']
            
            with st.expander(f"#{rank + 1} | 👤 **{cand.get('name', 'Unknown')}** | {cand.get('current_role', 'Candidate')} | 🏆 **Overall Score: {item['final_score']}/100**", expanded=True):
                
                # Top Metrics Row
                colA, colB, colC = st.columns(3)
                colA.metric("Overall Match", f"{item['final_score']}%")
                colB.metric("Skill Match", f"{item['match']['match_score']}%")
                colC.metric("Interest Level", f"{item['engagement']['interest_score']}%")
                
                st.markdown("**Candidate Skills:**")
                cand_skills_html = "".join([f"<span class='skill-pill'>{s}</span>" for s in cand.get('skills', [])])
                st.markdown(cand_skills_html, unsafe_allow_html=True)
                
                st.info(f"**Agent Reasoning:** {item['match'].get('explanation', '')}")
                
                # The Simulated Conversation View
                st.markdown("#### 💬 Simulated Outreach Log")
                st.markdown(f"<span class='chat-recruiter'>AI Recruiter:</span> {item['engagement'].get('recruiter_msg', '')}", unsafe_allow_html=True)
                st.markdown(f"<span class='chat-candidate'>Candidate ({cand.get('name')}):</span> {item['engagement'].get('candidate_reply', '')}", unsafe_allow_html=True)