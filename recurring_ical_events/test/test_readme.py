'''
Test the README file.

This is necessary because a deployment does not work if the README file
has errors.

Credits: https://stackoverflow.com/a/47494076/1320237
'''
import restructuredtext_lint
from pathlib import Path

HERE = Path(__file__).parent
readme_path = HERE.parent.parent / "README.rst"

def test_readme_file():
    '''CHeck README file for errors.'''
    messages = restructuredtext_lint.lint_file(str(readme_path))
    error_message = "expected to have no messages about the README file!"
    for message in messages:
        print(message.astext())
        error_message += "\n" + message.astext()
    assert len(messages) == 0, error_message