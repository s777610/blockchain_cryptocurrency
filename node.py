
from flask import Flask
from wallet import Wallet

# only clients running on same server can access this server
# only web pages html returned by a server can again send requests to it
from flask_cors import CORS  # Cross-Origin Resource Sharing


app = Flask(__name__)
wallet = Wallet()
CORS(app)


# pass path and type of request
@app.route('/', methods=['GET'])
def get_ui():
    return 'This works!'


if __name__ == '__main__':
    # run() take 2 args, IP and port
    app.run(host='0.0.0.0', port=5000)


