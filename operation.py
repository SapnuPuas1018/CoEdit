import time


class Operation:
    def __init__(self, op_type, text, line, char, timestamp=None):
        assert op_type in ("insert", "delete")
        self.op_type = op_type
        self.text = text
        self.line = line
        self.char = char
        self.timestamp = timestamp or time.time()

    def apply(self, content: str) -> str:
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
        return self.timestamp < other.timestamp

    def __str__(self):
        return (f"{self.op_type.capitalize()}('{self.text}' "
                f"at line {self.line}, char {self.char}, "
                f"time={self.timestamp:.3f})")