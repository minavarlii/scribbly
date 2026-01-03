class Stroke:
    def __init__(self, color, size, tool):
        self.color = color
        self.size = size
        self.tool = tool
        self.points = []


class StrokeHistory:
    def __init__(self):
        self.strokes = []
        self.redo_stack = []

    def start_stroke(self, color, size, tool):
        s = Stroke(color, size, tool)
        self.strokes.append(s)
        self.redo_stack.clear()
        return s

    def add_point(self, stroke, p):
        stroke.points.append(p)

    def undo(self):
        if self.strokes:
            self.redo_stack.append(self.strokes.pop())

    def redo(self):
        if self.redo_stack:
            self.strokes.append(self.redo_stack.pop())

    def clear(self):
        self.strokes.clear()
        self.redo_stack.clear()