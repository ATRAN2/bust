from flask import Flask

app = Flask(__name__)

@app.route('/api')
def hello():
    return 'This is the api home.'

if __name__ == '__main__':
    app.run()

