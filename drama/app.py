from flask import Flask, render_template, request, redirect, session, url_for
import random

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DRAMA DATA ----------------
dramas = [
    {"name": "Crash Landing On You", "genre": "Romance", "image": "crash.jpg", "description": "A South Korean heiress accidentally lands in North Korea and meets a soldier.", "ratings": []},
    {"name": "Vincenzo", "genre": "Action", "image": "vincenzo.jpg", "description": "A mafia lawyer returns to Korea and fights against corruption.", "ratings": []},
    {"name": "Kingdom", "genre": "Thriller", "image": "kingdom.jpg", "description": "A crown prince fights a mysterious zombie outbreak.", "ratings": []},
    {"name": "Itaewon Class", "genre": "Romance", "image": "itaewon.jpg", "description": "A young man opens a bar to take revenge on a powerful company.", "ratings": []},
    {"name": "The Glory", "genre": "Thriller", "image": "the_glory.jpg", "description": "A woman plans long-term revenge against her bullies.", "ratings": []},
    {"name": "Twinkling Watermelon", "genre": "Romance", "image": "watermelon.jpg", "description": "A boy travels back in time and meets his parents.", "ratings": []},
    {"name": "True Beauty", "genre": "Romance", "image": "true_beauty.jpg", "description": "A girl hides her insecurities behind makeup.", "ratings": []},
    {"name": "All Of Us Are Dead", "genre": "Thriller", "image": "dead.jpg", "description": "Students struggle to survive a zombie outbreak in school.", "ratings": []},
    {"name": "Goblin", "genre": "Fantasy", "image": "goblin.jpg", "description": "An immortal goblin searches for his bride.", "ratings": []},
    {"name": "Hotel Del Luna", "genre": "Fantasy", "image": "luna.jpg", "description": "A hotel for ghosts run by a mysterious woman.", "ratings": []},
    {"name": "Hospital Playlist", "genre": "Medical", "image": "playlist.jpg", "description": "Doctors balance work, friendship, and life.", "ratings": []},
    {"name": "Dr Romantic", "genre": "Medical", "image": "romantic.jpg", "description": "A genius doctor teaches young surgeons.", "ratings": []},
    {"name": "Mr Queen", "genre": "Comedy", "image": "queen.jpg", "description": "A chef’s soul enters a queen’s body.", "ratings": []},
    {"name": "Strong Woman Do Bong Soon", "genre": "Comedy", "image": "strong.jpg", "description": "A girl with super strength fights crime.", "ratings": []}
]

# ---------------- HELPER FUNCTION ----------------
def get_dramas_by_genre(genre):
    return [d for d in dramas if d["genre"].lower() == genre.lower()]

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with open('users.txt', 'a') as f:
            f.write(f"{username},{password}\n")

        session['user'] = username
        return redirect('/')

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            with open('users.txt', 'r') as f:
                users = f.readlines()
        except:
            users = []

        for user in users:
            stored_user, stored_pass = user.strip().split(',')
            if username == stored_user and password == stored_pass:
                session['user'] = username
                return redirect(url_for('home'))

        return render_template('login.html', error="Invalid Credentials ❌")

    return render_template('login.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# ---------------- HOME ----------------
@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template('home.html', user=session['user'])

# ---------------- MOOD RECOMMENDATION ----------------
def get_recommendations_by_mood(mood):
    mood_map = {
        "happy": ["comedy"],
        "sad": ["romance"],
        "romantic": ["romance"],
        "stressed": ["comedy"]
    }

    genres = mood_map.get(mood, [])
    return [d for d in dramas if d["genre"].lower() in genres]

@app.route('/recommend', methods=['POST'])
def recommend():
    mood = request.form['mood']
    results = get_recommendations_by_mood(mood)
    return render_template('recommendations.html', dramas=results)

# ---------------- GENRE RECOMMENDATION ----------------
@app.route('/recommendations')
def recommendations():
    genre = request.args.get('genre')
    if not genre:
        return "No genre selected"
    results = get_dramas_by_genre(genre)
    return render_template('recommendations.html', dramas=results, genre=genre)

# ---------------- SURPRISE ----------------
@app.route('/surprise')
def surprise():
    drama = random.choice(dramas)
    return render_template('drama_detail.html', drama=drama)

# ---------------- SEARCH PAGE ----------------
@app.route('/search')
def search_page():
    return render_template('search.html')

# ---------------- SEARCH RESULT ----------------
@app.route('/search-results')
def search_results():
    query = request.args.get('q', '').lower()
    results = [d for d in dramas if query in d["name"].lower()]
    return render_template('recommendations.html', dramas=results)

# ---------------- CHATBOT PAGE ----------------
@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')

# ---------------- CHATBOT RESPONSE ----------------
@app.route('/chat', methods=['POST'])
def chat():
    msg = request.form['message'].lower()

    if "romantic" in msg:
        return "Try a romantic drama 💖"
    elif "sad" in msg:
        return "Watch a melodrama 😢"
    elif "funny" in msg or "happy" in msg:
        return "Go for a comedy 😄"
    else:
        return "Tell me your mood!"

# ---------------- DRAMA DETAIL ----------------
@app.route('/drama/<name>')
def drama_detail(name):
    selected = next((d for d in dramas if d["name"] == name), None)
    return render_template('drama_detail.html', drama=selected)

# ---------------- WATCHLIST ----------------
@app.route('/add_to_watchlist/<name>')
def add_to_watchlist(name):
    watchlist = session.get('watchlist', [])
    if name not in watchlist:
        watchlist.append(name)
    session['watchlist'] = watchlist
    return redirect('/watchlist')

@app.route('/watchlist')
def watchlist():
    selected_names = session.get('watchlist', [])
    selected = [d for d in dramas if d["name"] in selected_names]
    return render_template('watchlist.html', dramas=selected)

@app.route('/remove_from_watchlist/<name>')
def remove_from_watchlist(name):
    watchlist = session.get('watchlist', [])
    if name in watchlist:
        watchlist.remove(name)
    session['watchlist'] = watchlist
    return redirect('/watchlist')

# ---------------- RATING ----------------
@app.route('/rate/<name>', methods=['POST'])
def rate(name):
    rating = int(request.form['rating'])
    for d in dramas:
        if d["name"] == name:
            d["ratings"].append(rating)
    return redirect('/drama/' + name)

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)