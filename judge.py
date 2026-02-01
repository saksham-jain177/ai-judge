import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    exit("Error: GOOGLE_API_KEY missing.")

client = genai.Client(api_key=API_KEY)
model_id = "gemini-3-flash-preview"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_STR = open(os.path.join(BASE_DIR, "prompts", "system.txt"), "r", encoding="utf-8").read()
INSTR_TMPL = open(os.path.join(BASE_DIR, "prompts", "instruction.txt"), "r", encoding="utf-8").read()

def main():
    state = {"round": 1, "user_bomb": False, "bot_bomb": False}

    while True:
        u_in = input(f"[Round {state['round']}] Move: ").strip()
        if u_in.lower() == "exit": break

        prompt = (INSTR_TMPL
                  .replace("{{round}}", str(state["round"]))
                  .replace("{{user_bomb_used}}", str(state["user_bomb"]).lower())
                  .replace("{{bot_bomb_used}}", str(state["bot_bomb"]).lower())
                  .replace("{{user_input}}", u_in))

        res = client.models.generate_content(
            model=model_id,
            contents=[SYSTEM_STR, prompt],
        )
        raw = res.text.strip()
        if raw.startswith("```"):
            raw = raw.strip("`").removeprefix("json").strip()
        
        data = json.loads(raw)

        print(
            f"\nUser Move: {data['user_move']}"
            f"\nBot Move: {data['bot_move']}"
            f"\nValidity: {data['validity']}"
            f"\nWinner: {data['winner']}"
            f"\nNext: {data['next_action']}\n"
        )

        if "GAME_OVER" in data["next_action"] or "FINAL_RESULT" in data["next_action"]:
            break

        # Bomb state is updated strictly from model output.
        state["round"] += 1
        state["user_bomb"] = data["user_bomb_used"]
        state["bot_bomb"] = data["bot_bomb_used"]

if __name__ == "__main__":
    main()
