from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
from flask.json import JSONEncoder
#import public_html.db_secrets as s
import db_secrets as s

app = Flask(__name__) 
app.config['MYSQL_HOST'] = s.MYSQL_HOST
app.config['MYSQL_USER'] = s.MYSQL_USER
app.config['MYSQL_PASSWORD'] = s.MYSQL_PASSWORD
app.config['MYSQL_DB'] = s.MYSQL_DB
app.config['MYSQL_PORT'] = s.MYSQL_PORT
app.config['MYSQL_CURSORCLASS'] = s.MYSQL_CURSORCLASS
app.config['SECRET_KEY'] = s.SECRET_KEY
mysql = MySQL(app)

larp_number = 1
XP = 0
HP = 0
MP = 0

#Check to see if email has @ and . in it
def validate_email(email):
    return "@" in email and "." in email

#Returns player information via user email lookup
def get_player_data(email):
    cursor = mysql.connection.cursor()
    query = """SELECT
                p.idplayers,
                p.first_name,
                p.last_name,
                p.primary_email,
                p.pronouns,
                p.rewards,
                p.legal_release,
                p.signed_name,
                p.date_signed,
                p.emergency_contact_name,
                p.emergency_contact_phone
            FROM
                players p
            INNER JOIN
                users u
            ON
                p.user_id=u.idusers
            WHERE
                u.email=%s"""
    queryVars = (email,)
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    results = cursor.fetchall()
    
    return results

#Returns character data from idplayers
def get_character_data(p_id):
    cursor = mysql.connection.cursor()
    query = """SELECT
                c.idcharacters,
                c.name,
                c.xp,
                c.hp,
                c.mp,
                c.bio,
                c.picture,
                c.last_saved,
                c.playground_flag,
                s.species_name,
                s.description,
                l.name AS class_name,
                l.description
            FROM
                players p
            INNER JOIN characters c ON p.idplayers=c.player_id
            LEFT JOIN species s ON c.species_id=s.idspecies
            LEFT JOIN classes l ON c.class_id=l.idclasses
            WHERE
                p.idplayers=%s"""
    queryVars = (p_id,)
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    results = cursor.fetchall()
    
    return results

#Returns character data from idcharacters
def get_character(char_id):
    cursor = mysql.connection.cursor()
    query = """SELECT
                c.idcharacters,
                c.name,
                c.xp,
                c.hp,
                c.mp,
                c.bio,
                c.picture,
                c.last_saved,
                c.playground_flag,
                s.species_name,
                s.description,
                l.name AS class_name,
                l.description
            FROM
                characters c
            LEFT JOIN species s ON c.species_id=s.idspecies
            LEFT JOIN classes l ON c.class_id=l.idclasses
            WHERE
                c.idcharacters=%s"""
    queryVars = (char_id,)
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    results = cursor.fetchall()
    
    return results

#Calculates current HP
def get_hp(xp):
    return 5*int(xp) + 2;
    
#Calculates current MP
def get_mp(xp):
    return 10*int(xp) + 4;

#Returns the hashed password for the given user email
def get_password(email):
    cursor = mysql.connection.cursor()
    query = "SELECT password FROM users WHERE email=%s"
    queryVars = (email,)
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    results = cursor.fetchall()
    
    return results

#Checks timestamp on legal release against 1 year, and updates database if LR is older than 1 year
def update_legal_release(email):
    results=get_player_data(email)
    
    player_id = results[0]['idplayers']    
    date_signed = results[0]['date_signed']
    
    if date_signed is not None:
        #Check to see if legal release was signed too long ago
        time_since_signed = datetime.now().date() - date_signed
        
        if time_since_signed.days > 365:
            cursor = mysql.connection.cursor()
            query = "UPDATE players SET legal_release=%s WHERE idplayers=%s"
            queryVars = (0,player_id,)
            cursor.execute(query, queryVars)
            mysql.connection.commit()
    else:
        cursor = mysql.connection.cursor()
        query = "UPDATE players SET legal_release=%s WHERE idplayers=%s"
        queryVars = (0,player_id,)
        cursor.execute(query, queryVars)
        mysql.connection.commit()

#Validates given number as phone number
def validate_phone(phone):
    phone = phone.replace('(', '')
    phone = phone.replace(')', '')
    phone = phone.replace('.', '')
    phone = phone.replace('-', '')
    phone = phone.replace(' ', '')
    
    if len(phone) != 10:
        phone = None
        
    try:
        phone = int(phone)
    except:
        phone = None
    
    return phone

#Verifies session is active
def verify_session():
    try:
        session['users']
        return True
    except:
        return False

#Returns all species
def get_species():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM species;"
    queryVars = ()
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    results = cursor.fetchall()
    
    return results

#Returns all classes
def get_classes():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM classes;"
    queryVars = ()
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    results = cursor.fetchall()
    
    return results


#start of pages
#Index page
@app.route('/')
def index():
    return render_template('index.html')

#About page
@app.route('/about')
def about():
    return render_template('about.html')

#Policies Page
@app.route('/policies')
def policies():
    return render_template('policies.html')

#Rules Page
@app.route('/rules')
def rules():
    return render_template('rules.html')

#Donations Page
@app.route('/donations')
def donations():
    return render_template('donations.html')

#Contact Page
@app.route('/contact')
def contact():
    return render_template('contact.html')

#Index for the database portion: if logged in, displays message, otherwise prompts to log in/create user
@app.route('/db_index')
def db_index():
    email=session.get('users')
    
    if email != None:
        results=get_player_data(email)
    else:
        results = []
    
    return render_template('db_index.html', data=results)

#Signs user up for an account on the database
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('db_signup.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        password_reenter = request.form.get('password_two')
    
        if len(password) < 8:
            error = "Password not secure. Please try again."
            return render_template('db_signup.html', error=error)
        else:
            if password == password_reenter:
                results = get_password(email)
                
                if (len(results) == 0):
                    if (validate_email(email)):
                        securedPassword = generate_password_hash(password)
                        cursor = mysql.connection.cursor()
                        query = 'INSERT INTO users(email, password) VALUES (%s, %s)'
                        queryVars = (email,securedPassword,)
                        cursor.execute(query, queryVars)
                        mysql.connection.commit()
                        
                        query = "SELECT idusers FROM users WHERE email=%s"
                        queryVars = (email,)
                        cursor.execute(query, queryVars)
                        mysql.connection.commit()
                        results = cursor.fetchall()
                        
                        query = 'INSERT INTO players(first_name, last_name, primary_email,pronouns, user_id) VALUES (%s, %s, %s, %s, %s)'
                        queryVars = ("Unknown", "Unknown", email, "Unknown", results[0]['idusers'])
                        cursor.execute(query, queryVars)
                        mysql.connection.commit()
                        
                        results=get_player_data(email)
                        return redirect(url_for('db_index',data=results))
                    else:
                        return render_template('db_signup.html', error="Invalid email address")
                else:
                    return render_template('db_signup.html', error="That email already exists.")
            else:
                return render_template('db_signup.html', error="Passwords don't match. Please try again.")

#Allows user to log in if they exist in the database
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('db_login.html', error=request.args.get('error'))
    else: 
        email = request.form.get('email')
        password = request.form.get('password')
    
        results = get_password(email)
        
        if (len(results) == 1):
            update_legal_release(email)
            hashedPassword = results[0]['password']
            
            if check_password_hash(hashedPassword, password):
                session['users'] = email
                return redirect(url_for('db_index'))
            else:
                
                return redirect(url_for('login', error="Passwords don't match"))
        else:
            return redirect(url_for('db_index', error="Error fetching data"))

#Logs user out
@app.route('/logout')
def logout():
    session.pop('users', None)
    return redirect(url_for('db_index'))

#Generates the player information page, where users can update their profiles, legal releases and passwords
@app.route('/player_info')
def player_info():
    if verify_session():
        email = session['users']
        update_legal_release(email)
        
        #Get the legal release info from the database of legal releases 
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM legal_releases WHERE larp_id=%s"
        queryVars = (larp_number,)
        cursor.execute(query, queryVars)
        mysql.connection.commit()
        legal_release_results = cursor.fetchall()
            
        results = get_player_data(email)
        
        return render_template('db_player_ajax.html', rows=results, lrr=legal_release_results)

    else:
        return redirect(url_for('db_index'))

#Generates characters page where players can create and manage characters
@app.route('/characters')
def characters():
    if verify_session():
        email = session['users']
        
        pc_data = get_player_data(email)
        p_id = pc_data[0]['idplayers']
        
        characters = get_character_data(p_id)
        
        return render_template('db_characters.html', pc_data=pc_data, characters=characters)
    
    else:
        return redirect(url_for('db_index'))

#AJAX method for changing password
@app.route('/change_password', methods=['GET','POST'])
def change_password():
    if request.method == 'POST':
        pc_data = request.get_json()
        #print(pc_data)
        
        email=session['users']
        
        orgpw = pc_data[0]['oldpw']
        newpw1 = pc_data[1]['newpw1']
        newpw2 = pc_data[2]['newpw2']
    
        if newpw1 != newpw2:
            error = "Passwords don't match. Please try again."
        elif orgpw == newpw1:
            error = "Same password used. Please use a new password."
        elif len(newpw1) < 8:
            error = "Not a secure password. Passwords must be at least 8 characters. Please try again."
        else:
            results=get_password(email)
            
            hashed_pw = results[0]['password']
            
            if check_password_hash(hashed_pw, orgpw):
                secured_pw = generate_password_hash(newpw1)
                cursor = mysql.connection.cursor()
                query = 'UPDATE users SET password=%s WHERE email=%s'
                queryVars = (secured_pw,email,)
                cursor.execute(query, queryVars)
                mysql.connection.commit()
                error = ""
                
                session.pop('users', None)
            else:
                error="Incorrect original password. Please try again."
    
    if error:
        results = [
            {'processed': 'false'},
            {'error': error}
        ]

    else:
        results = {'processed': 'true'}
    
    return jsonify(results)

#AJAX method for processing updated player data
@app.route('/process_pc_data', methods=['GET', 'POST'])
def process_pc_data():
    if request.method == "POST":
        pc_data = request.get_json()
        #print(pc_data)
        
        email=session['users']
        
        first = pc_data[0]['first']
        last = pc_data[1]['last']
        primary_email = pc_data[2]['email']
        pronouns = pc_data[3]['pronouns']
        e_c_n = pc_data[4]['e_c_n']
        e_c_p = validate_phone(pc_data[5]['e_c_p'])
        
        if len(primary_email) == 0 or primary_email=="None":
            primary_email=email
        
        if e_c_p is not None:
            cursor = mysql.connection.cursor()
            query = """UPDATE players p INNER JOIN users u ON p.user_id = u.idusers SET p.first_name=%s, p.last_name=%s,
                    p.primary_email=%s, p.pronouns=%s, p.emergency_contact_name=%s, p.emergency_contact_phone=%s WHERE u.email=%s"""
            queryVars = (first,last,primary_email,pronouns,e_c_n,e_c_p,email,)
            cursor.execute(query, queryVars)
            mysql.connection.commit()
            
            data = get_player_data(email)
            
            results={'processed': 'true'}
            return jsonify(results)

        else:
            data = get_player_data(email)
         
            results={'processed': 'false'}
            return jsonify(results)

#AJAX method for updating the legal release
@app.route('/update_legal_release', methods=['GET','POST'])
def update_lr():
    if request.method=="POST":
        lr_data = request.get_json()
        
        email=session['users']
        results = get_player_data(email)
        
        name = lr_data[0]['name']
        date = lr_data[1]['date']
        
        player_id = results[0]['idplayers']
        
        cursor = mysql.connection.cursor()
        query = "UPDATE players SET legal_release=%s, signed_name=%s, date_signed=%s WHERE idplayers=%s"
        queryVars = (1,name,date,player_id,)
        cursor.execute(query, queryVars)
        mysql.connection.commit()
        
        results = {"processed": "true"}
        
        return jsonify(results)

#AJAX method for updating the date on the legal release
@app.route('/get_lr_date')
def get_lr_date():
    if verify_session():
        email=session['users']
        results = get_player_data(email)
    
        return render_template('db_lr_date.html', results=results)
    else:
        return redirect(url_for('db_index'))

#Page for creating a new character
@app.route('/new_char', methods=["GET", "POST"])
def new_character():
    if verify_session():
        email=session['users']
        
        if request.method == "GET":
            species = get_species()
            classes = get_classes()
            
            return render_template('db_new_character.html', species=species, classes=classes)
            
        else:
            name = request.form.get('name')
            species = request.form.get('species')
            char_class = request.form.get('class')
            bio = request.form.get('bio')
            picture = request.form.get('pic')
            
            player_data = get_player_data(email)
            player_id = player_data[0]['idplayers']
            
            time = datetime.now()
            
            cursor = mysql.connection.cursor()
            query = 'INSERT INTO characters(player_id, name, xp, hp, mp, bio, picture, species_id, class_id, last_saved, playground_flag) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            queryVars = (player_id, name, XP, HP, MP, bio, picture, species, char_class, time, 0,)
            cursor.execute(query, queryVars)
            mysql.connection.commit()
            
            return redirect(url_for('characters'))
    else:
        return redirect(url_for('db_index'))

#Page for creating a new playground character
@app.route('/new_p_char', methods=["GET", "POST"])
def new_p_character():
    if verify_session():
        email=session['users']
        
        if request.method == "GET":
            species = get_species()
            classes = get_classes()
            
            return render_template('db_new_p_character.html', species=species, classes=classes)
            
        else:
            name = request.form.get('name')
            xp = request.form.get('xp')
            species = request.form.get('species')
            char_class = request.form.get('class')
            bio = request.form.get('bio')
            picture = request.form.get('pic')
            
            player_data = get_player_data(email)
            player_id = player_data[0]['idplayers']
            
            time = datetime.now()
            
            cursor = mysql.connection.cursor()
            query = 'INSERT INTO characters(player_id, name, xp, hp, mp, bio, picture, species_id, class_id, last_saved, playground_flag) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            queryVars = (player_id, name, xp, HP, MP, bio, picture, species, char_class, time, 1,)
            cursor.execute(query, queryVars)
            mysql.connection.commit()
            
            return redirect(url_for('characters'))
    else:
        return redirect(url_for('db_index'))

#Updates HP and MP based on XP for playground characters
@app.route('/update_hp_mp', methods=["POST"])
def update_hp_mp():
    if verify_session():
        email=session['users']
        
        updated_data = request.get_json()
        
        pc_data = get_player_data(email)
        p_id = pc_data[0]['idplayers']
        
        char_id = updated_data[0]['id']
        new_xp = updated_data[1]['xp']
        
        character = get_character(char_id)
        #validate that this character belongs to this player
        
        if character[0]['playground_flag'] == 1:
            #update character with new hp, xp, mp
            hp = get_hp(new_xp)
            mp = get_mp(new_xp)
            
            cursor = mysql.connection.cursor()
            query = 'UPDATE characters SET xp=%s, hp=%s, mp=%s WHERE idcharacters=%s'
            queryVars = (new_xp, hp, mp, char_id)
            cursor.execute(query, queryVars)
            mysql.connection.commit()
            
            results = {"processed": "true"}
        
            return jsonify(results)        
        else:
            results = {"processed": "false"}
        
            return jsonify(results)
    else:
        return redirect(url_for('db_index'))

#AJAX method to update HP and MP on playground character
@app.route('/new_hp_mp', methods=["POST"])
def new_hp_mp():
    if verify_session():
        email=session['users']
        
        player = get_player_data(email)
        
        char_id = request.form.get("charid")
        
        character = get_character(char_id)
        
        return render_template('db_get_hp_mp.html', character=character)
    
    else:
        return redirect(url_for('db_index'))