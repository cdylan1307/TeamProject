class Song:
    def __init__(self,name, artist, years):
        self.name = name
        self.artist = artist
        self.years = years

    def displayDetails(self):
        print(f"Name: {self.name}")
        print(f"Artist: {self.artist}")
        print(f"Years: {self.years}")

    def calculateAge(self):
        age = 2026 - int(self.years)
        return age
    

audi = Song("BlueSky", "Jimmy", "2020")
print(audi.calculateAge())
audi.displayDetails()