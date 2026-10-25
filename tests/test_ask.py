import sys

from app import ask as ask_module


class FakeResponse:
    text = "回答"
    usage_metadata = None


class FakeChat:
    def __init__(self):
        self.questions = []

    def send_message(self, question):
        self.questions.append(question)
        return FakeResponse()


class FakeChats:
    def __init__(self, chat):
        self.chat = chat
        self.created = 0

    def create(self, *, model):
        assert model == ask_module.MODEL
        self.created += 1
        return self.chat


def test_main_keeps_one_chat_for_follow_up_questions(monkeypatch, capsys):
    chat = FakeChat()
    chats = FakeChats(chat)

    class FakeClient:
        def __init__(self, *, api_key):
            assert api_key == "test-key"
            self.chats = chats

    questions = iter(["追質問", "exit"])
    monkeypatch.setattr(sys, "argv", ["app.ask", "最初の質問"])
    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr("builtins.input", lambda _prompt: next(questions))

    ask_module.main()

    assert chats.created == 1
    assert chat.questions == ["最初の質問", "追質問"]
    assert capsys.readouterr().out.count("回答") == 2
