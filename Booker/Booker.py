import requests
import datetime
import json
import random

class User:
    def __init__(self, guid, password):
        self.guid = guid
        self.session = requests.Session()
        login = self._process_login(password)
        self.name = login['firstname'].replace(',',' ')

    def _process_login(self, password):
        data = {
            'guid':self.guid,
            'password':password,
            'rememberMe':True
        }
        login = self.session.post('https://frontdoor.spa.gla.ac.uk/timetable/login',json=data)
        data = json.loads(login.content)
        return data

    def get_rooms(self, filter=None):
        req = self.session.get('https://frontdoor.spa.gla.ac.uk/timetable/booking/locations')
        rooms = json.loads(req.content)
        if filter:
            return [room for room in rooms if filter in room[1]]
        return rooms

    def _generate_dates(self, date, time, length):
        dates = []
        time = datetime.datetime.strptime(time, '%H:%M')
        for i in range(length*2):
            dates.append(f'{date} {time.strftime("%H:%M")}')
            time = time + datetime.timedelta(minutes=30)
        return dates

    def book_room(self, code, date, time, length):
        data = {
            "attendees":1,
            "dates":self._generate_dates(date, time, length),
            "locationId":code
            }
        booked = self.session.post('https://frontdoor.spa.gla.ac.uk/timetable/bookingv2', json=data)
        
        return booked.content

# IDK wtf is above this, THANKS MURPHY YOU LEGEND

# Need to set up reading this from a file of multiple (encrypted) login details and picking one at "random"
guid = "2668930o"
password = ""

#Initilising all of Murphys stuff
user = User(str(guid), str(password))

# Read the Seminar rooms from a json file
with open('rooms.json') as json_file:
    data = json.load(json_file)

# Pick a random room from the list
room_index = random.randint(0, len(data) - 1)

# Setting some variable to prep for the booking section
starting_room = room_index
next_week = datetime.date.today() + datetime.timedelta(days=7)
room_booked = False
morning_error = False

#booked = user.book_room("1730408", "2021-10-03", "16:00", 1) # A test book for room 408 on Sunday

# For booking, loop until it books a room, if the program loops through all the rooms provided
# from the json then it sends an error message to the Discord bot

# Morning Slot (9-12)
while not room_booked and not morning_error: # Loops until the room is booked or it errors
    booked = user.book_room(data[room_index]["id"], str(next_week), "08:00", 3) # Try to book a room
    print(room_index)
    if '{"showLecturer":true,"noTimetable":false}' not in str(booked): # Check if the room was successfully booked
        room_index += 1
        if room_index > len(data) - 1: 
            room_index = 0
        if room_index == starting_room: # If we have tried to book every room in the json, it errors
            morning_error = True
    else:
        room_booked = True
        morning_room = room_index

afternoon_error = False
room_booked = False

# This is the same as the morning section - im not commenting this too
# Afternoon time slot (12-15)
starting_room = room_index

while not room_booked and not afternoon_error:
    booked = user.book_room(data[room_index]["id"], str(next_week), "11:00", 3)
    
    if '{"showLecturer":true,"noTimetable":false}' not in str(booked):
        room_index += 1
        if room_index > len(data) - 1:
            room_index = 0
        if room_index == starting_room:
            afternoon_error = True
    else:
        room_booked = True
        afternoon_room = room_index

# This will eventually tell the discord bot if the room was booked successfully and what room
if morning_error: # Morning bookings
    print("unable to book morning time slot")
else:
    print("morning room booked successfully, room: " + str(data[morning_room]["name"]))
if afternoon_error: # Afternoon Bookings
    print("unable to book afternoon time slot")
else:
    print("afternoon room booked successfully, room: " + str(data[afternoon_room]["name"]))


# This nasty little bit of code takes a hot minute to execute and lists all the rooms we can book
"""
rooms = user.get_rooms()
print(rooms)
"""