import os
from flask import Flask, request, jsonify, make_response
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
sessionStorage = {}

@app.route('/post', methods=['POST'])
def main():
    try:
        # Логируем сырые входящие данные для отладки
        raw_data = request.get_data()
        logging.info(f'Raw request data: {raw_data}')

        if not request.json:
            logging.error('Empty JSON request received')
            return make_response(jsonify({
                'response': {
                    'text': 'Произошла ошибка: пустой запрос',
                    'end_session': False,
                    'buttons': get_suggests('default_user')
                },
                'version': '1.0',
                'session': {
                    'message_id': 0,
                    'session_id': 'empty_session',
                    'user_id': 'anonymous'
                }
            }), 200)

        logging.info(f'Parsed request: {request.json!r}')

        # Создаем базовую структуру ответа
        response = {
            'response': {
                'text': 'Привет! Купи слона!',
                'end_session': False,
                'buttons': []
            },
            'version': request.json.get('version', '1.0'),
            'session': request.json['session']
        }

        handle_dialog(request.json, response)

        logging.info(f'Response: {response!r}')
        
        # Явно указываем content-type
        resp = make_response(jsonify(response), 200
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
        return resp

    except Exception as e:
        logging.error(f'Error processing request: {str(e)}', exc_info=True)
        return make_response(jsonify({
            'response': {
                'text': 'Произошла внутренняя ошибка',
                'end_session': False,
                'buttons': get_suggests('error_user')
            },
            'version': '1.0',
            'session': {
                'message_id': 0,
                'session_id': 'error_session',
                'user_id': 'anonymous'
            }
        }), 200)

def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': ["Не хочу.", "Не буду.", "Отстань!"],
            'elephant_asked': False
        }
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Обработка числового ввода (как в вашем примере "1233")
    if 'nlu' in req['request'] and 'entities' in req['request']['nlu']:
        for entity in req['request']['nlu']['entities']:
            if entity['type'] == 'YANDEX.NUMBER':
                num = entity['value']
                res['response']['text'] = f'Цифра {num} - это интересно, но купи слона!'
                res['response']['buttons'] = get_suggests(user_id)
                return

    # Обработка текстового ввода
    user_input = req['request'].get('original_utterance', '').lower()
    
    if not user_input.strip():
        res['response']['text'] = 'Я вас не расслышала, повторите пожалуйста!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if any(word in user_input for word in ['ладно', 'куплю', 'покупаю', 'хорошо', 'согласен']):
        res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        res['response']['card'] = {
            'type': 'BigImage',
            'image_id': '997614/3a04d25b65407e9e8c24',
            'title': 'Вот ваш слон!',
            'description': 'Спасибо за покупку!'
        }
    else:
        res['response']['text'] = f"Все говорят '{user_input}', а ты купи слона!"
        res['response']['buttons'] = get_suggests(user_id)

def get_suggests(user_id):
    session = sessionStorage.get(user_id, {'suggests': ["Не хочу.", "Не буду.", "Отстань!"]})
    
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]
    
    # Добавляем кнопку с ссылкой
    suggests.append({
        "title": "Ладно",
        "url": "https://market.yandex.ru/search?text=слон",
        "hide": True
    })
    
    return suggests

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
