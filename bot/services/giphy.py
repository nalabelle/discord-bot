import giphypop

class Giphy:
    """ Giphy library """

    def __init__(self):
        self.giphypop = giphypop.Giphy()

    def get(self, phrase : str):
        results = self.giphypop.translate(phrase=phrase)
        if results.url:
            return results.url

