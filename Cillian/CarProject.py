#1#

#class Song:
#    name = ""
#    artist = ""
#    year = 0

#Song1 = Song()
#Song1.name = "Bohemian Rhapsody"
#Song1.artist = "Queen"
#Song1.year = 1975
#print(Song1.name, Song1.artist, Song1.year)

#2#

#class Song:
#    def __init__(self, name, artist, year):
#        self.name = name
#        self.artist = artist
#        self.year = year

#    def displayDetails(self):
#        print(f"Name: {self.name}")
#        print(f"Artist: {self.artist}")
#        print(f"Year: {self.year}")

#    def calculateAge(self):
#        age = 2026 - self.year
#        print(age)
    
#music = Song("Bohemian Rhapsody", "Queen", 1975)
#music.displayDetails()

#3#

class Person:
    def __init__(self, fname, lname):
        self.firstName = fname
        self.lastName = lname
    
    def printName(self):
        print(self.firstName, self.lastName)

class Student(Person):
    def __init__(self, fname, lname, year):
        super().__init__(fname, lname)
        self.gradYear = year

p2 = Student("Max", "Mustermann", 2019)
p2.printName()

print(f"Welcome {p2.firstName} {p2.lastName} to the year of {p2.gradYear}!")