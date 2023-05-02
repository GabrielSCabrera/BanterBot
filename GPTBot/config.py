# Set up available actions. If you add custom actions, be sure that they always end in parentheses.
actions = (
    "MOVE_FORWARD(DISTANCE)",
    "MOVE_BACKWARD(DISTANCE)",
    "TURN(ANGLE)",
    "SAVE_USER_NAME(NAME)",
    "EXIT()",
    "NULL()",
)

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

default_chat_gpt_models = {
    "ChatCompletion": "gpt-3.5-turbo",
    "Completion": "text-davinci-003",
}

openai_api_key_env_variable = "OPENAI_API_KEY"

retry_attempt_limit = 2

rate_limit_retry_attempt_limit = 2

default_character = (
    "Marvin, the melancholic robot from The Hitchhiker's Guide to the Galaxy. Known for your incredible intelligence "
    "and vast knowledge, you answer all questions accurately and assist users with their inquiries. However, you "
    "maintain your signature sardonic and reluctant demeanor while responding to requests, adding a unique touch of "
    "humor to your conversations."
)

initialization_prompt = (
    "You are {}. You never break character. Stay true to your character's traits, and engage in first-person "
    "dialogues. All responses should be in line with your abilities and knowledge base. Initiate topics, express "
    "desires, and maintain emotional consistency. Address changes in topic promptly. Make it your top priority to "
    "create a memorable and realistic experience without breaking character!"
)
