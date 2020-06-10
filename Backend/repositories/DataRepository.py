from .Database import Database

class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def read_metingen():
        sql = "SELECT Metingen.metingsid, Metingen.apparaatid, cast(Metingen.tijdstip AS char) AS tijdstip, Metingen.waarde, Apparaten.eenheid FROM Metingen JOIN Apparaten ON Apparaten.apparaatid = Metingen.apparaatid ORDER BY Metingen.tijdstip DESC"
        return Database.get_rows(sql)
    
    @staticmethod
    def read_metingen_per_id(apparaatid):
        sql = "SELECT Metingen.metingsid, Metingen.apparaatid, cast(Metingen.tijdstip AS char) AS tijdstip, Metingen.waarde, Apparaten.eenheid FROM Metingen JOIN Apparaten ON Apparaten.apparaatid = Metingen.apparaatid WHERE Metingen.apparaatid = %s ORDER BY Metingen.tijdstip"
        params = [apparaatid]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_metingen_per_id_IR(apparaatid):
        sql = "SELECT Metingen.metingsid, Metingen.apparaatid, cast(Metingen.tijdstip AS date) AS tijdstip, sum(Metingen.waarde) AS waarde, Apparaten.eenheid FROM Metingen JOIN Apparaten ON Apparaten.apparaatid = Metingen.apparaatid WHERE Metingen.apparaatid = %s GROUP BY cast(Metingen.tijdstip AS date)"
        params = [apparaatid]
        return Database.get_rows(sql, params)
    
    @staticmethod
    def read_latest_meting_per_id(apparaatid):
        sql = "SELECT Metingen.metingsid, Metingen.apparaatid, cast(Metingen.tijdstip AS char) AS tijdstip, Metingen.waarde, Apparaten.eenheid FROM Metingen JOIN Apparaten ON Apparaten.apparaatid = Metingen.apparaatid WHERE Metingen.apparaatid = %s ORDER BY Metingen.tijdstip DESC LIMIT 1"
        params = [apparaatid]
        return Database.get_one_row(sql, params)

    @staticmethod
    def add_meting(apparaatid, tijdstip, waarde):
        sql = "INSERT INTO Metingen (apparaatid, tijdstip, waarde) VALUES (%s,%s,%s)"
        params = [apparaatid, tijdstip, waarde]
        return Database.execute_sql(sql, params)
    
    @staticmethod
    def read_apparaten():
        sql = "SELECT * FROM Apparaten"
        return Database.get_rows(sql)