
class LabelList:
    def __init__(self):
        self.labeledList = {}

    def insert(self, label, item):
        if label not in self.labeledList:
            self.labeledList[label] = []
        self.labeledList[label].append(item)

    def __getitem__(self, label):
        return self.labeledList[label]




