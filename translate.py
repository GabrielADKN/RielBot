from deep_translator import GoogleTranslator

def translator(text, src, dest):
    translated = GoogleTranslator(source=src, target=dest).translate(text)
    return translated