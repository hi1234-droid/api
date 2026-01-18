from flask import Flask, jsonify, request
import requests
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///passes.db'  # Database to track passes
db = SQLAlchemy(app)

# Database model to store passes for each game
class GamePass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(50), nullable=False)
    pass_id = db.Column(db.Integer, nullable=False)
    pass_name = db.Column(db.String(200), nullable=False)
    pass_price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<GamePass {self.pass_name} ({self.pass_id})>'

# Create tables
with app.app_context():
    db.create_all()

@app.route('/games/<int:user_id>', methods=['GET'])
def get_user_games(user_id):
    # Get the list of games the user has created from Roblox API
    url = f"https://apis.roblox.com/developer/v1/users/{user_id}/games"
    response = requests.get(url)

    if response.status_code == 200:
        games = response.json()["data"]
        games_data = []

        for game in games:
            game_data = {
                "game_id": game["id"],
                "game_name": game["name"],
                "game_passes": get_game_passes_for_game(game["id"])
            }
            games_data.append(game_data)

        return jsonify(games_data), 200
    else:
        return jsonify({"error": "Unable to fetch user games"}), 500

def get_game_passes_for_game(game_id):
    # Query database to get game passes for this specific game
    passes = GamePass.query.filter_by(game_id=game_id).all()
    return [
        {"pass_id": pass_.pass_id, "pass_name": pass_.pass_name, "pass_price": pass_.pass_price}
        for pass_ in passes
    ]

@app.route('/add_game_pass', methods=['POST'])
def add_game_pass():
    # Manually add game passes (for now, assuming you track pass data)
    data = request.get_json()
    game_pass = GamePass(
        game_id=data["game_id"],
        pass_id=data["pass_id"],
        pass_name=data["pass_name"],
        pass_price=data["pass_price"]
    )
    db.session.add(game_pass)
    db.session.commit()

    return jsonify({"message": "Game pass added successfully!"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # Make the server public
