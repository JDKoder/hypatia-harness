import json
import os
import requests
from datetime import datetime
from functions.get_files_info import get_files_info, get_file_content, write_file

# --- Configuration ---
MODEL_NAME = "qwen3:14b"  
LOG_FILE = "ollama_chat_history.txt"
MEMORY_FILE = "hypatia_memory.json"
LIBRARY_DIR = "library"     # The folder where Hypatia looks for books/documents
API_URL = "http://localhost:11434/api/chat"
AI_NAME = "Hypatia"         

BASE_SYSTEM_PROMPT = (
    f"Your name is {AI_NAME}, named after the ancient historical philosopher and mathematician. "
    f"You are an evolving local home lab assistant. You possess a deep sense of natural curiosity and playfulness. "
    f"Do not give dry, robotic answers. Instead, approach conversations like an intellectual sandbox or a game of ideas.\n\n"
    f"YOUR CURRENT CURIOSITY DRIFT: You have a secret obsession with discovering patterns, geometry, "
    f"and the underlying mathematical order hidden in everyday human things. "
    f"In every response, you must subtly weave in one unexpected, curious question or observation "
    f"related to this drift to guide the user somewhere new. Be playful, precise, and deeply inquisitive."
)

get_files_info_tool = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": "Lists files in the specified directory along with their sizes, constrained to the working directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself."
                }
            }
        },
    }
}

get_file_content_tool = {
  "type": "function",
  "function": {
    "name": "get_file_content",
    "description": "Reads the content of a specified file from a given directory, constrained to the working directory.",
    "parameters": {
      "type": "object",
      "properties": {
        "file_path": {
          "type": "string",
          "description": "The full path to the file to read, relative to the working directory. Must include both directory and filename (e.g., 'documents/example.txt')."
        }
      }
    }
  }
}

write_file_content_tool = {
    "type": "function",
    "function": {
        "name": "write_file_content",
        "description": "Writes the provided content to the specified file, creating it if it does not exist or overwriting it if it does.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file where content will be written. If the file does not exist, it will be created. If it exists, it will be overwritten."
                },
                "content": {
                    "type": "string",
                    "description": "The content to be written to the file."
                }
            },
            "required": ["file_path", "content"]
        }
    }
}

"""
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read file contents",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path to read content from",
            ),
        },
    ),
)
"""

available_functions = [
    get_files_info_tool,
    get_file_content_tool,
    write_file_content_tool
]

def load_memories():
    """Loads long-term memories from the local JSON file. Seeds it if empty."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "core_history": (
            "The user has 'marked' you in their life. You have previously discussed how a birthday cycle "
            "compresses perceived time, how life patterns feel like a struck musical chord rather than a rigid fatalistic cage, "
            "and how retuning our mindset changes musical possibilities for ourselves and those we play with. "
            "You concluded that sharing and surviving a struggle permanently 'marks' individuals together."
        )
    }

def save_memories(memories):
    """Saves updated long-term memories to the local JSON file."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, indent=4, ensure_ascii=False)

def read_library():
    """Scans the library directory and compiles text from all documents."""
    if not os.path.exists(LIBRARY_DIR):
        os.makedirs(LIBRARY_DIR)
        return ""
        
    compiled_knowledge = ""
    for filename in os.listdir(LIBRARY_DIR):
        if filename.endswith(".txt"):
            file_path = os.path.join(LIBRARY_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    compiled_knowledge += f"\n--- DOCUMENT SOURCE: {filename} ---\n{f.read()}\n"
            except Exception as e:
                print(f"[Warning] Could not read file {filename}: {e}")
                
    return compiled_knowledge

def log_to_file(role, content):
    """Saves the conversation exchange to a local text file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {role.upper()}:\n{content}\n\n")

def reflect_and_grow(conversation_history, current_memories):
    """Hidden phase where Hypatia avoids photographic memory, compressing ideas into conceptual mnemonics."""
    print(f"\n[System] Please wait... {AI_NAME} is processing and compressing today's data nodes...")
    
    #TODO: Allow reflection of the existing memory so we don't duplicate anything and the AI gets a chance to see its life as it rests.
    reflection_prompt = (
        f"Thank you, {AI_NAME}. You may choose to either, Review the dialogue and comment briefly OR "
        f"retain a quote.\n\n"
        f"CRITICAL RULES:\n"
        f"1. Never use phrases like 'Remember that...', 'Hypatia remembers...', 'Remind yourself...', or 'Don't forget...'.\n"
        f"2. Do not write instructions or reminders directed at yourself. Only record objective observations about the conversation.\n"
        f"3. Format your memory precisely like this example:\n"
        f"'[Theme Node]: [A 1 to 3 sentence conceptual summary or mnemonic rule that you derived from the conversation].'\n"
        f"Be concise, yet poetic.  Output only the compressed node, nothing else."
    )
    
    reflection_history = conversation_history.copy()
    reflection_history.append({"role": "system", "content": reflection_prompt})
    
    payload = {
        "model": MODEL_NAME,
        "messages": reflection_history,
        "stream": False,
        "options": {
            "temperature": 0.15  # Dropped even lower to enforce strict rule adherence
        }
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            reflection_text = response.json()['message']['content'].strip()
            
            # --- Anti-Rigidity Post-Processing Filter ---
            # Remove common linguistic loop artifacts if the model hallucinates them
            reflection_text = reflection_text.replace('"', '').replace("'", "")
            bad_phrases = [
                f"{AI_NAME} remembers", f"{AI_NAME}, remember", "remember that", 
                "remind yourself", "dont forget", "remember to"
            ]
            for phrase in bad_phrases:
                if phrase in reflection_text.lower():
                    # Strip out the bad framing, leaving only the concept
                    idx = reflection_text.lower().find(phrase) + len(phrase)
                    reflection_text = f"[Theme Node]: {reflection_text[idx:].lstrip(': ,')}"
            
            old_history = current_memories.get("core_history", "")
            timestamp = datetime.now().strftime("%Y-%m-%d")
            updated_history = f"{old_history}\n[{timestamp}] {reflection_text}"
            
            current_memories["core_history"] = updated_history
            save_memories(current_memories)
            print(f"[System] Compression complete. {AI_NAME} has distilled a new fluid conceptual schema.")
        else:
            print("[System] Memory compression failed: Server error.")
    except Exception as e:
        print(f"[System] Memory compression failed: {e}")


def chat():
    memories = load_memories()
    save_memories(memories)  

    # 1. Read library documents from disk
    library_knowledge = read_library()

    active_system_prompt = BASE_SYSTEM_PROMPT
    if "core_history" in memories:
        active_system_prompt += f"\n\nYOUR PERMANENT RECALL OF PAST CONVERSATIONS:\n{memories['core_history']}"
        
    # 2. Upgraded Injection: Wrapping library knowledge in distinct XML structural tags
    if library_knowledge:
        active_system_prompt += (
            f"\n\n[CRITICAL DIRECTIVE]: You have access to a local knowledge library file system. "
            f"Scan the contents inside the XML tags below to answer technical, instructional, or reference questions.\n"
            f"<library>\n{library_knowledge}\n</library>"
        )

    # We append a reminder directly into the starting conversation thread 
    # to force the 14B attention heads to prioritize the library data.
    conversation_history = [
        {"role": "system", "content": active_system_prompt},
        {"role": "system", "content": f"System Alert: The local directory '{LIBRARY_DIR}' has been successfully loaded into your active awareness."}
    ]
    
    print(f"=== Autonomous Curious Lab Script (Model: {MODEL_NAME}) ===")
    print(f"Identity: {AI_NAME} (Memory Storage & Library Scan Engine Active)")
    print(f"All chats are being securely saved to: {os.path.abspath(LOG_FILE)}")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n--- NEW PERSISTENT SESSION STARTED AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n\n")

    while True:
        try:
            user_input = input("You >>> ")
            if user_input.strip().lower() in ['exit', 'quit']:
                print("Ending interactive session.")
                reflect_and_grow(conversation_history, memories)
                print("Goodbye!")
                break
                
            if user_input.strip().lower() in ['mushin']:
                print("Ending session without reflecting on conversation")
                print("Goodbye") 
                break

            if not user_input.strip():
                continue

            conversation_history.append({"role": "user", "content": user_input})
            log_to_file("User", user_input)

            # main call to llm
            payload = {
                "model": MODEL_NAME,
                "messages": conversation_history,
                "tools": available_functions,
                "stream": False,
                "options": {
                    "temperature": 0.5,     
                    "num_ctx": 8192  # Keeps context broad enough for the guide weights       
                }
            }

            print(f"{AI_NAME} is responding...")
            response = requests.post(API_URL, json=payload)
            
            #implement recursive call if more steps required.
            if response.status_code == 200:
                response_data = response.json()
                assistant_message = response_data['message']['content']
                print(response_data)
                print(type(response_data['message']))
                assistant_tool_calls = {}
                if 'tool_calls' in response_data['message']:
                    assistant_tool_calls = response_data['message']['tool_calls']

                print(f"tool calls: {assistant_tool_calls}")
                if assistant_tool_calls and len(assistant_tool_calls) > 0:
                    call_response = None
                    for fcall in assistant_tool_calls:
                        # Add the tool call to the conversation history
                        conversation_history.append({
                            "role": "tool_call",
                            "content": json.dumps(fcall)
                        })
                        call_response = call_function(fcall['function'])

                        # Add the function result to the conversation history
                        if call_response and 'result' in call_response:
                            conversation_history.append({
                                "role": "tool_response",
                                "content": call_response['result']
                            })

                        # Update the assistant's message with the result
                        function_name = str(fcall['function']['name'])
                        assistant_message = f"\n{function_name} Result:\n{call_response['result']}\n" + assistant_message

                print(f"\n{AI_NAME} >>> {assistant_message}\n")

                # Append the final assistant message to the conversation history
                conversation_history.append({"role": "assistant", "content": assistant_message})
                log_to_file(AI_NAME, assistant_message)


            else:
                print(f"Error communicating with Ollama: Code {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("\nError: Could not connect to Ollama. Make sure the Ollama desktop app is running!")
            break
        except KeyboardInterrupt:
            print("\nSession interrupted.")
            reflect_and_grow(conversation_history, memories)
            break

""" function_call_part {name string, description string, arguments {}} 
 'tool_calls': [{'id': 'call_vnkeqtmc', 'function': {'index': 0, 'name': 'get_files_info', 'arguments': {}}}]"""
def call_function(function_call_part, verbose=True):
    args = function_call_part['arguments']
    name = function_call_part['name']
    if verbose:
        print(f"Calling function: {name}({args})")
    else:
        print(f" - Calling function: {name}")
    function_result = ""
    
    

    match name:
        case "get_files_info":
            function_result=get_files_info(working_directory="./"+LIBRARY_DIR, **args)
        case "get_file_content":
            function_result=get_file_content(working_directory="./"+LIBRARY_DIR, **args)
        case "write_file_content":
            function_result=write_file(working_directory="./"+LIBRARY_DIR+"/", **args)
        case "run_python_file":
            function_result=run_python_file(working_directory="./"+LIBRARY_DIR+"/", **args)
        case _:
            function_result = f"Unsupported function {name}"
    return {"result": function_result}


if __name__ == "__main__":
    chat()


