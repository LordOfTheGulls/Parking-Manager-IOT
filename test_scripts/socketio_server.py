import socketio
import eventlet

sio = socketio.Server()
app = socketio.WSGIApp(sio)
port = 8000

class SocketIOServer() :
    
    def __init__(self) -> None:
        pass
    
    def setup(self): 
        eventlet.wsgi.server(eventlet.listen(('', port)), app)
        print('SocketIO server is running at port %s' % port)

    @sio.event
    def connect(self, sid, environ):
        print('connect', sid)
        sio.emit('ParkingLots', {})
        
    @sio.event
    def message(sid, data):
        print(data)

    @sio.event
    def disconnect(sid):
        print(sid, 'disconnected')
        


socketIO = SocketIOServer()
socketIO.setup()