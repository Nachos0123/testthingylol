

class CurveTable:
    def __init__(self, data):
        self.keys = [(value["KeyTime"], value["KeyValue"]) for value in data]

    def eval(self, key):
        if key < self.keys[0][0]:
            return self.keys[0][1]

        if key >= self.keys[-1][0]:
            return self.keys[-1][1]

        index = next(i for i, k in enumerate(self.keys) if k[0] > key)

        prev = self.keys[index - 1]
        next_ = self.keys[index]

        fac = (key - prev[0]) / (next_[0] - prev[0])
        return prev[1] * (1 - fac) + next_[1] * fac
