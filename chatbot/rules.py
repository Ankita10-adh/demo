import re

def get_bot_response(message):
    message = message.lower().strip()  # 🔥 IMPORTANT

    rules = {
        r"\b(hi|hello|hey)\b": "Hello 👋 Welcome to Karyathalo!",
        r"\b(job|jobs|vacancy)\b": "Check Jobs section for latest vacancies.",
        r"\b(register|signup)\b": "Click Sign Up to create account.",
        r"\b(login|signin)\b": "Use email & password to login.",
    }

    for pattern, reply in rules.items():
        if re.search(pattern, message):
            return reply

    return "Sorry 😕 I didn’t understand that."
