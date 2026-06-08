import json
import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), 'foods.json')
with open(DATA_PATH, encoding='utf-8') as f:
    FOODS = json.load(f)

NUTRIENTS = [
    ('energy_kcal',   'エネルギー',     'kcal'),
    ('protein_g',     'たんぱく質',      'g'),
    ('fat_g',         '脂質',           'g'),
    ('carb_g',        '炭水化物',        'g'),
    ('fiber_g',       '食物繊維',        'g'),
    ('salt_g',        '食塩相当量',      'g'),
    ('calcium_mg',    'カルシウム',      'mg'),
    ('iron_mg',       '鉄',             'mg'),
    ('vitamin_a_ug',  'ビタミンA',       'μg'),
    ('vitamin_b1_mg', 'ビタミンB1',      'mg'),
    ('vitamin_b2_mg', 'ビタミンB2',      'mg'),
    ('vitamin_c_mg',  'ビタミンC',       'mg'),
    ('vitamin_d_ug',  'ビタミンD',       'μg'),
]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/foods')
def search_foods():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    results = [
        {'id': f['id'], 'name': f['name'], 'category': f['category']}
        for f in FOODS
        if q in f['name'] or q in f['category']
    ]
    return jsonify(results[:30])


@app.route('/api/food/<int:food_id>')
def get_food(food_id):
    food = next((f for f in FOODS if f['id'] == food_id), None)
    if not food:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(food)


@app.route('/api/calculate', methods=['POST'])
def calculate():
    items = request.json.get('items', [])

    zero = {k: 0.0 for k, _, _ in NUTRIENTS}
    detailed = []

    for item in items:
        food_id = int(item.get('food_id', 0))
        amount = float(item.get('amount', 0))
        food = next((f for f in FOODS if f['id'] == food_id), None)
        if not food or amount <= 0:
            continue
        ratio = amount / 100.0
        nutrition = {k: round(food['nutrition'].get(k, 0) * ratio, 1) for k, _, _ in NUTRIENTS}
        for k in zero:
            zero[k] += nutrition[k]
        detailed.append({
            'food_id': food_id,
            'name': food['name'],
            'amount': amount,
            'nutrition': nutrition,
        })

    totals = {k: round(v, 1) for k, v in zero.items()}
    return jsonify({'totals': totals, 'items': detailed})


@app.route('/api/nutrients')
def get_nutrients():
    return jsonify([{'key': k, 'label': l, 'unit': u} for k, l, u in NUTRIENTS])


if __name__ == '__main__':
    app.run(debug=True, port=5000)
