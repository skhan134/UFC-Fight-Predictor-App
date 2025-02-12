from collections import defaultdict
import pandas as pd
import joblib
import numpy as np
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow frontend to call the API

# Load ML model
model = joblib.load('models/UFC_Model.pkl')  # Adjust path to model if needed

# Load and clean fighter dataset (now located in the 'data/' folder)
fighters_df = pd.read_csv('data/fighter_stats_cleaned.csv').drop_duplicates(subset="name", keep="first")

# Convert to dictionary lookup for fast access
fighters_dict = fighters_df.set_index("name").to_dict(orient="index")

# Optimized function for fight prediction
def predict_fight_outcome(fighter1_name, fighter2_name): 
    if fighter1_name not in fighters_dict or fighter2_name not in fighters_dict:
        return {"error": "One or both fighters not found."}

    fighter1 = fighters_dict[fighter1_name]
    fighter2 = fighters_dict[fighter2_name]

    if fighter1["division"] != fighter2["division"]:
        return {"error": "Fighters must be in the same weight class."}

    feature_cols = ["Striking_Score", "Grappling_Score", "Experience_Score", "Physicality_Score", "age"]
    fighter1_features = np.array([fighter1[col] for col in feature_cols], dtype=float)
    fighter2_features = np.array([fighter2[col] for col in feature_cols], dtype=float)

    diff_features = np.abs(fighter1_features - fighter2_features)

    # Concatenate features correctly
    input_features = np.hstack([fighter1_features, fighter2_features, diff_features]).reshape(1, -1)
    print("Final input shape:", input_features.shape)
    prediction = model.predict(input_features)

    return fighter1_name if prediction[0] == 1 else fighter2_name

# API Routes
@app.route('/api/divisions', methods=['GET'])
def get_divisions():
    return jsonify(sorted(fighters_df['division'].unique().tolist()))

# Create an API route to get fighters by division
@app.route('/api/fighters/<division>', methods=['GET'])
def get_fighters_by_division(division):
    division_fighters = fighters_df[fighters_df['division'] == division]['name'].tolist()
    return jsonify(division_fighters)

@app.route('/api/fighters', methods=['GET'])
def get_fighters():
    division = request.args.get('division')
    if not division:
        return jsonify({"error": "Division parameter is required."}), 400

    fighters_in_division = fighters_df[fighters_df['division'] == division]['name'].tolist()
    return jsonify(fighters_in_division)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    print(request.json)
    fighter1 = data.get("fighter1")
    fighter2 = data.get("fighter2")

    if not fighter1 or not fighter2:
        return jsonify({"error": "Both fighters must be selected."}), 400

    result = predict_fight_outcome(fighter1, fighter2)
    return jsonify(result)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)