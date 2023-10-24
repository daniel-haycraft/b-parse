import pyodbc

cursor.execute("SELECT *")




if __name__ == "__main__":
    cnxn = pyodbc.connect("DRIVER={CData ODBC Driver for HubSpot}; DATABASE=CData HubSpot Sys; Auth Scheme=OAuth; OAuth Settings Location='C:/Users/Daniel Haycraft/Desktop/newstuff/OAuth.txt'")
    cursor = cnxn.cursor()
    

















