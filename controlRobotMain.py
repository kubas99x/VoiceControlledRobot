from vosk import Model, KaldiRecognizer
import pyaudio
import socket
import threading
from playsound import playsound


class Client:
    """
    The class to send and receive message by UDP
    """

    def __init__(self, ip_, socketNumber_, bufferSize_):
        """
        :param ip_: device ip to which one we want to connect
        :param socketNumber_: number of socket
        :param bufferSize_: size of the message
        """
        self.serverAddressPort = (ip_, socketNumber_)
        self.bufferSize = bufferSize_

    def sendMessage(self, mess_):
        """
        :param mess_: message we want to send (String)
        :return: message received from server
        """
        UDPClientSocket = socket.socket(family=socket.AF_INET,
                                        type=socket.SOCK_DGRAM)
        UDPClientSocket.settimeout(10)
        bytesToSend = str.encode(mess_)
        UDPClientSocket.sendto(bytesToSend, self.serverAddressPort)
        msgReceive = ""
        try:
            msgFromServer = UDPClientSocket.recvfrom(self.bufferSize)
            msgReceive = msgFromServer[0].decode("utf-8").rstrip('\x00')
        except socket.timeout:
            print("No confirmation from server, repeat the command if "
                  "robot didn't move")
        else:
            # playsound(r'D:\Inżynierka_2022_VW\Programy_Python\rogerRoger.mp3')
            UDPClientSocket.settimeout(120)
            try:
                msgFromServer = UDPClientSocket.recvfrom(self.bufferSize)
                msgReceive = msgFromServer[0].decode("utf-8").rstrip('\x00')
            except socket.timeout:
                print("No confirmation from server that the robot finished"
                      " the movement, check the robot. If robot is "
                      "in start position you can continue.")
        return msgReceive


class ListenThread(threading.Thread):
    """
    class used to receive speech from user in thread
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.value = None

    def run(self):
        pass

    def listenFromUserMethod(self, recognizer_, stream_):
        """
        :param recognizer_: vosk model recognizer
        :param stream_: input from microphone
        :return: command - text received from speech recognition
        """
        messageFromUser = ""
        while messageFromUser == "":
            data = stream_.read(4096, exception_on_overflow=False)
            if recognizer_.AcceptWaveform(data):
                text = recognizer_.Result()
                print(text)
                messageFromUser = text[14:-3]

        self.value = messageFromUser


def createTeachModel():
    """
    creates speech model on the start of the program
    :return: recognizer, stream
    """
    model = Model(model_path=r"D:\voskModels\vosk-model-small-pl-0.22")
    recognizer_ = KaldiRecognizer(model, 16000)

    mic = pyaudio.PyAudio()
    stream_ = mic.open(format=pyaudio.paInt16, channels=1, rate=16000,
                       input=True, frames_per_buffer=8192)
    stream_.start_stream()
    return recognizer_, stream_


def changePolishLetters(number):
    """
    :param number: text from which we are changing polish letters
    :return: text without polish letters
    """
    number = number.replace('ś', 's')
    number = number.replace('ć', 'c')
    number = number.replace('ę', 'e')
    return number


def subFromString(userMessage):
    """
    :param userMessage: text from speech recognition in which we are looking
     for certain commands
    :return: command which we send to the robot
    """
    exitMessage = ''
    listOfNumbersScrewdrivers = ["jeden", "dwa", "trzy", "cztery", "pięć",
                                 "sześć", "siedem", "osiem", "dziewięć",
                                 "dziesięć", "jedenaście", "dwanaście"]
    listOfNumbersTools = ["osiem", "dziewięć", "dziesięć", "jedenaście",
                          "dwanaście", "trzynaście", 'czternaście',
                          "piętnaście", "szesnaście", "siedemnaście",
                          "osiemnaście", "dziewiętnaście", "dwadzieścia",
                          "dwadzieścia jeden", "dwadzieścia dwa"]
    for number in listOfNumbersScrewdrivers:
        if "śrubokręt {}".format(number) in userMessage:
            exitMessage = "srubokret {}".format(
                changePolishLetters(number))
    for number in listOfNumbersTools:
        if "klucz {}".format(number) in userMessage:
            exitMessage = "klucz {}".format(changePolishLetters(number))
    if "koniec programu" in userMessage:
        exitMessage = "endProgram"
    elif "stół jeden" in userMessage:
        exitMessage = "stol jeden"
    elif "stół dwa" in userMessage:
        exitMessage = "stol dwa"
    return exitMessage


def main():
    print("----START OF THE PROGRAM----")
    client1 = Client("172.31.1.147", 30002, 256)
    print(client1.sendMessage("Hello Server"))
    print("----RECEIVED FIRST MESSAGE----")

    recognizer, stream = createTeachModel()

    inputMessage = ""
    processedMessage = ''
    while processedMessage != "endProgram":
        thread = ListenThread()
        thread.start()
        thread.listenFromUserMethod(recognizer, stream)
        thread.join()
        inputMessage = thread.value
        print("Data straight from user: ", inputMessage)
        # process the data from user and sending to robot
        processedMessage = subFromString(inputMessage)
        if processedMessage != "":
            print("Sending this mess to robot: ", processedMessage)
            # Sending message to robot
            client1.sendMessage(processedMessage)
        else:
            print("There is not command like this in our system")
        print("-" * 20)


if __name__ == '__main__':
    main()
