import datetime


def is_data_correct(con, item, _vars):
    if con.execute("""SELECT * FROM Items WHERE name = ? and item_id != ?""",
                   (item[1], item[0])).fetchall():
        return False
    for i in _vars:
        if con.execute("""SELECT * FROM Vars WHERE var_id = ? and item_id != ?""",
                       (i[0, item[0]])).fetchall():
            return False
    return True


def get_users(con, name=''):
    res = """SELECT * FROM Users """
    if name:
        res += """WHERE username LIKE '%?%'""".replace('?', name)
    return con.execute(res).fetchall()


def get_user_by_id(con, userid):
    return con.execute("""SELECT *  FROM Users WHERE id = ?""", (userid,)).fetchone()


def get_user_by_username(con, username):
    return con.execute("""SELECT * FROM Users WHERE username = ?""", (username,)).fetchone()


def get_user_by_data(con, username, password):
    return con.execute("""SELECT * FROM Users WHERE username = ? AND password = ?""",
                       (username, password)).fetchone()


def get_cart_id(con, user_id):
    return con.execute("""SELECT order_id FROM OrderData 
    LEFT JOIN Statuses ON OrderData.status = Statuses.id 
    WHERE OrderData.user_id = ? AND Statuses.value = 'cart'""", (user_id,)).fetchone()[0]


def get_vars(con, item_id=0, var_id=0, name='', min_price='', max_price='', size='', color='',
             brand='', gender=''):
    # 0-var_id, 1-item_id, 2-price, 3-size, 4-color
    res = """
    SELECT Vars.var_id, Vars.item_id, Vars.price, Vars.size, Colors.value
    FROM Vars
    LEFT JOIN Colors ON Vars.color = Colors.id
    LEFT JOIN Items ON Vars.item_id = Items.item_id
    LEFT JOIN Genders ON Items.gender = Genders.id
    LEFT JOIN Brands ON Items.brand = Brands.id    
    WHERE true"""
    if item_id:
        res += f""" AND Vars.item_id = {item_id}"""
    if var_id:
        res += f""" AND Vars.var_id = {var_id}"""
    if name:
        res += f""" AND Items.name LIKE '%{name}%'"""
    if min_price:
        res += f""" AND Vars.price >= {min_price}"""
    if max_price:
        res += f""" AND Vars.price <= {max_price}"""
    if size:
        res += f""" AND Vars.size = '{size}'"""
    if color:
        res += f""" AND Colors.value = '{color}'"""
    if brand:
        res += f""" AND Brands.value = '{brand}'"""
    if gender:
        res += f""" AND Genders.value = '{gender}'"""
    return con.execute(res).fetchall()


def get_order_items(con, order_id):
    return con.execute("""SELECT * FROM OrderItems WHERE order_id = ?""", (order_id,)).fetchall()


def get_items(con, item_id='', name='', brand='', gender=''):
    # 0-item_id, 1-name, 2-brand, 3-gender, 4-desc
    res = """
    SELECT Items.item_id, Items.name, Brands.value, Genders.value, Items.description 
    FROM Items
    LEFT JOIN Genders ON Items.gender = Genders.id
    LEFT JOIN Brands ON Items.brand = Brands.id
    WHERE true
    """
    if item_id not in ('', 'unset'):
        res += f""" AND Items.item_id = '{item_id}'"""
    if name not in ('', 'unset'):
        res += f""" AND name LIKE '%{name}%'"""
    if brand not in ('', 'unset'):
        res += f""" AND Brands.value = '{brand}'"""
    if gender not in ('', 'unset'):
        res += f""" AND Genders.value = '{gender}'"""
    return con.execute(res).fetchall()


def get_order_item_by_data(con, order_id, var_id):
    con.execute("""SELECT * FROM OrderItems WHERE order_id = ? AND var_id = ?""",
                (order_id, var_id))
    con.commit()


def get_orders(con):
    return con.execute("""SELECT OrderData.order_id, OrderData.user_id, OrderData.datetime,
       Statuses.value, OrderData.comment, OrderData.delivering_address FROM OrderData
       LEFT JOIN Statuses ON OrderData.status = Statuses.id""").fetchall()


def get_statuses_dict(con):
    return dict(con.execute("""SELECT * FROM Statuses""").fetchall())


def get_brands_dict(con):
    return dict(con.execute("""SELECT * FROM Brands""").fetchall())


def get_genders_dict(con):
    return dict(con.execute("""SELECT * FROM Genders""").fetchall())


def get_colors_dict(con):
    return dict(con.execute("""SELECT id, value FROM Colors""").fetchall())


def set_order_item_count(con, order_id, var_id, count):
    con.execute("""UPDATE OrderItems SET count = ? WHERE order_id = ? AND var_id = ?""",
                (count, order_id, var_id))
    con.commit()


def set_order_status(con, order_id, status):
    con.execute("""UPDATE OrderData SET status = (SELECT id FROM Statuses WHERE value = ?)
    WHERE order_id = ?""", (status, order_id))
    con.commit()


def set_order_comm(con, order_id, comm):
    con.execute("""UPDATE OrderData SET comment = ? WHERE order_id = ?""", (comm, order_id))
    con.commit()


def set_order_address(con, order_id, address):
    con.execute("""UPDATE OrderData SET delivering_address = ? WHERE order_id = ?""",
                (address, order_id))
    con.commit()


def set_order_datetime(con, order_id):
    dt = datetime.datetime.now()
    con.execute("""UPDATE OrderData SET datetime = ? WHERE order_id = ?""", (dt, order_id))
    con.commit()


def set_var_color(con, var_id, color):
    con.execute("""UPDATE Vars SET color = (SELECT id FROM Colors WHERE value = ?) 
    WHERE var_id = ?""", (color, var_id))
    con.commit()


def set_var_size(con, var_id, size):
    con.execute("""UPDATE Vars SET size = ? WHERE var_id = ?""", (size, var_id))
    con.commit()


def set_var_price(con, var_id, price):
    con.execute("""UPDATE Vars SET price = ? WHERE var_id = ?""", (price, var_id))
    con.commit()


def set_item_name(con, item_id, name):
    con.execute("""UPDATE Items SET name = ? WHERE item_id = ?""", (name, item_id))
    con.commit()


def set_item_brand(con, item_id, name):
    con.execute("""UPDATE Items SET brand = (SELECT id FROM Brands WHERE value = ?) 
    WHERE item_id = ?""", (name, item_id))
    con.commit()


def set_item_gender(con, item_id, name):
    con.execute("""UPDATE Items SET gender = (SELECT id FROM Genders WHERE value = ?) 
    WHERE item_id = ?""", (name, item_id))
    con.commit()


def set_item_desc(con, item_id, desc):
    con.execute("""UPDATE Items SET description = ? WHERE item_id = ?""", (desc, item_id))
    con.commit()


def add_user(con, username, password, name, surname, phone, address):
    con.execute("""INSERT INTO Users (username, password, name, surname, phone, address)
    VALUES(?, ?, ?, ?, ?, ?)""", (username, password, name, surname, phone, address))
    con.commit()
    add_order(con, get_user_by_username(con, username)[0])
    con.commit()


def add_order(con, user_id):
    con.execute("""INSERT INTO OrderData (user_id) VALUES (?)""", (user_id,))
    con.commit()


def add_order_item(con, order_id, var_id):
    con.execute("""INSERT INTO OrderItems VALUES (?, ?, ?)""", (order_id, var_id, 1))
    con.commit()


def add_item(con, name, brand, gender, description):
    con.execute("""INSERT INTO Items VALUES (?, ?, ?, ?)""", (name, brand, gender, description))
    con.commit()


def add_var(con, item_id, color, size, price):
    con.execute("""INSERT INTO Vars(item_id, color, size, price) VALUES
    (?, (SELECT id from Colors WHERE value = ?), ?, ?)""", (item_id, color, size, price))
    con.commit()


def delete_order_item_by_data(con, order_id, var_id):
    con.execute("""DELETE FROM OrderItems WHERE order_id = ? AND var_id = ?""", (order_id, var_id))
    con.commit()


def delete_var_and_connected(con, var_id):
    print(var_id)
    con.execute("""DELETE FROM OrderItems WHERE var_id = ?""", (var_id,))
    con.execute("""DELETE FROM Vars WHERE var_id = ?""", (var_id,))
    con.commit()


if __name__ == '__main__':
    import sqlite3

    connection = sqlite3.connect('shop_db.db')
    print(get_vars(connection, item_id=1))
    connection.close()
