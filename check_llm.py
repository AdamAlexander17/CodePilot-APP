"""One-off script to verify the LLM connection works. Delete after use."""

from codepilot.llm.factory import get_chat_model

model = get_chat_model("fast")
response = model.invoke("Reply with exactly the word: pong")
print(response.content)
