from app import build_message


def main() -> None:
    message = build_message()
    assert message == "Hello, AgentFlow!", message
    print("SMOKE_OK")


if __name__ == "__main__":
    main()
