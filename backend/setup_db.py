import pymysql

try:
    connection = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='your_password',
        port=3306
    )

    with connection.cursor() as cursor:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS organ_donation_db"
        )
        print("Database created successfully.")

    connection.commit()
    connection.close()

except pymysql.MySQLError as e:
    print("MySQL connection failed.")
    print(e)