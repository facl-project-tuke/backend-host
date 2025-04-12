from flask import Flask, render_template, jsonify, request
import pyodbc
import os
from dotenv import load_dotenv
from requests import post, get
import base64

app = Flask(__name__)

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

DB_SERVER = 'zctserver.database.windows.net'
DB_NAME = 'ZCT'
DB_USER = 'superadmin'
DB_PASSWORD = 'ZCT12345ZCT_'

conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD};"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)

def get_spotify_token():
    auth_bytes = f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    result = post(url, headers=headers, data={"grant_type": "client_credentials"})
    return result.json().get("access_token") if result.ok else None

def get_track_preview(spotify_id, token):
    url = f"https://api.spotify.com/v1/tracks/{spotify_id}"
    headers = {"Authorization": f"Bearer {token}"}
    result = get(url, headers=headers)
    data = result.json()
    return data.get("preview_url") if result.ok else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend_tracks():
    data = request.get_json()
    emotion = data.get('emotion')  # получаем emotion из JSON

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT TOP 10 track, artist, spotify_id 
        FROM muse 
        WHERE mapped_emotions = ?
        ORDER BY NEWID()
        """,
        f"['{emotion}']"
    )

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    token = get_spotify_token()

    tracks = [{
        'track': row.track,
        'artist': row.artist,
        'spotify_id': row.spotify_id,
        'preview_url': get_track_preview(row.spotify_id, token)
    } for row in results]

    print("Recommended tracks:", tracks)
    return jsonify({ "tracks": tracks })


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
