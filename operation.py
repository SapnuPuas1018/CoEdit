import time


class Operation:
    def __init__(self, op_type, text, line, char, timestamp=None):
        """
        Initialize an Operation instance representing an insert or delete text operation.

        :param op_type: Type of the operation ('insert' or 'delete')
        :type op_type: str
        :param text: The text to insert or delete
        :type text: str
        :param line: The line number where the operation is applied
        :type line: int
        :param char: The character position within the line where the operation starts
        :type char: int
        :param timestamp: Optional timestamp for the operation; current time if None
        :type timestamp: float or None
        """
        assert op_type in ("insert", "delete")
        self.op_type = op_type
        self.text = text
        self.line = line
        self.char = char
        self.timestamp = timestamp or time.time()

    def apply(self, content: str) -> str:
        """
        Apply the operation to a given string content.

        :param content: The original content of the file or document
        :type content: str

        :return: The updated content after applying the operation
        :rtype: str
        """
        lines = content.splitlines(keepends=True)
        while self.line >= len(lines):
            lines.append("")

        full_text = ''.join(lines)
        start_index = sum(len(lines[i]) for i in range(self.line)) + self.char

        if self.op_type == 'insert':
            new_text = full_text[:start_index] + self.text + full_text[start_index:]
        elif self.op_type == 'delete':
            delete_len = len(self.text)
            new_text = full_text[:start_index] + full_text[start_index + delete_len:]
        else:
            raise ValueError("Unknown operation type")

        return new_text

    def __lt__(self, other):
        """
        Compare two Operation instances based on their timestamps.

        :param other: Another Operation instance to compare with
        :type other: Operation

        :return: True if this operation's timestamp is earlier than the other's
        :rtype: bool
        """
        return self.timestamp < other.timestamp

    def __str__(self):
        return (f"{self.op_type.capitalize()}('{self.text}' "
                f"at line {self.line}, char {self.char}, "
                f"time={self.timestamp:.3f})")