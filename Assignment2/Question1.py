from flask import Flask, render_template      

app = Flask(__name__)

@app.route("/<text>")
def home(text):
    return generateResponse(text)

def generateResponse(text):
    #remove any non letters in the string
    word = ''.join([i for i in text if i.isalpha()])

    result = ''

    for letter in word:
        if letter.isupper():
            result+=result.join(letter.lower())
        if letter.islower():
            result+=result.join(letter.upper())
        
    return "Welcome, "+ result+", to my CSCB20 website!"

if __name__ == "__main__":
    app.run(debug=True)



