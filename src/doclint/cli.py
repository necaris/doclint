import os

# TODO: Investigate lighter-weight control flow
import controlflow as cf


def setup_llm():
    """Set up the LLM connection through LangChain.

    If we have an Anthropic API key, use Claude 3.5 Haiku for speed. If we don't, try Ollama with Llama 3.2 3B (again for speed).

    Down the line, we probably want to use different models, but this is a good start.
    """
    if os.environ.get("ANTHROPIC_API_KEY"):
        from langchain_anthropic import ChatAnthropic

        model = ChatAnthropic(model="claude-3-5-haiku-20241022")

    else:
        from langchain_ollama import ChatOllama

        model = ChatOllama(model="llama3.2")

    try:
        model.invoke("Are you there, Meta? It's me, Doclint.")
    except Exception as e:
        raise AssertionError(
            "LLM could not be connected to. Do you have Anthropic or Ollama set up?"
        ) from e

    cf.defaults.model = model


def main():
    setup_llm()
    task = cf.Task(
        objective="Write a poem about the provided topic",
        instructions="Write four lines that rhyme",
        context={"topic": "AI"},
    )
    print(task.run())


if __name__ == "__main__":
    main()
