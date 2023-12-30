from flask import Blueprint, render_template, jsonify, request,flash,url_for,redirect,session, abort
from flask_bcrypt import Bcrypt
from bson import ObjectId
from datetime import datetime, timedelta
import requests
import math
from db import app, mongo

main_bp = Blueprint('main', __name__)

@main_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    results = filter_tickets(query)
    return jsonify(results)


def filter_tickets(query):
    filtered_tickets = [
        {
            'route': ticket['route'],
            'track_number': ticket['track_number'],
            'stops': [stop['name'] for stop in ticket['stops']]
        }
        for ticket in mongo.db.tickets
        if query.lower() in ticket['route'].lower() or any(query.lower() in stop['name'].lower() for stop in ticket['stops'])
    ]

    return filtered_tickets
def is_logged_in():
    return 'user_id' in session

@main_bp.route('/flight_list', methods=['GET'])
def flight_list():
    if not is_logged_in():
        return redirect(
            url_for('admin.login_admin'))  # Перенаправление на страницу входа, если пользователь не авторизован

    print("Attempting to retrieve ticket data")
    ticket_data = mongo.db.tickets.find({}, {'_id': 0, 'route': 1, 'track_number': 1})
    tickets_list = list(ticket_data)
    print(f"Tickets list: {tickets_list}")

    return render_template('test.html', tickets=tickets_list)


# ПРОВЕРКА НА ПРИСУТСТВИЕ ИНТЕРНЕТА
@main_bp.route('/check_internet_connection')
def check_internet_connection():
    try:
        response = requests.get("https://www.google.com")

        if response.status_code == 200:
            return jsonify({"message": "Интернет-соединение присутствует."}), 200
        else:
            return jsonify({"message": "Ошибка: Нет доступа к внешнему ресурсу."}), 500

    except requests.ConnectionError:
        return jsonify({"message": "Ошибка: Отсутствует интернет-соединение."}), 500


# ПОИСК билета
@main_bp.route('/get_ticket/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    try:
        print(f"Attempting to find ticket with id: {ticket_id}")
        ticket = mongo.db.tickets.find_one({'_id': ObjectId(ticket_id)})

        if ticket:
            ticket['_id'] = str(ticket['_id'])

            for stop in ticket.get('stops', []):
                if '_id' in stop:
                    stop['_id'] = str(stop['_id'])

            print(f"Found ticket: {ticket}")
            return jsonify({'ticket': ticket}), 200
        else:
            print("Ticket not found")
            return jsonify({'error': 'Билет не найден'}), 404
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# УДАЛЕНИЕ билета
@main_bp.route('/delete_ticket/<ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    try:
        print(f"Attempting to delete ticket with id: {ticket_id}")
        result = mongo.db.tickets.delete_one({'_id': ObjectId(ticket_id)})

        if result.deleted_count > 0:
            print("Ticket deleted successfully")
            return jsonify({'message': 'Билет успешно удален'}), 200
        else:
            print("Ticket not found for deletion")
            return jsonify({'error': 'Билет не найден для удаления'}), 404
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ДОБАВЛЕНИЕ билета
@main_bp.route('/add_ticket', methods=['POST'])
def add_ticket():
    data = request.json

    if 'route' not in data or 'track_number' not in data or 'stops' not in data:
        return jsonify({'error': 'Неверные данные билета'}), 400

    route = data['route']
    track_number = data['track_number']
    stops = data['stops']

    ticket_data = {
        'route': route,
        'track_number': track_number,
        'stops': stops
    }

    mongo.db.tickets.insert_one(ticket_data)
    return jsonify({'message': 'Билет успешно добавлен в базу данных'}), 200


#ПОЛЕ для админов
admin_bp = Blueprint('admin', __name__)
bcrypt = Bcrypt()

#РЕГИСТРАЦИЯ админа
@admin_bp.route('/register_admin', methods=['POST'])
def register_admin():
    data = request.json

    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Необходимо указать имя пользователя и пароль'}), 400

    username = data['username']
    password = data['password']

    existing_user = mongo.db.admins.find_one({'username': username})

    if existing_user:
        return jsonify({'error': 'Пользователь с таким именем уже существует'}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    user_data = {
        'username': username,
        'password': hashed_password
    }

    mongo.db.admins.insert_one(user_data)
    return jsonify({'message': 'Пользователь успешно зарегистрирован'}), 201

#АВТОРИЗАЦИЯ админа
@admin_bp.route('/login_admin', methods=['POST'])
def login_admin():
    data = request.json

    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Необходимо указать имя пользователя и пароль'}), 400

    username = data['username']
    password = data['password']

    user = mongo.db.admins.find_one({'username': username})

    if user and bcrypt.check_password_hash(user['password'], password):
        session['user_id'] = str(user['_id'])  # Установка сеанса
        # return jsonify({'message': 'Авторизация пользователя успешна'}), 200
        return redirect(url_for('main.flight_list'))
    else:
        return jsonify({'error': 'Неверное имя пользователя или пароль'}), 401

@admin_bp.route('/logout_admin', methods=['POST'])
def logout_admin():
    session.pop('user_id', None)
    return redirect(url_for('admin.login_admin'))

#УДАЛЕНИЕ админа
@admin_bp.route('/delete_admin/<username>', methods=['DELETE'])
def delete_admin(username):
    try:
        print(f"Attempting to delete admin with username: {username}")
        result = mongo.db.admins.delete_one({'username': username})

        if result.deleted_count > 0:
            return jsonify({'message': 'Админ успешно удален'}), 200
        else:
            return jsonify({'error': 'Админ не найден для удаления'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500




ticket = [
    {
        "_id": "65579d58aa2c52ee2fa8d8e6",
        "route": "Алматы 2 → Нурлы Жол'",
        "track_number": '003Ц',
        "train_speed_kmh": 200,
        "stops": [
            {"name": 'Алматы 2', "departure_time": '13:28', "latitude": 43.273675, "longitude": 76.939167},
            {"name": 'Отар', "arrival_time": '15:33', "stop_duration": '00:15', "departure_time": '15:48', "latitude": 49.8019, "longitude": 73.1021},
            {"name": 'Шу', "arrival_time": '17:40', "stop_duration": '00:30', "departure_time": '18:10', "latitude": 53.147914, "longitude": 69.350533},
            {"name": 'Сары Шаган', "arrival_time": '21:25', "stop_duration": '00:17', "departure_time": '21:42', "latitude": 46.119231, "longitude": 73.605393},
            {"name": 'Акадыр', "arrival_time": '00:08', "stop_duration": '00:10', "departure_time": '00:18', "latitude": 46.119231, "longitude": 73.605393},
            {"name": 'Караганды Пасс', "arrival_time": '02:18', "stop_duration": '00:12', "departure_time": '02:30', "latitude": 46.119231, "longitude": 73.605393},
            {"name": 'Нур-Султан-Нурлы Жол', "arrival_time": '05:20', "latitude": 43.534929, "longitude": 75.212983}
        ]
    }
]

def calculate_total_time(stops, train_speed_kmh):
    total_time = timedelta()

    for i, stop in enumerate(stops):
        if i == 0:  # Первый город
            departure_time = datetime.strptime(stop["departure_time"], "%H:%M")
            total_time += timedelta(hours=departure_time.hour, minutes=departure_time.minute)
        elif i == len(stops) - 1:  # Последний город
            arrival_time = datetime.strptime(stop["arrival_time"], "%H:%M")
            total_time += timedelta(hours=arrival_time.hour, minutes=arrival_time.minute)
        else:
            stop_duration = datetime.strptime(stop["stop_duration"], "%H:%M")
            total_time += timedelta(hours=stop_duration.hour, minutes=stop_duration.minute)

            # Рассчитываем время в пути между текущей и следующей остановкой
            current_stop = stops[i]
            next_stop = stops[i + 1]
            travel_time_hours = calculate_travel_time(train_speed_kmh, current_stop, next_stop)
            total_time += timedelta(hours=travel_time_hours)

    return total_time

def calculate_travel_time(train_speed_kmh, current_stop, next_stop):
    distance_km = calculate_distance(0, 0, 0, 0)  # Замените 0, 0, 0, 0 на координаты текущей и следующей остановки
    travel_time_hours = distance_km / train_speed_kmh
    return travel_time_hours

def calculate_distance(lat1, lon1, lat2, lon2):
    # Здесь вы можете использовать более точные формулы для расчета расстояния
    # Например, формула гаверсинуса, которая используется в предыдущем коде
    R = 6371  # Радиус Земли в км
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = math.radians(lat1), math.radians(lon1), math.radians(lat2), math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_km = R * c
    return distance_km


@main_bp.route('/get_time')
def get_total_time():
    total_time = calculate_total_time(ticket[0]["stops"], ticket[0]["train_speed_kmh"])
    hours, remainder = divmod(total_time.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return jsonify({"total_time": f"{hours} ч {minutes} мин"})

