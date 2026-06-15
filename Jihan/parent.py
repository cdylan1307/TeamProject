class Person:
    def __init__(self, fname, lname):
        self.firstName = fname
        self.LastName = lname

    def printName(self):
        print(self.firstName, self.LastName)

class Student(Person):
    def __init__(self, fname, lname, year):
        super().__init__(fname, lname)
        self.gradyear = year



p2 = Student("Max", "Mustermann", 2023)
p2.printName()

print(f"Welcom {p2.firstName} {p2.LastName} to the year of {p2.gradyear} !")
        