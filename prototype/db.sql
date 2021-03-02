CREATE TABLE Users(
username VARCHAR(255) primary key,
email    VARCHAR(255),
password VARCHAR(255)
);


CREATE TABLE Stocks(
company_name  VARCHAR(255),
date_         DATETIME,
price         INT,


PRIMARY KEY(company_name)
);


CREATE TABLE Watchlist(
  username   VARCHAR(255),
  company_name VARCHAR(255),
  owned     BOOLEAN default FALSE,

  PRIMARY KEY(username, company_name),
  FOREIGN KEY(username) REFERENCES Users(username) ON DELETE CASCADE,
  FOREIGN KEY(company_name) REFERENCES Stocks(company_name) ON UPDATE CASCADE
);
