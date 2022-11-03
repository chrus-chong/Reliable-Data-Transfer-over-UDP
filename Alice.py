# blank
from socket import *
import sys
import zlib

class MessageSender:
    def __init__(self, portNumber: int):
        self.portNumber = portNumber
        self.sequenceNumber = 1 #This represents the highest sequence number of a packet that has been sent out thus far. First packet sent out should be number 1.
        self.socket = socket(AF_INET, SOCK_DGRAM) #SOCK_DGRAM for udp connection

    def run(self):
        strData:str = sys.stdin.read(Packet.maxSizeOfMessageData)
        while strData != "":
            packet = Packet(self.sequenceNumber, 0, strData.encode())
            self.socket.sendto(packet.getBytesPacket(), ("localhost", self.portNumber))
            #print(f"sent to port {packet.getBytesPacket()}")

            try:
                self.socket.settimeout(0.05)
                receivedBytesPacket = self.socket.recvfrom(Packet.maxSizeOfPacket)[0]
                receivedPacket:Packet = Packet.createReceivedPacketFromBytes(receivedBytesPacket)
                ## If ACK is equal to current seq number, increment. Else, if less, resend. This means sequence number should start from 1.
                ## if header is corrupted (ACK or seq num) --> receivedPacket is None
                ## what if header or data checksum is corrupted? not accounted for
                while receivedPacket is None or receivedPacket.ack != self.sequenceNumber:
                    self.socket.sendto(packet.getBytesPacket(), ("localhost", self.portNumber))
                    #print(f"sent to port {packet.getBytesPacket()}")

                    self.socket.settimeout(0.05)
                    receivedBytesPacket, serverAddress = self.socket.recvfrom(Packet.maxSizeOfPacket)
                    receivedPacket:Packet = Packet.createReceivedPacketFromBytes(receivedBytesPacket)
            except:
                # If timeout, continue and send again at beginning of while loop
                continue
            #print(f"Received with ack{receivedPacket.ack}")
            self.sequenceNumber += 1
            if self.sequenceNumber == 2**(Packet.maxSizeOfSeqNum*8):
                self.sequenceNumber = 1
            strData:str = sys.stdin.read(Packet.maxSizeOfMessageData)
        return
        



class Packet:
    maxSizeOfPacket = 64  # bytes including header
    maxSizeOfSeqNum = 2  # bytes. Can support sequence numbers up to 2^16 - 1 = 65535 
    maxSizeOfACK = 2  # bytes.
    maxSizeOfHeaderChecksum = 4  # bytes.
    maxSizeOfDataChecksum = 4  # bytes
    maxSizeOfMessageData = (
        maxSizeOfPacket - maxSizeOfSeqNum - maxSizeOfACK - maxSizeOfDataChecksum - maxSizeOfHeaderChecksum
    )
    byteOrder = "little"

    def __init__(self, sequenceNumber: int, ack: int, data: bytes):
        self.sequenceNumber: int = sequenceNumber
        self.ack: int = ack
        self.headerChecksum: int = zlib.crc32(
            sequenceNumber.to_bytes(Packet.maxSizeOfSeqNum, Packet.byteOrder)
            + ack.to_bytes(Packet.maxSizeOfACK, Packet.byteOrder)
        )
        self.dataChecksum: int = zlib.crc32(data)
        self.data: bytes = data
        if len(self.getBytesPacket()) > Packet.maxSizeOfPacket:
            raise Exception(f"Packet size exceeds {Packet.maxSizeOfPacket} bytes. Is currently {len(self.getBytesPacket())} bytes.")

    def getBytesPacket(self) -> bytes:
        byteSeqNum = self.sequenceNumber.to_bytes(
            Packet.maxSizeOfSeqNum, Packet.byteOrder
        )
        byteACK = self.ack.to_bytes(Packet.maxSizeOfACK, Packet.byteOrder)
        byteHeaderChecksum = self.headerChecksum.to_bytes(
            Packet.maxSizeOfHeaderChecksum, Packet.byteOrder
        )
        byteDataCheckSum = self.dataChecksum.to_bytes(
            Packet.maxSizeOfDataChecksum, Packet.byteOrder
        )
        return byteSeqNum + byteACK + byteHeaderChecksum + byteDataCheckSum + self.data

    def getSizeOfPacket(self):
        return len(self.getBytesPacket())

    def getDataChecksum(self):
        return self.dataChecksum
    
    def getData(self):
        return self.data

    def createReceivedPacketFromBytes(bytePacket: bytes):
        seqNumStop = Packet.maxSizeOfSeqNum
        seqNum = int.from_bytes(bytePacket[:seqNumStop], Packet.byteOrder)

        ackStop = seqNumStop + Packet.maxSizeOfACK
        ack = int.from_bytes(
            bytePacket[seqNumStop:ackStop],
            Packet.byteOrder,
        )

        headerChecksumStop = ackStop + Packet.maxSizeOfHeaderChecksum
        headerChecksum = int.from_bytes(
            bytePacket[ackStop:headerChecksumStop], Packet.byteOrder
        )

        dataChecksumStop = headerChecksumStop + Packet.maxSizeOfDataChecksum
        dataChecksum = int.from_bytes(
            bytePacket[headerChecksumStop:dataChecksumStop], Packet.byteOrder
        )

        data = bytePacket[dataChecksumStop:]
        receivedPacket = Packet(seqNum, ack, data)
        if (
            receivedPacket.dataChecksum != dataChecksum
            or receivedPacket.headerChecksum != headerChecksum
        ):
            return None
        return receivedPacket


portNumber = int(sys.argv[1])
alice = MessageSender(portNumber)
alice.run()