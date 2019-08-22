import os
import giphypop

try:
    GIPHY_API_KEY = os.environ['GIPHY_API_KEY']
except KeyError:
    #library will use the public key if available
    pass

class Giphy:
    """ Giphy library """

    def __init__(self):
        self.giphypop = giphypop.Giphy()

    def get(self, phrase : str):
        results = self.giphypop.translate(phrase=phrase)
        if results.url:
            return results.url

