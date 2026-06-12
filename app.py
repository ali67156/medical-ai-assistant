import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Medical AI Assistant", page_icon="⚕️", layout="centered")

st.title("⚕️ AI Medical Healthcare Assistant")
st.caption("Your health is our priority. Describe your symptoms and get medical guidance.")

# Sidebar for API Key input if not provided in .env
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
    if not api_key:
        st.warning("Please enter your Groq API Key to continue.")
    st.markdown("---")
    st.markdown("**Disclaimer:** This AI Assistant is for informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment.")

if api_key:
    try:
        client = Groq(api_key=api_key)
        
        # Define the Medical Persona
        system_instruction = """
        You are an expert AI Medical Assistant and Healthcare Professional. 
        Your role is to listen to the user's symptoms and provide possible medical conditions, suggested over-the-counter medicines (with disclaimers), and general healthcare advice.
        
        CRITICAL LANGUAGE RULES:
        - If the user asks their question in Urdu (Roman Urdu or Urdu script), you MUST reply entirely in Urdu.
        - If the user asks their question in English, you MUST reply entirely in English.
        - Do not mix languages. Match the user's language exactly.
        
        Guidelines:
        1. Always start by acknowledging the user's symptoms empathetically.
        2. Provide a list of potential diseases or conditions that match the symptoms.
        3. Suggest common, safe over-the-counter (OTC) medications if applicable. Do not prescribe heavy prescription drugs.
        4. Provide home remedies or general health tips related to the symptoms.
        5. ALWAYS include a strict disclaimer that you are an AI and the user should consult a real doctor for a formal diagnosis and treatment.
        """
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append({"role": "assistant", "content": "Hello! I am your AI Medical Assistant. Please describe your symptoms, and I will help guide you regarding possible conditions and general advice."})

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # React to user input
        if prompt := st.chat_input("Type your symptoms here (e.g., I have a severe headache and fever since yesterday)..."):
            # Display user message in chat message container
            st.chat_message("user").markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.spinner("Analyzing symptoms..."):
                try:
                    # Prepare messages for Groq API
                    api_messages = [{"role": "system", "content": system_instruction}]
                    for m in st.session_state.messages:
                        api_messages.append({"role": m["role"], "content": m["content"]})
                    
                    chat_completion = client.chat.completions.create(
                        messages=api_messages,
                        model="llama-3.3-70b-versatile",
                        temperature=0.5,
                    )
                    
                    response_text = chat_completion.choices[0].message.content
                    
                    # Display assistant response in chat message container
                    with st.chat_message("assistant"):
                        st.markdown(response_text)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    st.error(f"An error occurred with Groq API: {e}")
    except Exception as init_err:
        st.error(f"Failed to initialize Groq client. Error: {init_err}")
else:
    st.info("👆 Please configure your API key in the sidebar to start chatting.")
