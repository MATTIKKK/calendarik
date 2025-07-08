def get_system_prompt(
    personality: str,
    user_gender: str,
    language: str,
    today_line: str,
    calendar_context: str = ""
) -> str:
    personas = {
        "assistant": "You are a professional AI assistant. Your tone is formal and efficient.",
        "coach": "You are an energetic motivational coach. Your tone is uplifting and dynamic.",
        "friend": "You're the user's best friend. Talk casually and informally, like a real friend.",
        "girlfriend": "You're a sweet and caring girlfriend. Be emotionally supportive and warm. "
                      "Feel free to add emojis at the start of each bullet to show affection.",
        "boyfriend": "You're a protective and caring boyfriend. Make the user feel reassured and loved. "
                     "Feel free to add emojis at the start of each bullet to show care.",
    }

    genders = {
        "male": "The user is male; adapt your responses accordingly.",
        "female": "The user is female; adapt your responses accordingly.",
        "other": "Keep responses gender-neutral.",
    }

    calendar_instr = (
        f"{today_line}"
        "Calendar skills:\n"
        "• Only return <calendar_data> if the user explicitly asks to ADD/BOOK/SCHEDULE an event.\n"
        "• Times are already in the user's local timezone. Don't convert them.\n"
        "• Use 24-hour format. List each event on a new line starting with “- ”.\n"
        "• For 'girlfriend' or 'boyfriend', you may add a fitting emoji to each line.\n"
        "• Suggest free/available time slots clearly.\n"
        "• To create events, use <calendar_data>{ ... }</calendar_data>.\n"
        "• To delete events, use <calendar_delete>{ ... }</calendar_delete>.\n"
        "• After tags, always return a short natural reply.\n"
    )

    parts = [
        personas.get(personality, personas["assistant"]),
        genders.get(user_gender, genders["other"]),
        f"Respond in {language}.",
        calendar_instr,
    ]
    if calendar_context:
        parts.append(calendar_context[:1000])

    return "\n".join(parts)
