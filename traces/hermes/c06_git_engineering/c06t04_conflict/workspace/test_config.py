from config import greeting, APP_NAME


def test_app_name():
    assert APP_NAME == "DemoApp"


def test_greeting_is_string():
    assert isinstance(greeting(), str) and "DemoApp" in greeting()


def test_greeting_combined():
    assert greeting() == "Hey there, valued user of DemoApp (v2)!"
