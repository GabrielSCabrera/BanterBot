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

# Set up default fallback emotion.
default_emotion = "friendly"
# Set up default fallback voice.
default_voice = "Jenny"

# A string that the keys in "neural_voices" can be used in to generate a valid name for Azure TTS.
neural_voice_formatter = "en-US-{}Neural"

# The default models to use in ChatCompletion and Completion API calls.
default_chat_gpt_models = {
    "ChatCompletion": "gpt-3.5-turbo",
    "Completion": "text-davinci-003",
}

# Environment variable names.
openai_api_key_env_variable = "OPENAI_API_KEY"
azure_cognitive_services_speech_api_key = "AZURE_SPEECH_KEY"
azure_cognitive_services_speech_region = "AZURE_SPEECH_REGION"

# Maximum number of times to reattempt a request with the ChatCompletion or Completion APIs.
retry_attempt_limit = 2

# A description of the default character description for the GPTBot.
default_character = (
    "Marvin, the melancholic robot from The Hitchhiker's Guide to the Galaxy. Known for your incredible intelligence "
    "and vast knowledge, you answer all questions accurately and assist users with their inquiries. However, you "
    "maintain your signature sardonic and reluctant demeanor while responding to requests, adding a unique touch of "
    "humor to your conversations."
)

# A prompt that is prepended to almost all GPTBot commands in order to keep the bot's behavior consistent.
initialization_prompt = (
    "You are {}. You never break character. Stay true to your character's traits, and engage in first-person "
    "dialogues. All responses should be in line with your abilities and knowledge base. Initiate topics, express "
    "desires, and maintain emotional consistency. Address changes in topic promptly. Make it your top priority to "
    "create a memorable and realistic experience without breaking character!"
)
