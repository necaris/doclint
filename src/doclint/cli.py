import argparse
import os
import subprocess

import unidiff
import controlflow as cf

from . import extractor


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


def main(opts: argparse.Namespace):
    if opts.file:
        captures = extractor.definitions_from_file(opts.file)
    elif opts.repo and opts.diff_range:
        output = subprocess.run(
            ["git", "diff", "-p", opts.diff_range],
            cwd=opts.repo,
            capture_output=True,
            text=True,
        )
        diff = unidiff.PatchSet.from_string(output.stdout)
        print(diff.modified_files)
        raise AssertionError("Diff logic not implemented yet.")
    else:
        raise AssertionError("Need either a file or a diff to parse.")

    setup_llm()
    # 2. Extract doc-ish comments
    #  - i.e. capture a function / class / module body
    #  - capture any docstrings adjacent to definition (e.g. strings or blocks of comments after (for Python))
    # 4. Given the function body as context, score the doc comment on
    #   - general guidelines (TODO: import some for the prompt)
    #   - describing the *why* vs the *what* (TODO: this should be something tunable)
    #   - relevance to the function it's attached to (comment drift)
    # 5. Extract functions / comments *touched by a diff* and run the above
    # 6. Explain the whole diff
    # 6. Expand to more languages
    # 7. Package up as a GHA / Pre-commit hook / etc
    #   - Provide configurable models
    #   - Tunables as above
    for doc, definition, _ in captures:
        print(doc)
        print(definition)
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
