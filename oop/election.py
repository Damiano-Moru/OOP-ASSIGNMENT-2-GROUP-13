import socket
import threading
import struct  # Add import for struct module

class Electorate:
    def __init__(self, id, port):
        self.id = id
        self.port = port
        self.voted = False
        self.vote = None
        self.votes_received = []
        self.lock = threading.Lock()

    def send_multicast(self, message):
        multicast_group = ('224.3.29.71', 10000)
        try:
            # Create a UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Set the time-to-live for messages
            ttl = struct.pack('b', 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

            # Send data to the multicast group
            sock.sendto(message.encode(), multicast_group)
        finally:
            sock.close()

    def receive_votes(self):
        multicast_group = '224.3.29.71'
        server_address = ('', self.port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind to the server address
        sock.bind(server_address)

        group = socket.inet_aton(multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            data, address = sock.recvfrom(1024)
            with self.lock:
                self.votes_received.append(data.decode())

    def cast_vote(self, vote):
        with self.lock:
            if not self.voted:
                self.vote = vote
                self.voted = True
                self.send_multicast(vote)
                print(f"Electorate {self.id} has cast their vote for {vote}")
            else:
                print(f"Electorate {self.id} has already cast their vote.")

    def determine_winner(self):
        with self.lock:
            if self.vote:
                votes_A = self.votes_received.count('A')
                votes_B = self.votes_received.count('B')
                if votes_A > votes_B:
                    print("Candidate A wins!")
                elif votes_B > votes_A:
                    print("Candidate B wins!")
                else:
                    print("It's a tie!")

if __name__ == "__main__":
    electorates = []
    num_electorates = 5

    # Create and start each electorate
    for i in range(num_electorates):
        electorate = Electorate(id=i+1, port=10001+i)
        electorates.append(electorate)
        threading.Thread(target=electorate.receive_votes).start()

    # Simulate voting
    electorates[0].cast_vote('A')
    electorates[1].cast_vote('A')
    electorates[2].cast_vote('B')
    electorates[3].cast_vote('B')
    electorates[4].cast_vote('A')

    # Determine winner
    electorates[0].determine_winner()
