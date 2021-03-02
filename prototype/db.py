import os
import sys
import constant
import pymysql
import yaml
import pandas as pd

class Database:
    def __init__(self):
        db_crediential = yaml.load(open(os.path.join(constant.CREDENTIAL_DIR, 'db.yaml')), Loader=yaml.FullLoader)
        host = db_crediential['mysql_host']
        user = db_crediential['mysql_user']
        password = db_crediential['mysql_password']
        db = db_crediential['mysql_db']
        self.con = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.
                                   DictCursor)
        self.cur = self.con.cursor()

    def insert_stock_data(self, filename):
        """
        SQL operation for inserting stock data into MySQL from a .csv file.
        """
        df = pd.read_csv(os.path.join(constant.DATA_DIR, filename))

        for index, row in df.iterrows():
            self.cur.execute("INSERT INTO stockprice(ticker, date, open, high, low, close, volume) VALUES(%s, %s, %s, %s, %s, %s, %s)",
                            (row['Ticker'], row['Date'], row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))
            if index % 1000 == 0:
                print(f"Inserted {index} rows")
        self.con.commit()
        self.con.close()

    def select_stock_with_latest_info(self):
        """
        SQL operation for selecting stock data displayed in home page.
        """
        query = """




                    SELECT latest_price.Ticker, sector, country, Date, Open
                    FROM StockInfo INNER JOIN (
                        SELECT Ticker, Date, CAST(Open AS DECIMAL(5, 2)) AS Open
                        FROM StockPrice
                        WHERE Date = (SELECT MAX(Date)
                                    FROM StockPrice)) latest_price  ON latest_price.Ticker = StockInfo.Ticker




                """
        self.cur.execute(query)
        result = self.cur.fetchall()
        #self.cur.close()
        return result





    def select_stock_with_max_price(self):
        """
        SQL operation for selecting stock data displayed in home page.
        """
        query = """
                    SELECT Ticker, MAX(Close)
                    FROM StockPrice
                    GROUP BY Ticker
                """
        self.cur.execute(query)
        result = self.cur.fetchall()
        #self.cur.close()
        return result


    def select_stock_with_daily_price(self, ticker):
        query = f"""
                    SELECT Ticker, Date, CAST(Open AS DECIMAL(5, 2)) AS Open,
                                         CAST(High AS DECIMAL(5, 2)) AS High,
                                         CAST(Low AS DECIMAL(5, 2)) AS Low,
                                         CAST(Close AS DECIMAL(5, 2)) AS Close
                    FROM StockPrice
                    WHERE Ticker = '{str(ticker)}'
                 """
        self.cur.execute(query)
        result = self.cur.fetchall()
        return result

    def get_user_id(self, user_id):
        query = f"""
                    SELECT user_id
                    FROM Users
                    WHERE user_id = '{user_id}'
        """
        self.cur.execute(query)
        result = self.cur.fetchall()
        return result[0]['user_id']

    def get_user_password(self, user_id):
        query = f"""
                    SELECT password
                    FROM Users
                    WHERE user_id = '{user_id}'
        """
        self.cur.execute(query)
        result = self.cur.fetchall()
        return result[0]['password']



    #default watchlist
    def watchlist_default(self,user_id):
        query = f"""
                    SELECT* FROM Watchlist
                    WHERE username like '{user_id}'
        """
        self.cur.execute(query)
        result = self.cur.fetchall()
        return result

    #SEARCH
    def watchlist_search(self, user_id,ticker):
        query = f"""
                    SELECT *
                    FROM Watchlist
                    WHERE ticker like '{ticker}' and username ='{user_id}'
        """
        self.cur.execute(query)
        result = self.cur.fetchall()
        return result

    #INSERT
    def watchlist_insert(self,user_id,ticker):
        query = f"""
                    INSERT INTO Watchlist(username, ticker)
                    VALUES('{user_id}', '{ticker}')
                    ON DUPLICATE KEY
                    UPDATE username = username

        """
        self.cur.execute(query)
        self.con.commit()
        return

    #UPDATE
    def watchlist_update(self,user_id,ticker):
        query = f"""
                    UPDATE Watchlist
                    SET owned = IF (owned,0,1)
                    WHERE ticker like '{ticker}' and username like '{user_id}'
        """
        self.cur.execute(query)
        self.con.commit()
        return

    #DELETE
    def watchlist_delete(self,user_id,ticker):
        query = f"""
                    DELETE FROM Watchlist
                    WHERE ticker like '{ticker}' and username like '{user_id}'
        """
        self.cur.execute(query)
        self.con.commit()
        return

    def watchlist_famous_stocks(self):
        query = f"""
                    select s1.Ticker, sector, country
                    from (select Ticker
                    from `Broker-er`.`Watchlist`
                    group by Ticker
                    order by sum(owned)
                    limit 10)s1 join `Broker-er`.`StockInfo` s2
                    where s1.Ticker = s2.Ticker

        """
        self.cur.execute(query)
        result = self.cur.fetchall()
        return result

    def get_stock_data(self,ticker):
        query = pd.read_sql_query(f"""
                    SELECT Ticker, Date, CAST(Close AS DECIMAL(5, 2)) AS Close
                    FROM StockPrice
                    WHERE Ticker = '{str(ticker)}'
                 """, self.con)

        result = pd.DataFrame(query, columns=['Ticker', 'Date','Close'])
        #self.cur.execute(query)
        #result = self.cur.fetchall()
        return result


    def get_recommendation(self):
        query = f"""
                select Ticker
                from PredictedResults
                where PredictionAvg > RecentPrice
        """
        self.cur.execute(query)
        results = self.cur.fetchall()
        return results

    def get_user_emails(self):
        query = f"""
                    SELECT distinct(email)
                    FROM Users
        """
        self.cur.execute(query)
        emails = self.cur.fetchall()
        return emails








if __name__ == "__main__":
    # Test db connection
    db = Database()
    print(f"Connected: {db.con.open}")
