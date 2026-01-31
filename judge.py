import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("Error: GOOGLE_API_KEY not found in environment.")
    exit(1)

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_PROMPT_PATH = os.path.join(BASE_DIR, "prompts", "system.txt")
INSTRUCTION_PROMPT_PATH = os.path.join(BASE_DIR, "prompts", "instruction.txt")

def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def main():
    # Initial State
    state = {
        "round_number": 1,
        "user_bomb_used": False,
        "bot_bomb_used": False
    }

    system_prompt = load_file(SYSTEM_PROMPT_PATH)
    instruction_template = load_file(INSTRUCTION_PROMPT_PATH)

    print("--- Rock-Paper-Scissors-Plus AI Judge ---")
    print("Rules: Rock, Paper, Scissors, and BOMB (one-time use).")
    print("Type 'exit' to quit.")

    while True:
        user_input = input(f"\n[Round {state['round_number']}] Your move: ").strip()
        if user_input.lower() == "exit":
            break

        # Prepare context injection
        instruction_prompt = (
            instruction_template
            .replace("{{round_number}}", str(state["round_number"]))
            .replace("{{user_bomb_used}}", str(state["user_bomb_used"]).lower())
            .replace("{{bot_bomb_used}}", str(state["bot_bomb_used"]).lower())
            .replace("{{user_input}}", user_input)
        )

        try:
            # Single LLM call per turn
            response = model.generate_content([system_prompt, instruction_prompt])
            
            # Extract JSON from response
            text = response.text.strip()
            # Clean possible markdown formatting
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            
            result = json.loads(text.strip())

            # Display Output
            print("\n--- JUDGE VERDICT ---")
            print(f"User Intent: {result.get('interpreted_user_intent')}")
            print(f"Validity:    {result.get('validity')}")
            print(f"Explanation: {result.get('explanation')}")
            print(f"User Move:   {result.get('user_move')}")
            print(f"Bot Move:    {result.get('bot_move')}")
            print(f"Winner:      {result.get('round_winner')}")
            print(f"Next Action: {result.get('next_action')}")

            # State Authority: Update state STRICTLY based on model output
            # We increment round_number even if not in JSON, but instruction says every submission increments.
            # However, to follow "Prompt Authority", we check if the model returned an incremented round.
            # Requirement says "Code must not decide validity ... override the model".
            
            state["round_number"] = result.get("round_number", state["round_number"]) + 1
            state["user_bomb_used"] = result.get("user_bomb_used", state["user_bomb_used"])
            state["bot_bomb_used"] = result.get("bot_bomb_used", state["bot_bomb_used"])

        except Exception as e:
            print(f"Error communicating with AI Judge or parsing response: {e}")
            # Even on error, we might want to increment to avoid infinite loops, 
            # but usually, we just retry the same round.
            # For simplicity, let's keep it robust.

if __name__ == "__main__":
    main()
