import argparse
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
        print(model.invoke("Are you there, LLM? It's me, Doclint."))
    except Exception as e:
        raise AssertionError(
            "LLM could not be connected to. Do you have Anthropic or Ollama set up?"
        ) from e

    cf.defaults.model = model


def main():
    setup_llm()
    # 1. Parse file using tree sitter
    # 2. Extract doc-ish comments
    # 3. Extract function / class the doc refers to
    # 4. Given the function as context, score the doc comment on
    #   - general guidelines (TODO: import some for the prompt)
    #   - describing the *why* vs the *what* (TODO: this should be something tunable)
    #   - relevance to the function it's attached to (comment drift)
    # 5. Extract functions / comments *touched by a diff* and run the above
    # 6. Explain the whole diff
    # 6. Expand to more languages
    # 7. Package up as a GHA / Pre-commit hook / etc
    #   - Provide configurable models
    #   - Tunables as above
    for doc, definition in captures:
        task = cf.Task(
            objective="Assess whether the documentation provides sufficient context",
            instructions=(
                "Critique the doc as it relates to the definition. "
                "Provide a score from 1 to 10. "
                "A doc that describes the definition but provides no additional information beyond a description of the code should receive a score of 1. "
                "Additional information as to why the code is written a certain way should result in a higher score."
            ),
            context={"doc": doc, "definition": definition},
            result_type=int,
        )
        print(task.run())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file")
    parser.add_argument("-r", "--repo")
    parser.add_argument("-d", "--diff-range")
    main(parser.parse_args())
