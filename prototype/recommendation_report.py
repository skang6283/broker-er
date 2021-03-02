import math
import pandas_datareader as web
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')


from db import Database

def predict(df):

    #create a new dataframe with only the close column

    data = df.filter(['Close'])
    dataset = data.values
    #dataset = data.values

    training_data_len = math.ceil(len(dataset) * 0.8)

    print(training_data_len)

    #Scale the data
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(dataset)

    #print(scaled_data)
    #create the training data set

    train_data = scaled_data[0:training_data_len , :]
    x_train = []
    y_train = []

    for i in range(30, len(train_data)):
        x_train.append(train_data[i-30:i, 0])
        y_train.append(train_data[i, 0])


    #convert to numpy arrays
    x_train, y_train = np.array(x_train), np.array(y_train)

    #reshape the data from 2d to 3d
    x_train = np.reshape(x_train,( x_train.shape[0], x_train.shape[1], 1))
    #print(x_train.shape)

    #build LSTM

    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape = (x_train.shape[1],1)))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(1))

    #compile
    model.compile(optimizer= 'adam', loss ='mean_squared_error')

    #train the model
    model.fit(x_train,y_train, batch_size= 1, epochs=1)

    test_data = scaled_data[training_data_len-30: , :]


    #create the data sets x_test and y_test
    x_test =[]
    y_test = dataset[training_data_len:, :]
    for i in range(30, len(test_data)):
        x_test.append(test_data[i-30:i, 0])

    x_test = np.array(x_test)

    x_test = np.reshape(x_test,(x_test.shape[0], x_test.shape[1], 1))



    #get the models predicted price values

    predictions = model.predict(x_test)
    predictions = scaler.inverse_transform(predictions)

    rmse = np.sqrt(np.mean(predictions - y_test)**2)

    train = data[:training_data_len]
    valid = data[training_data_len:]
    print(predictions)
    print(predictions.shape)
    #numpy array

    print(valid)
    valid['Predictions'] = predictions
    print(valid)

    plt.figure(figsize = (16,8))
    plt.plot(train['Close'])
    plt.plot(valid[['Close','Predictions']])
    plt.legend(['Train','Val', 'Predictions'], loc = 'lower right')
    plt.show()

    quote = df
    new_df = quote.filter(['Close'])
    last_30_days = new_df[-30:].values
    last_30_days_scaled = scaler.transform(last_30_days)

    X_test=[]
    X_test.append(last_30_days_scaled)
    X_test=np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0],X_test.shape[1],1))

    pred_price = model.predict(X_test)
    pred_price = scaler.inverse_transform(pred_price)
    print(pred_price)


if __name__ == "__main__":

    db = Database()
    print(f"Connected: {db.con.open}")
    famous_stocks = db.watchlist_famous_stocks()

    for ticker in famous_stocks:
        stock = ticker['Ticker']
        info = db.get_stock_data(stock)
        predict(info)
