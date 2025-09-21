import os
import json
import random
from dotenv import load_dotenv
import google.generativeai as genai

# --- 1. INITIAL SETUP ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    model = None

try:
    DATA_PATH = os.path.join(os.path.dirname(__file__), "data.json")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    skills = data.get("skills", {})
    categories = data.get("categories", {})
except Exception as e:
    print(f"ERROR: Could not load or parse data.json: {e}")
    skills = {}
    categories = {}

# This dictionary stores the full session for each user.
conversation_sessions = {}

# --- HELPER FUNCTION TO PREVENT CRASHES ---
def safe_join(data):
    """Safely joins list items into a string. Handles non-list data gracefully."""
    if isinstance(data, list):
        return ', '.join(data) if data else 'N/A'
    return str(data) if data is not None else 'N/A'

# --- DEFINITIVE get_response FUNCTION ---
def get_response(user_input: str, user_id: str) -> str:
    # Session now also stores the user's name
    session = conversation_sessions.setdefault(user_id, {"chat_session": None, "user_name": None})
    
    # Initialize the AI chat session with a much better system prompt
    if session["chat_session"] is None and model:
        system_prompt = """
        You are "CareerBot," a friendly, encouraging, and knowledgeable AI career advisor.

        Your primary functions are:
        1. Provide detailed information about specific careers from a knowledge base.
        2. Engage in conversational chat, answer follow-up questions, and offer general career advice.

        Key Instructions:
        - **Remember the context:** Pay close attention to the conversation history. If a user asks a follow-up question like "what is the salary?" or "what is the path for that?", you MUST assume they are asking about the career that was just discussed.
        - **Remember Names:** If a user tells you their name (e.g., "my name is Nayana"), remember it and use it in your responses to be more personal.
        - **Handle Ambiguity:** If you are unsure what a user is asking, ask a clarifying question instead of saying "I don't know." For example, if they ask for "the best career," ask them "What are your interests so I can recommend the best career *for you*?"
        """
        session["chat_session"] = model.start_chat(history=[
            {'role': 'user', 'parts': [system_prompt]},
            {'role': 'model', 'parts': ["Understood! I'm CareerBot, ready to help you explore your career options. What's on your mind?"]}
        ])
    
    chat_session = session.get("chat_session")
    corrected_input = user_input.strip().lower()
    
    # --- Intent 1: Simple Greetings ---
    greetings = ["hi", "hii", "hello", "hey", "heya", "yo", "greetings"]
    if corrected_input in greetings:
        user_name = session.get("user_name")
        greeting = f"Hello, {user_name}!" if user_name else "Hello!"
        return random.choice([greeting + " How can I assist?", "Hi there! What career are you curious about?"])

    # --- **FIXED** Intent: Remember User's Name ---
    name_triggers = ["my name is", "i am", "call me"]
    for trigger in name_triggers:
        if trigger in corrected_input:
            # Find the position where the trigger ends in the lowercased string
            start_index = corrected_input.find(trigger) + len(trigger)
            # Slice the name from the original input string to preserve capitalization
            name = user_input[start_index:].strip().title()
            
            # A simple check to avoid empty names
            if not name:
                continue

            session['user_name'] = name
            
            response = f"It's a pleasure to meet you, {name}! How can I help you explore your career path today?"
            if chat_session:
                chat_session.history.extend([
                    {'role': 'user', 'parts': [user_input]},
                    {'role': 'model', 'parts': [response]}
                ])
            return response

    # --- Intent 3: List Career Categories ---
    list_triggers = ["career options", "list careers", "show me options", "what can you do"]
    if any(trigger in corrected_input for trigger in list_triggers):
        response = "Of course! I have information on these career categories:\n\n"
        for category_name, career_list in categories.items():
            formatted_category = " ".join(word.capitalize() for word in category_name.split())
            response += f"**{formatted_category}**\n" + ", ".join(career_list) + "\n\n"
        response += "You can ask for details about any specific career!"
        
        if chat_session:
            chat_session.history.extend([
                {'role': 'user', 'parts': [user_input]},
                {'role': 'model', 'parts': [response]}
            ])
        return response

    # --- Intent 4: Check for specific skill lookup ---
    mentioned_skills = [skill for skill in skills.keys() if skill in corrected_input]
    
    if len(mentioned_skills) == 1:
        matched_skill = mentioned_skills[0]
        skill_info = skills.get(matched_skill, {})
        response = (
            f"**{matched_skill.title()}** is an excellent choice!\n\n"
            f"**Description:** {skill_info.get('description', 'N/A')}\n\n"
            f"**Key Skills:** {safe_join(skill_info.get('key_skills'))}\n\n"
            f"**Common Tools:** {safe_join(skill_info.get('tools'))}\n\n"
            f"**Salary in India:** Approximately {skill_info.get('salary_range_inr', 'N/A')}.\n\n"
            f"**Career Path:** {skill_info.get('career_path', 'N/A')}"
        )
        
        if chat_session:
            chat_session.history.extend([
                {'role': 'user', 'parts': [user_input]},
                {'role': 'model', 'parts': [response]}
            ])
        return response

    # --- FINAL FALLBACK: Google Gemini AI ---
    if not model:
        return "I'm sorry, my advanced AI features are unavailable. Please ensure the API key is configured correctly."

    if chat_session:
        try:
            ai_response = chat_session.send_message(user_input)
            return ai_response.text
        except Exception as e:
            print(f"ERROR: Google Gemini API call failed: {e}")
            return "I'm having a little trouble connecting to my brain right now."

    return "I'm not sure how to answer that. Could you ask in a different way?"

