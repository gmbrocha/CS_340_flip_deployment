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

    query = 'SELECT Guilds.guild_name AS name, ' \
            'Guilds.guild_color AS color ' \
            'FROM Guilds'

    headers = ['Name', 'Color']  # the headers for display in the table

    cur = db.execute_query(db_connection=con, query=query)

    guilds = cur.fetchall()

    # convert color int to hex and replace value, change from tuple since immutable
    guilds_list = []
    for el in guilds:
        hex_color = hex(el['color'])
        guilds_list.append([el['name'], hex_color])

    return render_template('guilds.j2', results=guilds_list, headers=headers)


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

    # query = f"""SELECT Guilds.guild_name AS name FROM Guilds
    #             INNER JOIN Alliances_Guilds
    #             ON Alliances_Guilds.guildID = Guilds.guildID
    #             INNER JOIN Alliances
    #             ON Alliances_Guilds.allianceID = Alliances.allianceID
    #             WHERE Alliances.alliance_name = '{alliances_names[0]}';"""
    
    # cur = db.execute_query(db_connection=con, query=query)
    # result = cur.fetchall()

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
            
    return render_template('alliances.j2', headers=headers)
    # return render_template('alliances.j2', results=alliances_members, headers=headers, max_members=max_members)
    # return render_template('status_message.j2', message=alliances_members)

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
        message = 'Record NOT Deleted! (Check Keys?)'
    finally:
        return render_template('status_message.j2', message=message)


@app.route('/update', methods=['POST', 'GET'])
def create_update_form():
    # TODO THIS NEEDS TO BE FIXED
    pass
    # # need to check form hidden attribute which will contain the update type
    # select = request.form.get('update-type')

    # ability_query = 'SELECT ability_name FROM Special_Abilities;'
    # pet_query = 'SELECT pet_name FROM Pets;'
    # weapon_query = 'SELECT item_name FROM Items WHERE item_type = "sword";'
    # armor_query = 'SELECT item_name FROM Items WHERE item_type ="armor";'
    # guild_query = 'SELECT guild_name FROM Guilds;'
    # pet_type_query = 'SELECT DISTINCT pet_type FROM Pets;'

    # fields = []
    # abilities = []
    # pets = []
    # weapons = []
    # armors = []
    # guilds = []
    # pet_types = []

    # # TODO FINISH CASES
    # if select == 'Player':
    #     fields = ['Name', 'Ability', 'Pet', 'Weapon', 'Armor', 'Guild']
    #     item_types = ['sword', 'armor']
    #     item_rarity = ['common', 'uncommon', 'rare', 'legendary']

    #     cur = db.execute_query(db_connection=con, query=ability_query)
    #     abilities = cur.fetchall()

    #     cur = db.execute_query(db_connection=con, query=pet_query)
    #     pets = cur.fetchall()

    #     cur = db.execute_query(db_connection=con, query=weapon_query)
    #     weapons = cur.fetchall()

    #     cur = db.execute_query(db_connection=con, query=armor_query)
    #     armors = cur.fetchall()

    #     cur = db.execute_query(db_connection=con, query=guild_query)
    #     guilds = cur.fetchall()

    # if select == 'Item':
    #     fields = ['Name', 'Item Type', 'Defense', 'Attack', 'Rarity']
    #     item_types = ['sword', 'armor']
    #     item_rarity = ['common', 'uncommon', 'rare', 'legendary']

    # if select == "Pet":
    #     fields = ['Name', 'Ability', 'Pet Type', 'Attack', 'Defense']
    #     item_types = ['sword', 'armor']
    #     item_rarity = ['common', 'uncommon', 'rare', 'legendary']

    #     # get abilities for dropdown
    #     cur = db.execute_query(db_connection=con, query=ability_query)
    #     abilities = cur.fetchall()

    #     # get abilities for dropdown
    #     cur = db.execute_query(db_connection=con, query=pet_type_query)
    #     pet_types = cur.fetchall()

    #     if select == "Ability":
    #         fields = ['Name', 'Attack', 'Cost']
    #         item_types = ['sword', 'armor']
    #         item_rarity = ['common', 'uncommon', 'rare', 'legendary']

    #     if select == "Guild":
    #         fields = ['Name', 'Color']
    #         item_types = ['sword', 'armor']
    #         item_rarity = ['common', 'uncommon', 'rare', 'legendary']

    #     if select == "Alliance":
    #         fields = ['Name']
    #         item_types = ['sword', 'armor']
    #         item_rarity = ['common', 'uncommon', 'rare', 'legendary']

    # return render_template('update_form.j2', select_type=select, fields=fields, abilities=abilities, pets=pets,
    #                        weapons=weapons, armors=armors, guilds=guilds, pet_types = pet_types, item_types = item_types,
    #                        item_rarity = item_rarity)

@app.route('/update-db', methods=['POST', 'GET'])
def update_db_entry():
    # TODO FINISH THIS IMPLEMENTATION
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