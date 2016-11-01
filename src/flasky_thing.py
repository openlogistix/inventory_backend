from flask import Flask

def main():
    server = Flask('thingy')
    @server.route('/bentest')
    def home():
        return 'goodbye world'
    server.run('0.0.0.0',port=7000, debug=True)

main()
