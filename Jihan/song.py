class Song:
    def __init__(self, name, artist, years):
        self.name = name
        self.artist = artist
        self.years = years
    def DisplayDetails(self):
        print(f"Name: {self.name}")
        print(f"Artist: {self.artist}")
        print(f"Years: {self.years}")

song = Song("BlueSky", "Jimmy", "2020")
song.DisplayDetails()