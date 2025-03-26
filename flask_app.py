import os
from flask import Flask, request, jsonify, make_response
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
sessionStorage = {}

@app.route('/post', methods=['POST'])
def main():
    try:
        if not request.json:
            logging.error('Empty request received')
            return make_response(jsonify({
                'response': {
                    'text': 'Произошла ошибка',
                    'end_session': True
                },
                'version': '1.0'
            }), 200)

        logging.info(f'Request: {request.json!r}')

        response = {
            'session': request.json['session'],
            'version': request.json['version'],
            'response': {
                'end_session': False,
                'text': 'Привет! Купи слона!',  # Default response
                'buttons': []
            }
        }

        handle_dialog(request.json, response)

        logging.info(f'Response: {response!r}')
        return make_response(jsonify(response), 200)

    except Exception as e:
        logging.error(f'Error: {str(e)}')
        return make_response(jsonify({
            'response': {
                'text': 'Произошла ошибка',
                'end_session': True
            },
            'version': '1.0'
        }), 200)

def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': ["Не хочу.", "Не буду.", "Отстань!"]
        }
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Добавляем проверку на пустой original_utterance
    if 'original_utterance' not in req['request'] or not req['request']['original_utterance'].strip():
        res['response']['text'] = 'Не расслышала, повторите пожалуйста!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    user_input = req['request']['original_utterance'].lower()
    if user_input in ['ладно', 'куплю', 'покупаю', 'хорошо']:
        res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
    else:
        res['response']['text'] = f"Все говорят '{user_input}', а ты купи слона!"
        res['response']['buttons'] = get_suggests(user_id)

def get_suggests(user_id):
    session = sessionStorage.get(user_id, {'suggests': []})
    suggests = [{'title': s, 'hide': True} for s in session['suggests'][:2]]
    
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })
    
    return suggests

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
