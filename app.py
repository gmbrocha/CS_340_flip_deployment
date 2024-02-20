from flask import Flask, render_template, url_for, request
import database.db_connector as db

# config
app = Flask(__name__)
con = db.connect_to_database(host = 'classmysql.engr.oregonstate.edu', user = 'cs340_brocharg', passwd = '3063', db = 'cs340_brocharg')


# routes
@app.route('/')
def root():
    return render_template('main.j2')


# # TODO CONSOLIDATE DISPLAY ROUTES
# @app.route('/display/<display_type>', methods=['POST', 'GET'])
# def display_table(display_type):
    
#     return render_template('status_message.j2', display_type=display_type)


@app.route('/players', methods=['POST', 'GET'])
def display_players():
    
    query = 'SELECT Players.player_name AS name, Special_Abilities.ability_name AS ability, ' \
        'Pets.pet_name AS pet, i.item_name AS weapon, i2.item_name AS armor, Guilds.guild_name AS guild ' \
        'FROM Players ' \
        'LEFT JOIN Special_Abilities ON Players.player_abilityID = Special_Abilities.abilityID ' \
        'LEFT JOIN Pets ON Players.petID = Pets.petID ' \
        'LEFT JOIN Items AS i ON Players.weaponID = i.itemID ' \
        'LEFT JOIN Items AS i2 ON Players.armorID = i2.itemID ' \
        'LEFT JOIN Guilds ON Players.guildID = Guilds.guildID ' \
    
    headers = ['Name', 'Ability', 'Pet', 'Weapon', 'Armor', 'Guild']  # the headers for display in the table

    cur = db.execute_query(db_connection=con, query=query)

    results = cur.fetchall()

    return render_template('players.j2', results=results, headers=headers)

@app.route('/pets', methods=['POST', 'GET'])
def display_pets():

    query = 'SELECT Pets.pet_name AS name, ' \
            'Special_Abilities.ability_name AS ability, ' \
            'Pets.pet_type AS type, Pets.pet_attack AS attack, ' \
            'Pets.pet_defense AS defense ' \
            'FROM Pets INNER JOIN Special_Abilities ' \
            'ON Pets.pet_abilityID = Special_Abilities.abilityID;'

    headers = ['Name', 'Ability', 'Type', 'Attack', 'Defense']  # the headers for display in the table

    cur = db.execute_query(db_connection=con, query=query)

    results = cur.fetchall()

    return render_template('pets.j2', results=results, headers=headers)

@app.route('/abilities', methods=['POST', 'GET'])
def display_abilities():

    query = 'SELECT Special_Abilities.ability_name AS name, ' \
            'Special_Abilities.ability_attack AS attack, ' \
            'Special_Abilities.ability_cost AS cost ' \
            'FROM Special_Abilities;'

    headers = ['Name', 'Attack', 'Cost']  # the headers for display in the table

    cur = db.execute_query(db_connection=con, query=query)

    results = cur.fetchall()

    return render_template('abilities.j2', results=results, headers=headers)    


@app.route('/items', methods=['POST', 'GET'])
def display_items():

    query = 'SELECT Items.item_name AS name, ' \
                'Items.item_type AS type, ' \
                'Items.item_defense AS defense,' \
                'Items.item_attack AS attack,' \
                'Items.item_rarity AS rarity ' \
                'FROM Items;'

    headers = ['Name', 'Type', 'Defense', 'Attack', 'Rarity']  # the headers for display in the table

    cur = db.execute_query(db_connection=con, query=query)

    results = cur.fetchall()

    return render_template('items.j2', results=results, headers=headers)


@app.route('/guilds', methods=['POST', 'GET'])
def display_guilds():

    query = """SELECT Guilds.guild_name AS name, Guilds.guild_color AS color
            FROM Guilds"""

    cur = db.execute_query(db_connection=con, query=query)

    guilds = cur.fetchall()

    headers = ['Name', 'Color', 'Alliances']  # the headers for display in the table

    guilds_names = []
    for g in guilds:
        guilds_names.append([g['name'], hex(g['color'])])

    guilds_dict = {}

    max_members = 0

    for guild in guilds_names:
        alliances = []
        query = f'''SELECT Alliances.alliance_name AS name FROM Alliances
            INNER JOIN Alliances_Guilds
            ON Alliances_Guilds.allianceID = Alliances.allianceID
            INNER JOIN Guilds
            ON Alliances_Guilds.guildID = Guilds.guildID
            WHERE Guilds.guild_name = "{guild[0]}";'''
        cur = db.execute_query(db_connection=con, query=query)
        results = cur.fetchall()

        for d in results:
            alliances.append(d['name'])
        guilds_dict[guild[0]] = alliances
        max_members = max(max_members, len(alliances))
        guilds_dict[guild[0]] = [guild[1], alliances]

        for name in guilds_dict:
            for _ in range(len(guilds_dict[name][1]), max_members):
                guilds_dict[name][1].append('')

    return render_template('guilds.j2', guilds_dict=guilds_dict, max_members=max_members, headers=headers)


@app.route('/alliances', methods=['POST', 'GET'])
def display_alliances():

    query = 'SELECT Alliances.alliance_name AS name ' \
            'FROM Alliances'

    headers = ['Name']  # the headers for display in the table

    cur = db.execute_query(db_connection=con, query=query)

    results = cur.fetchall()

    alliances_names = []
    for d in results:
        alliances_names.append(d['name'])

    alliances_members = {}

    max_members = 0

    for alliance in alliances_names:
        guilds = []
        query = f"""SELECT Guilds.guild_name AS name FROM Guilds
                JOIN Alliances_Guilds
                ON Alliances_Guilds.guildID = Guilds.guildID
                JOIN Alliances
                ON Alliances_Guilds.allianceID = Alliances.allianceID
                WHERE Alliances.alliance_name = '{alliance}';"""
        cur = db.execute_query(db_connection=con, query=query)
        results = cur.fetchall()

        for d in results:
            guilds.append(d['name'])
        max_members = max(max_members, len(guilds))
        alliances_members[alliance] = guilds

    for name in alliances_members:
        for _ in range(len(alliances_members[name]), max_members):
            alliances_members[name].append('')
            
    return render_template('alliances.j2', alliances_members=alliances_members, max_members=max_members)

@app.route('/delete', methods=['POST', 'GET'])
def delete_db_entry():

    select = request.form.get('delete-type')
    query = ''
    record = request.form.get('record')

    if select == 'Player':
        query = f"DELETE FROM Players WHERE player_name = '{record}';"
    if select == 'Pet':
        query = f"DELETE FROM Pets WHERE pet_name = '{record}';"
    if select == 'Ability':
        query = f"DELETE FROM Special_Abilities WHERE ability_name = '{record}';"
    if select == 'Item':
        query = f"DELETE FROM Items WHERE item_name = '{record}';"
    if select == 'Guild':
        query = f"DELETE FROM Guilds WHERE guild_name = '{record}';"
    if select == 'Alliance':
        query = f"DELETE FROM Alliances WHERE alliance_name = '{record}';"

    message = 'Record Deleted!'
    try:
        db.execute_query(db_connection=db, query=query)
    except:
        message = "Record NOT Deleted! Bet you didn't check to see whether that key was attached to another entity. Shame."
    finally:
        return render_template('status_message.j2', message=message)


@app.route('/update', methods=['POST', 'GET'])
def create_update_form():
     # get the entry type from the form
    select = request.form.get('update-type')
    record_name = request.form.get('record')

    # # TODO COMMENT THESE QUERIES
    ability_query = "SELECT `ability_name` FROM `Special_Abilities`;"
    pet_query = "SELECT `pet_name` FROM `Pets`;"
    weapon_query = "SELECT `item_name` FROM `Items` WHERE `item_type` = 'weapon';"
    armor_query = "SELECT `item_name` FROM `Items` WHERE `item_type` ='armor';"
    guild_query = "SELECT `guild_name` FROM `Guilds`;"

    # create empty queries for cases that the attribute isn't necessary
    fields = []
    abilities = []
    pets = []
    weapons = []
    armors = []
    guilds = []
    pet_types = []

    # these aren't nested, they don't have their own queries because they are static
    item_types = ['sword', 'armor']
    item_rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary']

    if select == "Player":
        # fields = ['Name', 'Ability', 'Pet', 'Weapon', 'Armor', 'Guild']
        fields = ['Ability', 'Pet', 'Weapon', 'Armor', 'Guild']

        # get abilities for dropdown
        cur = db.execute_query(db_connection=con, query=ability_query)
        abilities = cur.fetchall()

        # get pets for dropdown
        cur = db.execute_query(db_connection=con, query=pet_query)
        pets = cur.fetchall()

        # get weapons for dropdown
        cur = db.execute_query(db_connection=con, query=weapon_query)
        weapons = cur.fetchall()

        # get armors for dropdown
        cur = db.execute_query(db_connection=con, query=armor_query)
        armors = cur.fetchall()

        # get guilds for dropdown
        cur = db.execute_query(db_connection=con, query=guild_query)
        guilds = cur.fetchall()

        # TODO FIGURE OUT THIS QUERY BELOW - THIS RECORD WILL BE USED TO PREPOPULATE THE FORM
        # TODO pass the player_record object to the template and parse it for placeholder= in each input

        # query = f"""SELECT Players.player_name, Special_Abilities.ability_name, Pets.pet_name, Items.item_name,
        #         Items.item_name, Guilds.guild_name 
        #         FROM Players 
        #         LEFT JOIN Special_Abilities ON Special_Abilities.abilityID = Players.player_abilityID
        #         LEFT JOIN Pets ON Players.petID = Pets.petID
        #         LEFT JOIN Items ON Players.weaponID = Items.itemID
        #         LEFT JOIN Items ON Players.armorID = Items.itemID
        #         LEFT JOIN Guilds ON Players.guildID = Guilds.guildID
        #         WHERE Players.player_name = '{record_name}'"""
        # cur = db.execute_query(db_connection=con, query=query)
        # player_record = cur.fetchall()

    if select == "Pet":
        # fields = ['Name', 'Ability', 'Pet Type', 'Attack', 'Defense']
        fields = ['Ability', 'Pet Type', 'Attack', 'Defense']

        # get abilities for dropdown
        cur = db.execute_query(db_connection=con, query=ability_query)
        abilities = cur.fetchall()

    if select =="Ability":
        # fields = ['Name', 'Attack', 'Cost']
        fields = ['Attack', 'Cost']

    if select == "Item":
        # fields = ['Name', 'Item Type', 'Defense', 'Attack', 'Rarity']
        fields = ['Item Type', 'Defense', 'Attack', 'Rarity']

    if select == "Guild":
        # fields = ['Name', 'Color']
        fields = ['Color']

    if select == "Alliance":
        # fields = ['Name']
        fields = []

    return render_template('update_form.j2', name=record_name, select_type=select, fields=fields, abilities=abilities, pets=pets,
                           weapons=weapons, armors=armors, item_types=item_types, guilds=guilds,
                           item_rarity=item_rarities, pet_types=pet_types)

@app.route('/update-db', methods=['POST', 'GET'])
def update_db_entry():
    pass

@app.route('/create-db-entry', methods=['POST'])
def create_db_entry():

    query = ''
    values = []

    select = request.form.get('select-type')

    if select == 'Player':
        fields = ['Name', 'Ability', 'Pet', 'Weapon', 'Armor', 'Guild']
        for i in range(len(fields)):
            values.append(request.form.get(fields[i]))

        query = f"""INSERT INTO Players (player_name, player_abilityID, petID, weaponID, armorID, guildID)  
            VALUES ('{values[0]}', (SELECT abilityID FROM Special_Abilities WHERE ability_name = '{values[1]}'),
            (SELECT petID FROM Pets WHERE pet_name = '{values[2]}'),
            (SELECT itemID FROM Items WHERE item_name = '{values[3]}'), 
            (SELECT itemID FROM Items WHERE item_name = '{values[4]}'), 
            (SELECT guildID FROM Guilds WHERE guild_name = '{values[5]}'));"""

    if select == 'Pet':
        # todo validate the attack and defense to be integers
        fields = ['Name', 'Ability', 'Pet Type', 'Attack', 'Defense']
        for i in range(len(fields)):
            values.append(request.form.get(fields[i]))
        query = f"""INSERT INTO Pets (pet_name, pet_abilityID, pet_type, pet_attack, pet_defense) 
            VALUES ('{values[0]}', (SELECT abilityID FROM Special_Abilities WHERE ability_name = '{values[1]}'), 
            '{values[2]}', {int(values[3])}, {int(values[4])});"""

    if select == 'Ability':
        # todo validate the attack and cost to be integers
        fields = ['Name', 'Attack', 'Cost']
        for i in range(len(fields)):
            values.append(request.form.get(fields[i]))
        query = f"""INSERT INTO Special_Abilities (ability_name, ability_attack, ability_cost) 
            VALUES ('{values[0]}', {int(values[1])}, {int(values[2])});"""

    if select == 'Item':
        # todo validate the defense and attack to be integers
        fields = ['Name', 'Item Type', 'Defense', 'Attack', 'Rarity']
        for i in range(len(fields)):
            values.append(request.form.get(fields[i]))
        query = f"""INSERT INTO Items (item_name, item_type, item_defense, item_attack, item_rarity) 
            VALUES ('{values[0]}', '{values[1]}', {int(values[2])}, {int(values[3])}, '{values[4]}');"""

    if select == 'Guild':
        # todo validate the color entry to be an integer
        fields = ['Name', 'Color']
        for i in range(len(fields)):
            values.append(request.form.get(fields[i]))
        query = f"""INSERT INTO Guilds (guild_name, guild_color) 
            VALUES ('{values[0]}', {int(values[1])});"""

    if select == 'Alliance':
        # only 1 value in the return form here, just put it in the query
        query = f"""INSERT INTO Alliances (alliance_name) 
            VALUES ('{request.form.get('Name')}');"""

    db.execute_query(db_connection=con, query=query)

    message = 'Record Created!'

    return render_template('status_message.j2', message=message)

@app.route('/create-entry-form', methods=['POST', 'GET'])
def create_entry_form():

    # get the entry type from the form dropdown
    select = request.form.get('entry-type')

    # # TODO COMMENT THESE QUERIES
    ability_query = "SELECT `ability_name` FROM `Special_Abilities`;"
    pet_query = "SELECT `pet_name` FROM `Pets`;"
    weapon_query = "SELECT `item_name` FROM `Items` WHERE `item_type` = 'weapon';"
    armor_query = "SELECT `item_name` FROM `Items` WHERE `item_type` ='armor';"
    guild_query = "SELECT `guild_name` FROM `Guilds`;"

    # create empty queries for cases that the attribute isn't necessary
    fields = []
    abilities = []
    pets = []
    weapons = []
    armors = []
    guilds = []
    pet_types = []

    # these aren't nested, they don't have their own queries because they are static
    item_types = ['sword', 'armor']
    item_rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary']

    if select == "Player":
        fields = ['Name', 'Ability', 'Pet', 'Weapon', 'Armor', 'Guild']
        # get abilities for dropdown
        cur = db.execute_query(db_connection=con, query=ability_query)
        abilities = cur.fetchall()

        # get pets for dropdown
        cur = db.execute_query(db_connection=con, query=pet_query)
        pets = cur.fetchall()

        # get weapons for dropdown
        cur = db.execute_query(db_connection=con, query=weapon_query)
        weapons = cur.fetchall()

        # get armors for dropdown
        cur = db.execute_query(db_connection=con, query=armor_query)
        armors = cur.fetchall()

        # get guilds for dropdown
        cur = db.execute_query(db_connection=con, query=guild_query)
        guilds = cur.fetchall()

    if select == "Pet":
        fields = ['Name', 'Ability', 'Pet Type', 'Attack', 'Defense']

        # get abilities for dropdown
        cur = db.execute_query(db_connection=con, query=ability_query)
        abilities = cur.fetchall()

    if select =="Ability":
        fields = ['Name', 'Attack', 'Cost']

    if select == "Item":
        fields = ['Name', 'Item Type', 'Defense', 'Attack', 'Rarity']

    if select == "Guild":
        fields = ['Name', 'Color']

    if select == "Alliance":
        fields = ['Name']

    return render_template('entry_form.j2', select_type=select, fields=fields, abilities=abilities, pets=pets,
                           weapons=weapons, armors=armors, item_types=item_types, guilds=guilds,
                           item_rarity=item_rarities, pet_types=pet_types)


if __name__ == "__main__":
    
    app.run(port=6754, debug=True)

    # gunicorn -b 0.0.0.0:6754 -D app:app
    # pkill -u brocharg gunicorn