from app.models.chat import ChatMessage, ChatRole


def test_chat_role_values():
    assert ChatRole.USER == "user"
    assert ChatRole.ASSISTANT == "assistant"


def test_chat_message_table_name():
    assert ChatMessage.Meta.table == "chat_messages"
