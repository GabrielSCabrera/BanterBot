# Set up available voice emotions.
emotions = (
    "angry",
    "cheerful",
    "excited",
    "friendly",
    "hopeful",
    "sad",
    "shouting",
    "terrified",
    "unfriendly",
    "whispering",
)

default_emotion = "friendly"

# Set up available voice profiles.
neural_voices = {
    "Guy": ["male", "professional", "unemotional", "high-pitch"],
    "Tony": ["male", "professional", "unemotional", "medium-pitch"],
    "Davis": ["male", "casual", "expressive", "low-pitch"],
    "Jason": ["male", "casual", "unemotional", "high-pitch"],
    "Sara": ["female", "professional", "expressive", "medium-pitch"],
    "Aria": ["female", "casual", "unemotional", "high-pitch"],
    "Jenny": ["female", "casual", "expressive", "medium-pitch"],
    "Jane": ["female", "casual", "expressive", "high-pitch"],
    "Nancy": ["female", "casual", "expressive", "low-pitch"],
}

default_voice = "Jenny"
neural_voice_formatter = "en-US-{}Neural"

default_chat_gpt_model = "gpt-3.5-turbo"

openai_api_key_env_variable = "OPENAI_API_KEY"
