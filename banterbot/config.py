import datetime
import logging

import uuid6

# Maximum number of retries in calls to the OpenAI API
RETRY_LIMIT = 3

# The number of seconds to wait if the OpenAI API raises a RateLimitError
RETRY_TIME = 60

# The default seed to use in all random generation
SEED = 1337

# The default language used in speech-to-text recognition
DEFAULT_LANGUAGE = "en-US"

# Set the log settings
logging_level = logging.INFO
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging_level)

# Define the type of UUID that should be used across all modules
generate_uuid = uuid6.uuid8

# Define the punctuation marks that can be used to split sentences into phrases for prosody selection.
PHRASE_DELIM = [",", ".", "?", "!", ":", ";", '"', "`", "|", "\n", "\t", "\r\n"]

# The amount of time that should be added to a "soft interruption" as defined in class `SpeechToText`.
INTERRUPTION_DELAY: datetime.timedelta = datetime.timedelta(seconds=0.75)
