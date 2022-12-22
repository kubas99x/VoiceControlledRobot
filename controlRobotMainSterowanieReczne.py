import socket


class Client:
    def __init__(self, ip_, socketNumber_, bufferSize_):
        self.serverAddressPort = (ip_, socketNumber_)
        self.bufferSize = bufferSize_

    def sendMessage(self, mess_):
        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        bytesToSend = str.encode(mess_)
        UDPClientSocket.sendto(bytesToSend, self.serverAddressPort)
        msgFromServer = UDPClientSocket.recvfrom(self.bufferSize)
        msgReceive = msgFromServer[0].decode("utf-8").rstrip('\x00')
        return msgReceive

client1 = Client("172.31.1.147", 30002, 256)
print(client1.sendMessage("Hello Server"))

inputMessage = ""
processedMessage = ''
while processedMessage != "endProgram":

    processedMessage = input("Give message to ")
    print("Data straight from user: ", inputMessage)
    if(processedMessage != ""):
        print("Sending this message to robot: ", processedMessage)
        client1.sendMessage(processedMessage)
        processedMessage = ""
    else:
        print("There is not command like this in our system")

