import mysql.connector
from mysql.connector import Error

# try:
#     connection = mysql.connector.connect(host='pxukqohrckdfo4ty.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',
#                                          database='ozd6eww85spj1jca',
#                                          user='d47b8lhhas1vt18z',
#                                          password='fuqvj51bkxu6h8rd')
#     mySql_insert_query = """create table claims(username varchar(30), date date,       
# 							claimId int auto_increment,       
# 							description varchar(30), amount decimal(10, 2), primary key(claimId)) """

#     cursor = connection.cursor()
#     cursor.execute(mySql_insert_query)
#     connection.commit()
#     print(cursor.rowcount, "Record inserted successfully into claims table")
#     cursor.close()

# except mysql.connector.Error as error:
#     print("Failed to insert record into Laptop table {}".format(error))

# finally:
#     if connection.is_connected():
#         connection.close()
#         print("MySQL connection is closed")

try:
	username = "ebilsanta"
	description = "test2"
	amount = 22.3
	month = '12'
	day = '12'
	f_date = f"2022-{month}-{day}"
	connection = mysql.connector.connect(host='pxukqohrckdfo4ty.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',
                                         database='ozd6eww85spj1jca',
                                         user='d47b8lhhas1vt18z',
                                         password='fuqvj51bkxu6h8rd')
	cursor = connection.cursor()
	mySql_insert_query = """INSERT INTO claims (username, date, description, amount) 
						VALUES (%s, %s, %s, %s)"""
	record = (username, f_date, description, str(amount))
	cursor.execute(mySql_insert_query, record)
	connection.commit()
	connection.close()
	cursor.close()
	print("MySQL connection is closed")

except mysql.connector.Error as error:
	print("Error adding claim, please check formatting!")

try:
	username = "ebilsanta"
	connection = mysql.connector.connect(host='pxukqohrckdfo4ty.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',
                                         database='ozd6eww85spj1jca',
                                         user='d47b8lhhas1vt18z',
                                         password='fuqvj51bkxu6h8rd')

	sql_select_Query = "select * from claims where username = %s"

	cursor = connection.cursor()
	cursor.execute(sql_select_Query, (username,))
	records = cursor.fetchall()
	print("Total number of rows in table: ", cursor.rowcount)

	print("\nPrinting each row")
	for row in records:
		print("username = ", row[0])
		print("date = ", row[1])
		print("claimId = ", row[2])
		print("description = ", row[3])
		print("amount = ", row[4], "\n")
	connection.close()
	cursor.close()
	print("MySQL connection is closed")
	print(records)

except mysql.connector.Error as e:
	print("Error getting claims, please contact @ebilsanta for help")