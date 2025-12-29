import streamlit as st
import time
from datetime import datetime
import sys
import os

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Page configuration
st.set_page_config(
    page_title="IPC Legal Chatbot",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4B0082;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.5s;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
    }
    .bot-message {
        background-color: #F3E5F5;
        border-left: 4px solid #9C27B0;
    }
    .section-card {
        background-color: #FFF8E1;
        border: 1px solid #FFD54F;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .legal-disclaimer {
        background-color: #FFEBEE;
        border: 1px solid #EF5350;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .stButton button {
        width: 100%;
        background-color: #4B0082;
        color: white;
    }
    .stTextInput > div > div > input {
        border: 2px solid #4B0082;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    if 'chatbot' not in st.session_state:
        try:
            from utils.chatbot_engine import create_chatbot
            st.session_state.chatbot = create_chatbot()
            st.session_state.init_success = True
        except Exception as e:
            st.session_state.init_success = False
            st.session_state.init_error = str(e)
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    if 'sections_loaded' not in st.session_state:
        st.session_state.sections_loaded = 0
    
    if 'last_query' not in st.session_state:
        st.session_state.last_query = None

# Header
def display_header():
    """Display application header"""
    st.markdown('<h1 class="main-header">⚖️ IPC Legal Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Free AI assistant for Indian Penal Code - 575 Sections</p>', unsafe_allow_html=True)
    
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("IPC Sections", "575")
    with col2:
        st.metric("Chapters", "23")
    with col3:
        st.metric("Questions Asked", len(st.session_state.messages)//2)

# Sidebar
def display_sidebar():
    """Display sidebar with controls and info"""
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2092/2092655.png", width=100)
        
        st.markdown("### 💡 How to Use")
        st.markdown("""
        1. Ask about specific sections (e.g., "IPC 302")
        2. Query punishments (e.g., "theft punishment")
        3. Explore chapters (e.g., "Chapter 16")
        4. Get definitions (e.g., "define murder")
        """)
        
        st.markdown("### 📋 Sample Questions")
        
        # Define sample questions HERE (inside the function)
        sample_questions = [
            "What is IPC section 420?",
            "Punishment for murder",
            "Chapter 17 sections",
            "Define criminal trespass",
            "Cheating under IPC"
        ]
        
        # Simple clickable questions (no session state modification)
        for q in sample_questions:
            if st.button(f"💬 {q}", key=f"sample_{hash(q)}"):
                # Store the selected question in a temporary variable
                st.session_state.selected_question = q
                st.rerun()
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History", type="secondary", key="clear_chat"):
            st.session_state.messages = []
            if 'chatbot' in st.session_state:
                st.session_state.chatbot.clear_history()
            st.session_state.selected_question = None
            st.rerun()
        
        st.markdown("---")
        
        # System info
        st.markdown("### ℹ️ System Info")
        st.markdown(f"""
        **Status:** {"✅ Ready" if st.session_state.get('init_success', False) else "❌ Error"}
        **Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
        **Platform:** Streamlit Cloud
        **Cost:** 100% Free
        """)
        
        # Legal disclaimer (always visible)
        st.markdown("---")
        st.markdown("""
        ### ⚠️ Legal Disclaimer
        This chatbot provides information from the Indian Penal Code for educational purposes only. It does not constitute legal advice. Always consult a qualified lawyer for legal matters.
        """)

# Chat interface
def display_chat_interface():
    """Display main chat interface"""
    
    # Check if a sample question was selected
    if 'selected_question' in st.session_state and st.session_state.selected_question:
        # Auto-fill the input with the selected question
        default_question = st.session_state.selected_question
        # Clear it after use
        del st.session_state.selected_question
    else:
        default_question = ""
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages (only recent ones to avoid overflow)
        recent_messages = st.session_state.messages[-20:] if len(st.session_state.messages) > 20 else st.session_state.messages
        
        for message in recent_messages:
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant", avatar="⚖️"):
                    st.markdown(message["content"])
                    
                    # Show sections used if available
                    if "sections" in message and message["sections"]:
                        with st.expander(f"📄 Sections Referenced ({len(message['sections'])})"):
                            for section in message["sections"]:
                                st.markdown(f"""
                                **Section {section['number']}**: {section['title']}
                                *Chapter {section['chapter']}: {section['chapter_title']}*
                                """)
    
    # Input area
    st.markdown("---")
    
    col1, col2 = st.columns([6, 1])
    with col1:
        user_input = st.text_input(
            "Ask about IPC sections:",
            value=default_question,
            key="user_input",
            placeholder="e.g., 'What is IPC section 302?' or 'Punishment for theft'",
            label_visibility="collapsed"
        )
    with col2:
        send_button = st.button("Send", type="primary", use_container_width=True, key="send_button")
    
    # Process input - PREVENT REPEAT PROCESSING
    current_query = f"{user_input}_{send_button}"
    
    if user_input and (send_button or current_query != st.session_state.get('last_query')):
        # Only process if it's a new query
        if current_query != st.session_state.get('last_query'):
            st.session_state.last_query = current_query
            process_user_input(user_input)

def process_user_input(user_input):
    """Process user input and generate response - FIXED VERSION"""
    
    # Check if this is same as last message to avoid repeats
    if st.session_state.messages and len(st.session_state.messages) >= 2:
        last_user_msg = None
        last_bot_msg = None
        
        # Find last user and bot messages
        for msg in reversed(st.session_state.messages[-4:]):  # Check last 4 messages
            if msg["role"] == "user" and last_user_msg is None:
                last_user_msg = msg["content"]
            elif msg["role"] == "assistant" and last_bot_msg is None:
                last_bot_msg = msg["content"]
        
        # If same question was just asked, don't process again
        if last_user_msg == user_input:
            # Just show existing response again
            return
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Show processing indicator
    with st.spinner("🔍 Searching IPC sections..."):
        try:
            # Get chatbot response
            response = st.session_state.chatbot.process_question(user_input)
            
            # Add bot response to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["text"],
                "sections": response["sections"]
            })
            
            st.session_state.processing = False
            
        except Exception as e:
            error_msg = f"""
            ❌ Sorry, I encountered an error processing your question.
            
            **Error:** {str(e)}
            
            Please try rephrasing your question or try again later.
            """
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "sections": []
            })
            st.session_state.processing = False
    
    # Force rerun to show new messages
    st.rerun()
# Footer
def display_footer():
    """Display application footer"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📚 Data Source**")
        st.markdown("Indian Penal Code (575 Sections)")
    
    with col2:
        st.markdown("**⚡ Technology**")
        st.markdown("Python • Streamlit • Local AI")
    
    with col3:
        st.markdown("**📞 Support**")
        st.markdown("For MCA Project Evaluation")
    
    st.markdown("---")
    st.markdown("""
    <div class="legal-disclaimer">
    <strong>⚠️ IMPORTANT LEGAL NOTICE:</strong><br>
    This application is for informational and educational purposes only. The information provided is based on the Indian Penal Code but may not represent the most current legal provisions. This is not legal advice and should not be relied upon for legal decisions. Always consult with a qualified legal professional for specific legal matters.
    </div>
    """, unsafe_allow_html=True)

# Main application
def main():
    """Main application function"""
    
    # Initialize session state
    initialize_session_state()
    
    # Check initialization
    if not st.session_state.get('init_success', False):
        st.error(f"❌ Failed to initialize chatbot: {st.session_state.get('init_error', 'Unknown error')}")
        st.info("Please check if `data/ipc_data.json` exists and contains valid IPC data.")
        return
    
    # Display layout
    display_header()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        display_chat_interface()
    
    with col2:
        display_sidebar()
    
    display_footer()

# Run the app
if __name__ == "__main__":
    main()