import requests
import datetime
import json
import random
import getpass
from time import sleep

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

class Booker:

    # For booking, loop until it books a room, if the program loops through all the rooms provided from the json
    def BookRoom(user, time, day, rooms, room): #time slot (9, 12, 15), day, user, rooms

        booking_error = False
        room_booked = False
        starting_room = room

        while not room_booked and not booking_error: # Loops until the room is booked or it errors
            sleep(1)
            booked = user.book_room(rooms[room]["id"], day, time, 3) # Try to book a room
            print(booked)
           
            if '{"showLecturer":true,"noTimetable":false}' not in str(booked): # Check if the room was successfully booked
                room += 1
               
                if room > len(rooms) - 1: # If we exceeded the 
                    room = 0
               
                if room == starting_room: # If we have tried to book every room in the json, it errors
                    return False
            
            else:
                room_booked = True

        return room

    # Need to set up reading this from a file of multiple (encrypted) login details and picking one at "random"
    guid = "2668930o"
    password = getpass.getpass("password: ")

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

    # Morning Slot (9-12)
    morning_slot = BookRoom(user, "08:00", next_week, data, room_index)
    sleep(1)
    # Afternoon Slot (12-15)
    afternoon_slot = BookRoom(user, "11:00", next_week, data, room_index)
    sleep(1)
    # Evening Slot (15-18)
    evening_slot = BookRoom(user, "14:00", next_week, data, room_index)


    # This will eventually tell the discord bot if the room was booked successfully and what room
    if morning_slot == False: # Morning bookings
        print("Unable to book morning time slot")
    else:
        print("Morning room booked successfully, room: " + str(data[morning_slot]["name"]))
    if afternoon_slot == False: # Afternoon Bookings
        print("Unable to book afternoon time slot")
    else:
        print("Afternoon room booked successfully, room: " + str(data[afternoon_slot]["name"]))
    if evening_slot == False: # Evening Bookings
        print("Unable to book evening time slot")
    else:
        print("Evening room booked successfully, room: " + str(data[evening_slot]["name"]))

    # This nasty little bit of code takes a hot minute to execute and lists all the rooms we can book
    """
    rooms = user.get_rooms()
    print(rooms)
    """