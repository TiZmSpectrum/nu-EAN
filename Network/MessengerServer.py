from twisted.internet.protocol import Protocol, DatagramProtocol

from Framework.Server.Messenger import *
from Logger import Log
from Utilities.Packet import Packet


class TCPHandler(Protocol):
    def __init__(self):
        self.CONNOBJ = None
        self.logger = Log("MessengerServer", "\033[36;21m")
        self.logger_err = Log("MessengerServer", "\033[36;1;41m")

    def connectionMade(self):
        self.ip, self.port = self.transport.client
        self.transport.setTcpNoDelay(True)

        self.logger.new_message("[" + self.ip + ":" + str(self.port) + "] connected", 1)

    def connectionLost(self, reason):
        self.logger.new_message("[" + self.ip + ":" + str(self.port) + "] disconnected ", 1)

        if self.CONNOBJ is not None:
            self.CONNOBJ.IsUp = False
            del self

        return

    def dataReceived(self, data):
        packet_type = data[:4]
        packet_data = data[12:]

        dataObj = Packet(packet_data).dataInterpreter()
        self.logger.new_message("[" + self.ip + ":" + str(self.port) + "]<-- " + repr(data), 3)

        if packet_type == 'AUTH':
            AUTH.ReceiveRequest(self, dataObj)
        elif packet_type == 'RGET':
            RGET.ReceiveRequest(self, dataObj)
        elif packet_type == 'EPGT':
            EPGT.ReceiveRequest(self, dataObj)
        elif packet_type == 'PSET':
            PSET.ReceiveRequest(self, dataObj)
        elif packet_type == 'USCH':
            USCH.ReceiveRequest(self, dataObj)
        #elif packet_type == 'GDAT':
        #    GDAT.ReceiveRequest(self, dataObj)
        #elif packet_type == 'ECNL':
        #    ECNL.ReceiveRequest(self, dataObj)
        else:
            self.logger_err.new_message(
                "[" + self.ip + ":" + str(self.port) + ']<-- Got unknown message type (' + packet_type + ")", 2)


class UDPHandler(DatagramProtocol):
    def __init__(self):
        self.logger = Log("MessengerServer", "\033[32;21m")
        self.logger_err = Log("MessengerServer", "\033[32;1;41m")

    def datagramReceived(self, datagram, addr):
        packet_type = datagram[:4]
        packet_data = datagram[12:]
    
        dataObj = Packet(packet_data).dataInterpreter()
        self.logger.new_message("[" + addr[0] + ":" + str(addr[1]) + "]<-- " + repr(datagram), 3)
    
        #if packet_type == 'ECHO':
        #    ECHO.ReceiveRequest(self, dataObj, addr)
        #else:
        self.logger_err.new_message("[" + addr[0] + ":" + str(addr[1]) + "][UDP] Received unknown packet type! (" + packet_type + ")", 2)
    
