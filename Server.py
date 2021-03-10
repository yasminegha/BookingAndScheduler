#from Project1.Client import MS
import sys
import json
import time


def clientServerConnectionOutput():
    RoomBooking = "  , __                     , __         _                         \n " \
                  "/|/  \                   /|/  \       | | o                 ()     \n  " \
                  "|___/ __  __  _  _  _    | __/__  __ | |    _  _   __,     /\   \n  " \
                  "| \  /  \/  \/ |/ |/ |   |   /  \/  \|/_)| / |/ | /  |    /  \/ \n" \
                  "  |  \_\__/\__/  |  |  |_/ |(__\__/\__/| \_|_/ |  |_\_/|/   \__/\ \n" \
                  "                                                      /|          \n" \
                  "                                                      \|         "
    print(RoomBooking)
    time.sleep(0.5)
    MeetingScheduler ="  ,__ __                                   _                  _\n"\
          " /|  |  |         o                 ()    | |        |       | |"\
          "\n  |  |  |  _  __|_   _  _   __,     /\ __ | |   _  __|       | | _  ,_  "\
          "\n  |  |  | |/ |/ | | / |/ | /  |    /  /   |/ \ |/ /  | |   | |/ |/  / |"\
          "\n  |  |  |_|__|__|_|_/ |  |_\_/|  //(__\___|  |_|__\_/|_/\_/|_|__|__/  |_/"\
          "\n                             /|"                                          \
          "\n                             \|\n"

    print(MeetingScheduler)


class Server:

    def __init__(self, responseType):
        self.responseType = responseType

    def getRequestType(self, responseType):
        responses = {
            "REQUEST": 1,
            "ACCEPT": 2,
            "REJECT": 3,
            "CANCEL": 4,
            "WITHDRAW": 5,
            "ADD": 6,
        }
        print(responses.get(responseType, "Invalid Response"))

    def REQUEST_MESSAGE(self):
        print("Requesting a Booking" + self.name)

    #server_msg = Server("ROOM UNAVAILABLE MESSAGE") # example of an instance
