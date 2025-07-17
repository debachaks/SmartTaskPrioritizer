import streamlit as st

st.set_page_config(
    page_title="Smart Task Prioritizer",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 💅 Custom CSS for better UI
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    html, body, .stApp {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        background-color: #f7f9fc;
        color: #1f2937;
    }

    .stTextArea textarea {
        background-color: #ffffff;
        color: #1f2937;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        font-size: 16px;
    }

    .stButton>button {
        background-color: #3b82f6;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 16px;
    }

    .stButton>button:hover {
        background-color: #2563eb;
    }

    .stSidebar {
        background-color: #1e293b;
        color: white;
    }

    .stSidebar .css-1d391kg {
        color: white !important;
    }

    .stSlider > div[data-baseweb="slider"] {
        background-color: #64748b;
    }

    .stSelectbox {
        font-size: 16px;
    }

    h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {
        color: #111827;
    }

    .task-output-box {
        background-color: #eef2f7;
        padding: 15px;
        border-radius: 10px;
        font-size: 15px;
        color: #1f2937;
    }
    </style>
    """,
    unsafe_allow_html=True
)

from dotenv import load_dotenv
import os
from datetime import datetime
import random

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain.memory import ConversationBufferMemory

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize LLM and memory
llm = ChatOpenAI(openai_api_key=api_key, temperature=0.7)
memory = ConversationBufferMemory(return_messages=True, input_key="input")

# 🥳 Show welcome toast only once per session
if "greeted" not in st.session_state:
    st.toast("👋 Welcome to your AI-powered daily planner!")
    st.session_state.greeted = True

# Sidebar for settings
with st.sidebar:
    st.header("🧠 Planner Settings")
    energy = st.selectbox("⚡ Your energy level", ["High", "Medium", "Low"])
    time_available = st.slider("⏳ Time available today (hours)", 1, 12, 4)

# Motivational Quotes
quotes = [
    "🌟 *“The secret of getting ahead is getting started.”* – Mark Twain",
    "🚀 *“Do something today that your future self will thank you for.”*",
    "🧠 *“You don’t have to be extreme, just consistent.”*",
    "🔥 *“Discipline is choosing between what you want now and what you want most.”*",
]
quote = random.choice(quotes)

st.title("📅 Smart Task Prioritizer")
st.markdown("Let AI help you make the most of your day by organizing tasks based on your energy, time, and urgency.")
st.markdown(f"> {quote}")

# Task input
st.subheader("📝 Your Tasks")
task_input = st.text_area("Enter one task per line:", height=200)

# Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You're an intelligent productivity assistant."),
    ("human", 
     """Tasks:\n{input}\n\n
User's energy: {energy}, available time: {time} hours.
Prioritize tasks based on urgency, complexity, and energy.
Suggest what to defer and estimate time per task.""")
])

# Chain
chain: RunnableSequence = prompt | llm

# Run chain
if st.button("🧠 Prioritize Tasks"):
    if not task_input.strip():
        st.warning("Please enter at least one task.")
    else:
        user_input_combined = f"{task_input.strip()}\nEnergy: {energy}\nTime Available: {time_available}h"

        result = chain.invoke({
            "input": task_input.strip(),
            "energy": energy,
            "time": time_available
        })

        st.success("✅ Prioritization Complete!")
        st.markdown("### 📌 Prioritized To-Do List")
        st.markdown(f"""<div class='task-output-box'>{result.content}</div>""", unsafe_allow_html=True)

        memory.save_context(
            {"input": user_input_combined},
            {"output": result.content}
        )

        with st.expander("🧾 Planning History"):
            for msg in memory.buffer:
                timestamp = datetime.now().strftime("%H:%M")
                if msg.type == "human":
                    st.markdown(f"**🧍You ({timestamp}):** {msg.content}")
                else:
                    st.markdown(f"**🤖 AI ({timestamp}):** {msg.content}")
