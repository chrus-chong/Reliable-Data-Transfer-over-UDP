# blank
from socket import *
import sys
import zlib

class MessageReceiver:
    def __init__(self, portNumber:int):
        self.portNumber = portNumber
        self.ack = 0 # Represents the cumulative number of packets that Bob has received up till now.
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(('', self.portNumber))
    
    def run(self):
        ## Bob will keep on running until it is interrupted
        while True:
            receivedBytesPacket, senderAddress = self.socket.recvfrom(Packet.maxSizeOfPacket)
            receivedPacket:Packet = Packet.createReceivedPacketFromBytes(receivedBytesPacket)
            if receivedPacket is None:
                ## That means data got corrupted
                responsePacket = Packet(0,self.ack, b"")
                self.socket.sendto(responsePacket.getBytesPacket(), ("localhost", senderAddress[1]))
                continue
            ##If not corrupted, ACK is now the sequence number of the latest packet received (unless it is a duplicate)
            if receivedPacket.sequenceNumber > self.ack or receivedPacket.sequenceNumber == 1:
                self.ack = receivedPacket.sequenceNumber
                sys.stdout.write(receivedPacket.getData().decode())
            responsePacket = Packet(0,self.ack, b"")
            self.socket.sendto(responsePacket.getBytesPacket(), ("localhost", senderAddress[1]))
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
            raise Exception(f"Packet size exceeds {Packet.maxSizeOfPacket} bytes.")

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
bob = MessageReceiver(portNumber)
bob.run()