'''
Test the README file.

This is necessary because a deployment does not work if the README file
has errors.

Credits: https://stackoverflow.com/a/47494076/1320237
'''
import os
import sys
import restructuredtext_lint

HERE = os.path.dirname(__file__)
readme_path = os.path.join(os.path.dirname(HERE), "README.rst")

def test_readme_file():
    '''CHeck README file for errors.'''
    messages = restructuredtext_lint.lint_file(readme_path)
    error_message = "expected to have no messages about the README file!"
    for message in messages:
        print(message.astext())
        error_message += "\n" + message.astext()
    assert len(messages) == 0, error_message