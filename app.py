from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user = session.get("user_id")
    stocks = db.execute("SELECT stock, SUM(shares) FROM buy WHERE user= :user GROUP BY stock", user=user)
    balance = db.execute("SELECT cash FROM users WHERE id = :id", id=user)

    # Get actual price of stocks
    price = []
    for dic in stocks:
        price.append(lookup(dic['stock']))

    # Add actual name and price
    i = 0
    while i < len(stocks):
        for dic in price:
            stocks[i]["name"] = dic["name"]
            stocks[i]["price"] = dic["price"]
            i += 1
    stock = 0

    # Count total balance
    for dic in stocks:
        stock += (dic["price"] * dic["SUM(shares)"])
    total = stock + balance[0]["cash"]

    return render_template("index.html", stocks=stocks, balance=balance[0]["cash"], total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        try:
            int(shares)
        except ValueError:
            return apology("must be integer", 400)
        quoted = lookup(symbol)

        # Check valid input
        if quoted == None:
            return apology("invalid symbol", 400)
        elif int(shares) <= 0:
            return apology("amount must be greater than 0", 400)

        price = quoted["price"]
        user = session.get("user_id")
        cost = price * float(shares)

        # Check if user has enough amount of cash
        balance = db.execute("SELECT cash FROM users WHERE id = :id", id=user)
        if int(balance[0]["cash"]) < cost:
            return apology("sorry, you have not enough money", 400)
        else:
            new_balance = int(balance[0]["cash"]) - cost
            db.execute("INSERT INTO buy (user, stock, shares, price, cost) VALUES (?, ?, ?, ?, ?)",
                       (user, quoted["symbol"], shares, price, cost))
            db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash=new_balance, id=user)
        flash('Bought!')
        return render_template("buy.html")
    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    if request.method == "GET":
        username = request.values.get("username")

        if len(username) < 1:
            return jsonify(False)

        check_name = db.execute("SELECT * FROM users WHERE username = :username",
                                username=username)
        if len(check_name) == 1:
            return jsonify(False)
        else:
            return jsonify(True)


@app.route("/check_login", methods=["GET"])
def check_login():
    """Return true if username exists, else false, in JSON format"""

    if request.method == "GET":
        username = request.values.get("username")
        password = request.values.get("password")

        if len(username) < 1 or len(password) < 1:
            return jsonify(False)

        check_login = db.execute("SELECT * FROM users WHERE username = :username",
                                 username=username)

        # Ensure user is registered
        if len(check_login) == 1 and check_password_hash(check_login[0]["hash"], password):
            return jsonify(True)
        else:
            return jsonify(False)


@app.route("/check_buy_symbol", methods=["GET"])
def check_buy_symbol():
    """Return true if username exists, else false, in JSON format"""

    if request.method == "GET":
        symbol = request.values.get("symbol")
        quoted = lookup(symbol)

        if quoted is None:
            return jsonify(False)
        else:
            return jsonify(True)


@app.route("/check_buy_shares", methods=["GET"])
def check_buy_shares():
    """Return true if username exists, else false, in JSON format"""

    if request.method == "GET":
        symbol = request.values.get("symbol")
        quote = lookup(symbol)
        shares = request.values.get("shares")
        price = quote["price"]
        user = session.get("user_id")
        cost = price * float(shares)
        balance = db.execute("SELECT cash FROM users WHERE id = :id", id=user)

        if int(balance[0]["cash"]) < cost:
            return jsonify(False)
        else:
            return jsonify(True)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user = session.get("user_id")
    stocks = db.execute("SELECT stock, shares, price, date, time FROM buy WHERE user= :user", user=user)

    return render_template("history.html", stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        flash('You were successfully logged in')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        quoted = lookup(request.form.get("symbol"))

        # Check valid input
        if quoted is None:
            return apology("invalid symbol", 400)

        return render_template("quoted.html", quote=quoted)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirm was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensure password confirmed
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords are different", 400)

        # Query database for username
        check_name = db.execute("SELECT * FROM users WHERE username = :username",
                                username=request.form.get("username"))

        # Ensure user hasn't been already registered
        if check_name:
            return apology("username already exists. Please, choose another username")

        # Add username to db
        else:

            # Hash password
            password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

            username = request.form.get("username")
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, password))

        flash('Registered!')

        return redirect('/')

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user = session.get("user_id")

    # Get available stocks
    symbol_db = db.execute("SELECT stock FROM buy WHERE user= :user GROUP BY stock", user=user)

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Ensure valid input
        try:
            int(shares)
        except ValueError:
            return apology("must be integer", 400)

        # Check correct input of shares
        if int(shares) <= 0:
            return apology("amount must be greater than 0", 400)

        # Check if user has enough stocks
        shares_db = db.execute("SELECT stock, SUM(shares) FROM buy WHERE user= :user GROUP BY stock", user=user)
        for dic in shares_db:
            if dic["stock"] == symbol:
                if int(shares) > int(dic["SUM(shares)"]):
                    return apology("You don't have so much stocks", 400)

        # Sell stocks
        quoted = lookup(symbol)
        price = quoted["price"]
        cost = price * float(shares)
        balance = db.execute("SELECT cash FROM users WHERE id = :id", id=user)
        new_balance = balance[0]["cash"] + cost
        shares_neg = int(shares) * (-1)
        db.execute("INSERT INTO buy (user, stock, shares, price, cost) VALUES (?, ?, ?, ?, ?)",
                   (user, symbol, shares_neg, price, cost))
        db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash=new_balance, id=user)
        flash('Sold!')
        return render_template("sell.html", symbol_db=symbol_db)
    else:
        return render_template("sell.html", symbol_db=symbol_db)


@app.route("/charge", methods=["GET", "POST"])
@login_required
def charge():
    """Show history of transactions"""
    if request.method == "POST":
        user = session.get("user_id")
        charge = request.form.get("charge")

        # Ensure valid input
        try:
            int(charge)
        except ValueError:
            return apology("must be integer", 400)
        if int(charge) > 0:
            cash = db.execute("SELECT cash FROM users WHERE id = :id", id=user)
            new_balance = int(charge) + cash[0]["cash"]
            db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash=new_balance, id=user)
            flash('Done!')
            return render_template("charge.html")
        else:
            return apology("amount must be greater than 0", 400)
    else:
        return render_template("charge.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


