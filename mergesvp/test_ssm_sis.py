# client example

import socket
import time
import sys
import os

import struct
from datetime import date, datetime
from typing import List, Tuple

import threading
from enum import Enum


def pack_nav(latitude: float, longitude: float, timestamp: datetime):
    length = 0
    datagram_id = 0x50
    em_model_number = 3
    date = int(datetime.strftime(timestamp, "%Y%m%d"))
    time = int(datetime.strftime(timestamp, "%H%M%S"))
    latitude_val = int(latitude * 20000000)
    longitude_val = int(longitude * 10000000)

    data = struct.pack(
        (
            "<"
            "B"    # length
            "B"    # datagram ID
            "H"    # EM Model number
            "I"    # date
            "I"    # time
            "H"    # position counter
            "H"    # System / serial number
            "i"    # Latitude in decimal degrees*20000000
            "i"    # Longitude in decimal degrees*20000000
            "H"    # Measure of position fix quality in cm
            "H"    # Speed of vessel over ground in cm/s
            "H"    # Course of vessel over ground in 0.01deg
            "H"    # Heading of vessel in 0.01deg
            "B"    # Position system descriptor
            "B"    # Number of bytes in input datagram
            "B"    # End identifier = ETX (Always 03h)
            "H"     # Check sum of data between STX and ETX
        ),
        length,
        datagram_id,
        em_model_number,
        date,
        time,
        0,
        0,
        latitude_val,
        longitude_val,
        0,
        0,
        0,
        0,
        0,
        0,
        0x03,
        0
    )

    return data


def pack_svp(
        timestamp: datetime,
        depth_and_speed: List[Tuple[float, float]]
):
    length = 0
    start_identifier = 0x02
    datagram_id = 0x55
    em_model_number = 3
    date = int(datetime.strftime(timestamp, "%Y%m%d"))
    time = int(datetime.strftime(timestamp, "%H%M%S"))

    data = struct.pack(
        (
            "<"
            "B"    # length
            "B"    # datagram type
            "H"    # EM Model number
            "I"    # date
            "I"    # time
            "H"    # profile counter
            "H"    # System / serial number
            "I"    # date profile was created
            "I"    # time profile was created
            "H"    # Number of entries
            "H"    # Depth resolution in cm
        ),
        length,
        datagram_id,
        em_model_number,
        date,
        time,
        0,
        0,
        date,
        time,
        len(depth_and_speed),
        1
    )
    data = bytearray(data)

    for (depth, speed) in depth_and_speed:
        entry_data = struct.pack(
            (
                "<"
                "I"    # length
                "I"    # start identifier
            ),
            int(depth),
            int(speed)
        )
        data.extend(entry_data)

    return bytes(data)


class State(Enum):
    INITIALIZING = 1
    INITIAL_PROFILE_REQUESTED = 2
    INITIAL_PROFILE_SENT = 3
    INITIAL_PROFILE_RECEIVED = 4
    INITIAL_PROFILE_SENT_BACK = 5
    ALL_NAV_SENT = 6
    SVP_RECEIVED = 7
    RESEND_NAV = 8


class StateObject:
    """ Manages state across the client and server threads
    """

    def __init__(self) -> None:
        self._state = State.INITIALIZING
        self._last_state = None
        self.exit = False

        self.back_datagram = None
        self.nav_data = []
        self.svp_data = []

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, val):
        self._last_state = self.state
        self._state = val
        print(f"state change {self._last_state} -> {self._state}")


class ClientThread(threading.Thread):

    def __init__(self, state_object: StateObject, ip: str, port: int) -> None:
        super().__init__()
        self.state_object = state_object
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_MULTICAST_TTL,
            20
        )
        self.nav_data_send_time = None
        svp = [
            (0, 1500.0),
            (100, 1500.0)
        ]
        self.tmp_svp_data = pack_svp(timestamp=datetime.now(), depth_and_speed=svp)

    def __send_initial_nav(self):
        print("__send_initial_nav")
        nav_data = pack_nav(-45.1, 123.2, datetime.now())
        self.socket.sendto(nav_data, (self.ip, self.port))

        time.sleep(1.0)   # don't spam SSM


    def __send_initial_profile(self):
        self.socket.sendto(self.tmp_svp_data, (self.ip, self.port))


    def __send_back_profile(self):
        self.tmp_svp_data = self.state_object.back_datagram
        self.socket.sendto(self.tmp_svp_data, (self.ip, self.port))


    def __send_nav_data(self) -> bool:
        if len(self.state_object.nav_data) == 0:
            return False
        self.nav_data = state_object.nav_data.pop(0)
        self.nav_data_send_time = datetime.now()
        print(f"sending {self.nav_data}")
        time.sleep(10)

        nav_data_bytes = pack_nav(
            self.nav_data[1],
            self.nav_data[0],
            self.nav_data[2])
        self.socket.sendto(nav_data_bytes, (self.ip, self.port))
        time.sleep(1)

        return True

    def __resend_nav_date(self) -> None:
        self.nav_data_send_time = datetime.now()
        print(f"REsending {self.nav_data}")
        # time.sleep(10)

        nav_data_bytes = pack_nav(
            self.nav_data[1],
            self.nav_data[0],
            self.nav_data[2])
        self.socket.sendto(nav_data_bytes, (self.ip, self.port))
        time.sleep(1)

    def run(self) -> None:
        while not self.state_object.exit:
            if self.state_object.state == State.INITIALIZING:
                self.__send_initial_nav()
            elif self.state_object.state == State.INITIAL_PROFILE_REQUESTED:
                self.__send_initial_profile()
                self.state_object.state = State.INITIAL_PROFILE_SENT
            elif self.state_object.state == State.INITIAL_PROFILE_RECEIVED:
                self.__send_nav_data()
                self.__send_back_profile()
                
                self.state_object.state = State.INITIAL_PROFILE_SENT_BACK
                time.sleep(2.0)
            elif self.state_object.state == State.INITIAL_PROFILE_SENT_BACK:
                if self.__send_nav_data():
                    self.state_object.state = State.INITIAL_PROFILE_SENT
                else:
                    self.state_object.state = State.ALL_NAV_SENT
            elif self.state_object.state == State.INITIAL_PROFILE_SENT:
                if self.nav_data_send_time is not None:
                    dt = datetime.now() - self.nav_data_send_time
                    if dt.total_seconds() > 6:
                        self.state_object.state = State.RESEND_NAV
            elif self.state_object.state == State.RESEND_NAV:
                self.__resend_nav_date()
                self.state_object.state = State.INITIAL_PROFILE_SENT
            elif self.state_object.state == State.ALL_NAV_SENT:
                print("exit set")
                self.state_object.exit = True
            
            time.sleep(0.2)


class ServerThread(threading.Thread):

    def __init__(self, state_object: StateObject, ip: str, port: int) -> None:
        super().__init__()
        self.state_object = state_object

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, port))
        self.socket.settimeout(5.0)

    def _process_txt_svp(self, txt: str):
        depth_and_speed = []
        lines = txt.splitlines()
        lines = lines[1:-1]  # remove first and last lines
        
        for line in lines:
            line_bits = line.split(',')
            depth = float(line_bits[0]) * 100
            speed = float(line_bits[1]) * 10
            depth_and_speed.append((depth, speed))

        svp_data = pack_svp(datetime.now(), depth_and_speed)
        self.state_object.back_datagram = svp_data


    def run(self) -> None:
        while not self.state_object.exit:
            try:
                data, addr = self.socket.recvfrom(4096)  # buffer size is 1024 bytes
                txt = data.decode('utf-8')

                if txt.startswith("$SMR20,EMX=710"):
                    self.state_object.state = State.INITIAL_PROFILE_REQUESTED
                elif txt.startswith("$MVS01"):
                    print("received SVP from SSM")
                    self._process_txt_svp(txt)
                    self.state_object.state = State.INITIAL_PROFILE_RECEIVED

                time.sleep(0.2)
            except socket.timeout:
                print("socket timeout")
                time.sleep(0.1)
                continue



ip = 'localhost'
server_port = 4001
client_port = 16103

state_object = StateObject()
client = ClientThread(ip=ip, port=client_port, state_object=state_object)
server = ServerThread(ip=ip, port=server_port, state_object=state_object)


test_nav_data = [
    [147.5993694178344, -17.214294629299363, datetime.now()],
    [147.99819964616324, -17.406760982095005, datetime.now()],
    [148.33694665945947, -17.232192378378375, datetime.now()],
    [148.4115772, -17.3989903, datetime.now()],
    [146.16200744068598, -16.742423021990582, datetime.now()]
]
state_object.nav_data = test_nav_data


def main():

    client.start()
    server.start()

    print("client and server started")
    for t in [client, server]:
        t.join()
    print("client and server finished")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            state_object.exit = True
            sys.exit(0)
        except SystemExit:
            os._exit(0)

