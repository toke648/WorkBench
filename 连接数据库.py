import mysql.connector


t = mysql.connector.connect(
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 host="localhost",
        user="root",
        password="srd217",
        database="library"
    )

print(t)