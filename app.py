from flask import Flask,render_template
from routes import main_bp,admin_bp
from flask_socketio import SocketIO,emit
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
# app.register_blueprint(main_bp)

@admin_bp.route('/login_admin', methods=['GET'])
def show_login():
    return render_template('login.html')


app.register_blueprint(main_bp, url_prefix='/main')
app.register_blueprint(admin_bp, url_prefix='/admin')
socketio = SocketIO(app, async_mode='threading')


@socketio.on('connect', namespace='/home')
def handle_connect():
    print('Client connected')

@socketio.on('cancel_flight')
def cancel_flight(flight_number):
    message = f'Рейс {flight_number} отменен!'
    socketio.emit('flight_canceled', message)
    print('Canceled flight, emitting ticket list')  # добавьте эту строку для отладки

@socketio.on('train_delay')
def train_delay(data):
    train_number = data['train_number']
    delay_minutes = data['delay_minutes']
    message = f'Поезд с номером {train_number} опаздывает на {delay_minutes} минут'
    socketio.emit('delay_message', message)



if __name__ == '__main__':
    socketio.run(app, debug=True)
    # app.run(debug=True, port=27017)