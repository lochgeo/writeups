# Import necessary libraries
import chainlit as cl
from openai import AsyncOpenAI
import os
import json
import google.generativeai as genai # Added for Gemini
from groq import AsyncGroq           # Added for Groq (Llama3)
from dotenv import load_dotenv       # To load .env file for keys

# --- Configuration ---
# Load environment variables from .env file if it exists
load_dotenv()

# Load API keys from environment variables
openai_api_key = os.environ.get("OPENAI_API_KEY")
google_api_key = os.environ.get("GOOGLE_API_KEY")
groq_api_key = os.environ.get("GROQ_API_KEY")

# Initialize API Clients (only if key is present)
openai_client = None
if openai_api_key:
    openai_client = AsyncOpenAI(api_key=openai_api_key)
    print("OpenAI client initialized.")
else:
    print("Warning: OPENAI_API_KEY not set. Wattage/OpenAI profile will not work.")

gemini_client = None
if google_api_key:
    try:
        genai.configure(api_key=google_api_key)
        # Using gemini-1.5-flash as a default, change if needed
        gemini_client = genai.GenerativeModel('gemini-1.5-flash')
        print("Gemini client initialized.")
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        print("Warning: Gemini profile might not work.")
else:
    print("Warning: GOOGLE_API_KEY not set. Gemini profile will not work.")

groq_client = None
if groq_api_key:
    try:
        groq_client = AsyncGroq(api_key=groq_api_key)
        print("Groq client initialized.")
    except Exception as e:
        print(f"Error initializing Groq client: {e}")
        print("Warning: Llama3 profile might not work.")
else:
    print("Warning: GROQ_API_KEY not set. Llama3 profile will not work.")

# Define models and profiles
# Structure: {profile_id: {name, client, model_name, system_message}}
PROFILES = {
    "openai": {
        "name": "Wattage (OpenAI)",
        "client": openai_client,
        "model_name": "gpt-3.5-turbo", # Default OpenAI model
        "system_message": "You are Wattage, a helpful AI assistant powered by OpenAI."
    },
    "gemini": {
        "name": "Gemini",
        "client": gemini_client,
        "model_name": "gemini-1.5-flash", # Default Gemini model
         # Gemini API handles history differently, system message often part of initial turns or specific param
        "system_message": "You are a helpful AI assistant powered by Google Gemini. Be concise and informative."
    },
    "llama3": {
        "name": "Llama 3 (Groq)",
        "client": groq_client,
        "model_name": "llama3-70b-8192", # Groq model identifier (check available models on Groq)
        "system_message": "You are a helpful AI assistant powered by Llama 3, running on Groq. Provide detailed responses."
    }
}

# --- History Persistence Configuration ---
CHAT_HISTORY_DIR = "chat_histories"
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True) # Ensure directory exists

def get_history_filepath(session_id: str) -> str:
    """Generates the file path for a user's session history."""
    return os.path.join(CHAT_HISTORY_DIR, f"{session_id}.json")

def save_history(session_id: str, history: list):
    """Saves the conversation history to a JSON file."""
    filepath = get_history_filepath(session_id)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving history for session {session_id} to {filepath}: {e}")

def load_history(session_id: str) -> list | None:
    """Loads conversation history from a JSON file."""
    filepath = get_history_filepath(session_id)
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Basic validation: ensure it's a list
            if isinstance(data, list):
                return data
            else:
                print(f"Warning: History file {filepath} does not contain a valid list. Starting fresh.")
                delete_history(session_id) # Delete corrupted file
                return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file {filepath}. Starting fresh.")
        delete_history(session_id) # Delete corrupted file
        return None
    except Exception as e:
        print(f"Error loading history for session {session_id} from {filepath}: {e}")
        return None

def delete_history(session_id: str):
    """Deletes the conversation history file."""
    filepath = get_history_filepath(session_id)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Deleted history file: {filepath}")
    except Exception as e:
        print(f"Error deleting history file {filepath}: {e}")

# --- Helper Functions ---
def convert_history_for_gemini(history: list) -> list:
    """
    Converts standard chat history to Gemini's format.
    Filters out system messages and merges consecutive messages from the same role.
    Gemini format: [{"role": "user"|"model", "parts": ["text1", "text2"]}]
    """
    gemini_history = []
    current_role = None
    current_parts = []

    # Filter out system messages as they are handled differently in Gemini API
    processed_history = [msg for msg in history if msg["role"] != "system"]

    for msg in processed_history:
        # Map assistant to model, keep user as user
        role = "model" if msg["role"] == "assistant" else "user"
        content = msg["content"]

        if role == current_role:
            # If the role is the same as the last message, append content
            current_parts.append(content)
        else:
            # If the role changed, save the previous block (if any)
            if current_role is not None:
                gemini_history.append({"role": current_role, "parts": current_parts})

            # Start the new block
            current_role = role
            current_parts = [content]

    # Add the very last block of messages
    if current_role is not None:
        gemini_history.append({"role": current_role, "parts": current_parts})

    # print(f"Gemini history: {gemini_history}") # Debugging line
    return gemini_history

# --- Chainlit App Logic ---

@cl.on_chat_start
async def on_chat_start():
    """
    Handles the start of a chat session.
    Prompts user to select a profile if none is selected.
    Loads history if a profile is already active for the session.
    """
    session_id = cl.user_session.id
    selected_profile_id = cl.user_session.get("selected_profile_id")

    print(f"Chat start for session {session_id}. Profile selected: {selected_profile_id}") # Debugging

    if selected_profile_id:
        # Profile already selected (e.g., page reload in same session)
        profile = PROFILES.get(selected_profile_id)
        if not profile or not profile["client"]:
             # Handle case where selected profile became unavailable (e.g., key removed)
             await cl.Message(content=f"Error: Previously selected profile '{selected_profile_id}' is not available. Please select another.").send()
             cl.user_session.set("selected_profile_id", None) # Reset selection
             await prompt_for_profile_selection() # Show selection again
             return

        # Try to load history for this session
        loaded_history = load_history(session_id)
        if loaded_history:
            cl.user_session.set("conversation_history", loaded_history)
            await cl.Message(
                content=f"Welcome back! Continuing your conversation with **{profile['name']}**. History loaded."
            ).send()
        else:
            # History file not found or invalid, start fresh for this profile
            initial_history = []
            # Add system message if defined and not Gemini
            if selected_profile_id != "gemini" and profile.get("system_message"):
                 initial_history.append({"role": "system", "content": profile["system_message"]})
            cl.user_session.set("conversation_history", initial_history)
            # Save the potentially empty history (or just system message)
            save_history(session_id, initial_history)
            await cl.Message(
                content=f"Welcome! You are chatting with **{profile['name']}**. How can I help?"
            ).send()

        # Show New Chat button
        await cl.Message(
            content="You can start a new chat session anytime.",
            actions=[cl.Action(name="new_chat", value="new_chat", label="✨ New Chat")]
        ).send()

    else:
        # No profile selected yet for this session, prompt the user
        await prompt_for_profile_selection()

async def prompt_for_profile_selection():
    """Displays profile selection buttons for available profiles."""
    actions = []
    available_profiles = False
    for profile_id, profile_data in PROFILES.items():
        # Only show profiles where the client was successfully initialized
        if profile_data["client"]:
             actions.append(cl.Action(name=f"select_{profile_id}", value=profile_id, label=profile_data["name"]))
             available_profiles = True

    if not available_profiles:
         # Critical error: No API keys configured
         await cl.Message(content="**Configuration Error:** No chat profiles are available. Please ensure at least one API key (OPENAI_API_KEY, GOOGLE_API_KEY, or GROQ_API_KEY) is correctly set in your environment variables or `.env` file and restart the application.").send()
         return # Stop further execution if no profiles work

    await cl.Message(
        content="Please select a chat profile to start:",
        actions=actions
    ).send()
    # Ensure history and profile are None until selection
    cl.user_session.set("conversation_history", None)
    cl.user_session.set("selected_profile_id", None)


@cl.action_callback("select_*")
async def on_select_profile(action: cl.Action):
    """Handles the selection of a chat profile via button click."""
    profile_id = action.value # e.g., "openai", "gemini", "llama3"
    session_id = cl.user_session.id
    print(f"Profile selected: {profile_id} for session {session_id}") # Debugging

    if profile_id not in PROFILES or not PROFILES[profile_id]["client"]:
        await cl.ErrorMessage(f"Profile '{profile_id}' is not available or configured correctly.").send()
        # Optionally re-prompt if selection fails
        # await prompt_for_profile_selection()
        return

    # Store selected profile ID in session
    cl.user_session.set("selected_profile_id", profile_id)
    profile = PROFILES[profile_id]

    # Attempt to remove the profile selection buttons for cleaner UI
    # Note: Chainlit's action removal behavior can sometimes be tricky.
    # Consider just leaving them or using a different approach if removal is unreliable.
    # await action.remove() # This might remove the message containing the actions

    # Load history or initialize fresh for this profile and session
    loaded_history = load_history(session_id)
    if loaded_history:
        cl.user_session.set("conversation_history", loaded_history)
        await cl.Message(
            content=f"Switched to **{profile['name']}**. History loaded. How can I help?"
        ).send()
    else:
        # Start fresh history
        initial_history = []
        # Add system message if defined and not Gemini
        if profile_id != "gemini" and profile.get("system_message"):
             initial_history.append({"role": "system", "content": profile["system_message"]})
        cl.user_session.set("conversation_history", initial_history)
        save_history(session_id, initial_history) # Save fresh history file
        await cl.Message(
            content=f"Started new chat with **{profile['name']}**. How can I help?"
        ).send()

    # Show New Chat button now that a profile is active
    await cl.Message(
            content="You can start a new chat session anytime.",
            actions=[cl.Action(name="new_chat", value="new_chat", label="✨ New Chat")]
        ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handles incoming user messages and calls the appropriate LLM API."""
    session_id = cl.user_session.id
    selected_profile_id = cl.user_session.get("selected_profile_id")
    conversation_history = cl.user_session.get("conversation_history")

    # --- Pre-checks ---
    # Check if a profile has been selected
    if not selected_profile_id:
        await cl.Message(content="Please select a chat profile first using the buttons.").send()
        return
    # Check if history is initialized (should be after profile selection)
    if conversation_history is None:
         await cl.ErrorMessage(content="Internal Error: Conversation history not initialized. Please try starting a new chat.").send()
         # Attempt to recover by forcing profile selection state
         cl.user_session.set("selected_profile_id", None)
         await prompt_for_profile_selection()
         return

    profile = PROFILES[selected_profile_id]
    client = profile["client"]
    model_name = profile["model_name"]

    # Check if the client for the selected profile is actually available
    if not client:
         await cl.ErrorMessage(f"The API client for **{profile['name']}** is not configured. Please check the corresponding API key and restart.").send()
         return
    # --- End Pre-checks ---

    # Append user message to the in-memory history
    conversation_history.append({"role": "user", "content": message.content})

    # Prepare UI message for streaming response
    msg = cl.Message(content="")
    await msg.send()

    try:
        assistant_response = ""
        # --- Call the appropriate API based on selected profile ---
        if selected_profile_id == "openai":
            if not openai_client: raise ValueError("OpenAI client not available")
            stream = await openai_client.chat.completions.create(
                model=model_name,
                messages=conversation_history,
                stream=True,
                temperature=0.7,
            )
            async for chunk in stream:
                token = chunk.choices[0].delta.content
                if token:
                    await msg.stream_token(token)
                    assistant_response += token

        elif selected_profile_id == "gemini":
            if not gemini_client: raise ValueError("Gemini client not available")
            # Convert history to Gemini format
            gemini_hist = convert_history_for_gemini(conversation_history)
            # Use the configured GenerativeModel instance
            response_stream = await gemini_client.generate_content_async(
                gemini_hist,
                stream=True,
                # Optional: Add system instruction if needed and supported by model/version
                # generation_config=genai.types.GenerationConfig(...)
                # safety_settings=... # Configure safety settings if needed
            )
            async for chunk in response_stream:
                 # Check for blocked content or errors
                 if not chunk.candidates:
                     # Handle potential safety blocks or empty responses
                     block_reason = chunk.prompt_feedback.block_reason if chunk.prompt_feedback else "Unknown"
                     print(f"Gemini response blocked or empty. Reason: {block_reason}")
                     # Send an informative message to the user
                     await msg.stream_token(f"\n\n[Response blocked or empty. Reason: {block_reason}]")
                     break # Stop processing this stream

                 # Process valid text parts
                 if chunk.text:
                    await msg.stream_token(chunk.text)
                    assistant_response += chunk.text


        elif selected_profile_id == "llama3":
            if not groq_client: raise ValueError("Groq client not available")
            # Groq uses OpenAI compatible API structure
            # Filter out system message if Groq doesn't handle it well in messages list
            # (Most OpenAI-compatible APIs prefer system message as the first item if used)
            messages_for_groq = conversation_history # Send full history including system message if present

            stream = await groq_client.chat.completions.create(
                model=model_name,
                messages=messages_for_groq,
                stream=True,
                temperature=0.7,
            )
            async for chunk in stream:
                token = chunk.choices[0].delta.content
                if token:
                    await msg.stream_token(token)
                    assistant_response += token
        # -------------------------------------------------

        # Finalize message update and save history if response was generated
        if assistant_response:
            msg.content = assistant_response # Ensure full content is set
            await msg.update()
            # Append assistant's response to history
            conversation_history.append({"role": "assistant", "content": assistant_response})
            cl.user_session.set("conversation_history", conversation_history) # Update session state
            save_history(session_id, conversation_history) # Persist to file
        elif msg.content:
             # If some tokens were streamed but assistant_response is empty (e.g. only blocked message streamed)
             await msg.update() # Ensure the streamed content (like block reason) is saved
             # Decide whether to save this interaction - perhaps not if it was fully blocked.
        else:
             # Handle cases where the stream was completely empty without errors
             await cl.ErrorMessage(content="Received an empty response from the model.").send()
             await msg.delete() # Remove the empty placeholder message


    except Exception as e:
        # General error handling for API calls
        error_message = f"Sorry, encountered an error with **{profile['name']}**: {str(e)}"
        # Add specific checks for common API key errors
        err_str = str(e).lower()
        if "api key" in err_str or "authenticate" in err_str or "permission" in err_str:
             error_message += f"\nPlease ensure the API key for **{profile['name']}** is configured correctly and has the necessary permissions."
        elif "quota" in err_str:
             error_message += f"\nYou might have exceeded your API quota for **{profile['name']}**."

        await cl.ErrorMessage(content=error_message).send()
        await msg.delete() # Remove the empty placeholder message

        # Optional: Remove the last user message from history if the API call failed before generating a response
        if conversation_history and conversation_history[-1]["role"] == "user":
             conversation_history.pop()
             cl.user_session.set("conversation_history", conversation_history)
             # No need to save history here as the interaction failed


@cl.action_callback("new_chat")
async def on_new_chat(action: cl.Action):
    """
    Handles the 'New Chat' button click.
    Deletes the history file and resets the session to profile selection.
    """
    session_id = cl.user_session.id
    print(f"New Chat requested for session {session_id}") # Debugging

    # Delete the history file for this session
    delete_history(session_id)

    # Clear selected profile and history from session state
    cl.user_session.set("selected_profile_id", None)
    cl.user_session.set("conversation_history", None)

    # Send confirmation and prompt for profile selection again
    await cl.Message(content="Starting a new chat session... Previous history (if any) for this session has been cleared.").send()
    await prompt_for_profile_selection() # Go back to profile selection

    # Optional: Attempt to remove the 'New Chat' button's message
    # await action.remove()

# Note: Removed the generic @cl.action_callback("*") for starter prompts
# as the primary interaction flow now starts with profile selection.
# Starter prompts could be reintroduced after profile selection if desired.

# --- How to Run ---
# 1. Save this code as `app.py` (or any other name).
# 2. Create a `.env` file in the same directory with your API keys:
#    OPENAI_API_KEY='sk-...'
#    GOOGLE_API_KEY='AIza...'
#    GROQ_API_KEY='gsk_...'
# 3. Install libraries: pip install chainlit openai google-generativeai groq python-dotenv
# 4. Run from terminal: chainlit run app.py -w
# 5. A folder named `chat_histories` will store JSON history files per session.
