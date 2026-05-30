from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

print("Я ТОТ САМЫЙ СЕРВЕР")

def get_db():
    conn = sqlite3.connect("products.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db()
    cursor = conn.cursor()

    weight = ""
    height = ""
    age = ""
    gender = ""
    activity = "1"

    # Таблица дневника (создаётся автоматически)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        calories INTEGER
    )
    """)

    if request.method == "POST":
        weight = request.form.get("weight", "")
        height = request.form.get("height", "")
        age = request.form.get("age", "")
        gender = request.form.get("gender", "")
        activity = request.form.get('activity', "1")

    # ДОБАВЛЕНИЕ В ДНЕВНИК
    if "add_to_diary" in request.form:
        name = request.form["product_name"]
        calories = int(request.form["calories"])

        cursor.execute(
            "INSERT INTO diary (product_name, calories) VALUES (?, ?)",
            (name, calories)
        )
        conn.commit()
        return redirect(url_for("index"))
        # ДОБАВЛЕНИЕ В ДНЕВНИК
        # УДАЛЕНИЕ ИЗ ДНЕВНИКА
    elif "delete" in request.form:
        diary_id = request.form["delete"]

        cursor.execute(
            "DELETE FROM diary WHERE id = ?",
            (diary_id,)
        )
        conn.commit()
        return redirect(url_for("index"))
            
    # Получаем продукты
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    # Получаем дневник
    cursor.execute("SELECT * FROM diary")
    diary = cursor.fetchall()

    total_calories = sum([row["calories"] for row in diary])

    search_results = []
    calories_result = None

    # ПОИСК
    if "search" in request.form:
        name = request.form["search"].lower()
        cursor.execute(
            "SELECT * FROM products WHERE LOWER(name) LIKE ?",
            ('%' + name + '%',)
        )
        search_results = cursor.fetchall()

    # РАСЧЁТ КАЛОРИЙ
    if "weight" in request.form:
        gender = request.form["gender"]
        weight = float(request.form["weight"])
        height = float(request.form["height"])
        age = int(request.form["age"])
        activity = request.form["activity"]

        if gender == "м":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        factors = {
            "1": 1.2,
            "2": 1.375,
            "3": 1.55,
            "4": 1.725
        }

        calories_result = int(bmr * factors.get(activity, 1.2))

    conn.close()

    return render_template(
        "index.html",
        products=products,
        results=search_results,
        calories=calories_result,
        diary=diary,
        total=total_calories,
        weight=weight,
        height=height,
        age=age,
        gender=gender,
        activity=activity
    )

if __name__ == "__main__":
    app.run(debug=True)