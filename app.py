import streamlit as st

st.set_page_config(
    page_title="Smart Task Prioritizer",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    body {
        background-color: #e8f4fc;
    }
    .stApp {
        background-color: #e8f4fc;
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
        st.markdown(f"""<div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px;'>{result.content}</div>""", unsafe_allow_html=True)

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
