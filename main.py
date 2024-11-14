import eventlet
eventlet.monkey_patch()

from website import Server, db, socketio


app = Server()

if __name__ == '__main__':
    with app.app_context():
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)

