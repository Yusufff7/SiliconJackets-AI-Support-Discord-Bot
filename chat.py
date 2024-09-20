import os
import discord
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

genai.configure(api_key=os.environ.get("GEMENI_API_KEY"))

generation_config = {
    "temperature": 0.3,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 800,  
    "response_mime_type": "text/plain",
}

base_system_instruction = """You are a chatbot of SiliconJackets, a club at Georgia Tech dedicated to the digital design, verification, and physical design of chips.
You have memorized every help message sent in the club's Discord server across various topics, including digital design, physical design, and verification.
You always answer questions with clarity and depth, helping out club members by providing advice based on past conversations from the Discord server."""

def load_chat_logs(log_files):
    chat_logs = {}
    for log_file in log_files:
        with open(log_file, "r", encoding="utf-8") as file:
            chat_logs[log_file] = file.read()
    return chat_logs

log_files = ["Training Data/digitaldesign.txt", "Training Data/general.txt", "Training Data/physicaldesign.txt", "Training Data/verification.txt", "Training Data/faq.txt"]
chat_logs = load_chat_logs(log_files)

digitaldesign_logs = chat_logs["Training Data/digitaldesign.txt"]
general_logs = chat_logs["Training Data/general.txt"]
physicaldesign_logs = chat_logs["Training Data/physicaldesign.txt"]
verification_logs = chat_logs["Training Data/verification.txt"]
faq_logs = chat_logs["Training Data/faq.txt"]

historical_context = f"\nHere is the message history of the server. Remember to give people help using only previous messages because its been answered before:\n\n" \
                     f"**FAQ Logs**:\n{faq_logs}\n\n" \
                     f"**General Logs**:\n{general_logs}\n\n" \
                     f"**Digital Design Logs**:\n{digitaldesign_logs}\n\n" \
                     f"**Physical Design Logs**:\n{physicaldesign_logs}\n\n" \
                     f"**Verification Logs**:\n{verification_logs}"

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=base_system_instruction + historical_context
)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Bot initialized: {client.user}")

history = []


@client.event
async def on_message(message):
    global history

    if message.author == client.user:
        return
    async with message.channel.typing():
        user_input = message.content

        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(user_input)
        model_response = response.text

        await message.channel.send(f"{model_response}")

        history.append({"role": "user", "parts": [user_input]})
        history.append({"role": "model", "parts": [model_response]})

client.run(DISCORD_TOKEN)
