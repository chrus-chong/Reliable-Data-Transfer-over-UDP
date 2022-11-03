# Reliable-Data-Transfer-over-UDP

The aim of this project is to implement a reliable one-way chat program that sends
messages over an unreliable UDP channel that may either corrupt or drop packets
randomly (but will always deliver packets in order).

There are three programs involved in this project, Alice, UnreliNET and Bob (see
image below).
- Alice will send chat messages to Bob over UDP (and Bob may provide feedback
as necessary).
- The UnreliNET program is used to simulate the unreliable transmission channel
(in both directions) that randomly corrupt or drop packets. You can assume that
UnreliNET always delivers packets in order.
- Instead of sending packets directly to Bob, Alice will send all packets to UnreliNET.
UnreliNET may introduce bit errors or lose packets randomly. It then forwards
packets (if not lost) to Bob.
- When receiving feedback packets from Bob, UnreliNET may also corrupt them or
lose them with a certain probability before relaying them to Alice.

![image](https://user-images.githubusercontent.com/85006125/199656399-0ff04b8b-ac71-4899-bac8-3b933959afa0.png)

## How it works?

**1. UnreliNET Program** <br>
- To run UnreliNET on sunfire, type the following command: <br>
`java UnreliNET <P_DATA_CORRUPT> <P_DATA_LOSS> <P_ACK_CORRUPT> <P_ACK_LOSS> <unreliNetPort> <rcvPort>` <br>
- For example: <br>
`java UnreliNET 0.3 0.2 0.1 0.05 9000 9001` <br>
- The above command makes UnreliNET listen on port 9000 of localhost and forwards
all received data packets to Bob running on the same host with port 9001, with 30%
chance of packet corruption and 20% chance of packet loss. The UnreliNET program
also forwards ACK/NAK packets back to Alice, with a 10% packet corruption rate and
a 5% packet loss rate.
- Upon launching UnreliNET, the error statistics should be visible

![image](https://user-images.githubusercontent.com/85006125/199657870-addc7b0c-4755-44b4-b334-40b0245d09a0.png)

**_NOTE:_**  The source code for UnreliNET is created by the NUS CS2105 module teaching team and I do not take credit for its contents.

**2. Alice Program**
- Alice will read chat messages from standard input and send them to UnreliNET
(which will then forward to Bob as appropriate).
- The chat messages contain ASCII characters only, and there is no empty message (i.e. blank line).
- There’s no delay regarding the input to Alice.
To run Alice, type the following command:
`python3 Alice.py <unreliNetPort>`
<unreliNetPort> is the port number UnreliNET is listening to. For example:
`python3 Alice.py 9000`

**3. Bob Program**
- Bob receives chat messages from Alice (via UnreliNET) and prints them to standard output.
- The command to run the Python version of Bob is: <br>
`python3 Bob.py <rcvPort>`
- For example: <br>
`python3 Bob.py 9001`

## Running the programs
1. Bob.py should be launched in the first window.
2. Followed by UnreliNET in the second window.
3. Finally, launch Alice in a third window to start data transmission.

For the convenience, you can use the file redirection feature to let Alice read from a file (rather than from keyboard input).

For example, you can run Alice as follows: <br>
`python3 Alice.py 9000 < input1.txt`

Upon completion of data transmission, you can view the number of packets lost/corrupted/dropped in the UnreliNET window

![image](https://user-images.githubusercontent.com/85006125/199658173-5c820e05-0b30-4246-b2a7-b2eedef40385.png)
