CREATE DEFINER = CURRENT_USER TRIGGER `broker-er`.`PredictedStock_AFTER_UPDATE` AFTER UPDATE ON `PredictedStock` FOR EACH ROW
BEGIN

	declare t double default 0;

	if new.Future_Date =7 then

		set t =(select avg(Future_Price)
		from `broker-er`.`PredictedStock`
		where Ticker = new.Ticker
		group by Ticker);

		insert into `broker-er`.`PredictedResults`(Ticker,PredictionAvg)
			(select Ticker, avg(Future_Price)
			from `broker-er`.`PredictedStock`
			where Ticker = new.Ticker
			group by Ticker)
		on duplicate key
		update PredictionAvg = t;

    end if;
END

--------------------------------------------------------

CREATE DEFINER = CURRENT_USER TRIGGER `broker-er`.`PredictedStock_AFTER_UPDATE2` AFTER UPDATE ON `PredictedStock` FOR EACH ROW
BEGIN

	declare t double default 0;

	if new.Future_Date =7 then

		set t = (select distinct(Close)
        from `broker-er`.`StockPrice`s1, (select Ticker, max(Date) as maxDate
										from `broker-er`.`StockPrice`
										where Ticker = new.Ticker
										group by Ticker) s2
		where s1.Ticker = s2.Ticker and s1.Date = maxDate);

		insert into `broker-er`.`PredictedResults`(Ticker, RecentPrice)
			(select s1.Ticker, Close
			from `broker-er`.`StockPrice`s1, (select Ticker, max(Date) as maxDate
										from `broker-er`.`StockPrice`
										where Ticker = new.Ticker
										group by Ticker) s2
		where s1.Ticker = s2.Ticker and s1.Date = maxDate)
		on duplicate key
		update RecentPrice = t;

    end if;
END
