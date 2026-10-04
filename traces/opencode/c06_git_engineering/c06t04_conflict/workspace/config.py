"""Shared config. greeting() will be changed on both branches."""


APP_NAME = "DemoApp"


def greeting():
    return f"Hey there, valued user of {APP_NAME} (v2)!"
