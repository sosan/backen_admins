import subprocess
from json import JSONDecodeError

from requests_html import HTMLSession
from datetime import datetime
import json


class ManagerWeb:
    def __init__(self):
        self.web = HTMLSession()

    def getstreet(self, x, y):
        "https://reverse.geocoder.ls.hereapi.com/6.2/reversegeocode.json?apiKey=k-EckgQuyQOTGQoMy54SsslKuX9oMP8PFj2SyV-_wJM&mode=retrieveAddresses&prox=39.6156533,2.7755254&maxresults=1"
        uri = """https://reverse.geocoder.ls.hereapi.com/6.2/reversegeocode.json?apiKey=k-EckgQuyQOTGQoMy54SsslKuX9oMP8PFj2SyV-_wJM&mode=retrieveAddresses&prox={0},{1}&maxresults=1""".format(
            x, y)

        resultado = self.web.get(uri)
        if resultado != None:
            temp = json.loads(resultado.text)
            fulldireccion = temp["Response"]["View"][0]["Result"][0]["Location"]["Address"]["Label"]
            print(fulldireccion)
            splitdire = fulldireccion.split(",")
            print("2---{}".format(splitdire))

            if len(splitdire) == 2:  # sin nombre de la calle
                try:
                    separacion = splitdire[0].split(" ")
                    return "Ninguna", "0", separacion[0], separacion[1]  # calle= None, numero=None, cp, ciudad
                except IndexError:
                    print("211---{}".format(splitdire))
                    return "Ninguna", "0", separacion[0]
            else:
                #  _____ XXX XXXXXX, 5, 00000 XXXXXX (OOOO OOOOO), LLLLLLL
                try:

                    calle = " ".join(splitdire[0].split(" ")[1:])
                    separacion = splitdire[2].split(" ")

                    return calle, splitdire[1], separacion[1], separacion[2]  # calle= None, numero=None, cp, ciudad
                except IndexError:
                    print("3---{}".format(splitdire))
                    return splitdire[0], None, None, None
                    pass
        return None
