import os
import math
import pandas_datareader as web
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
import matplotlib
matplotlib.use("agg")

from db import Database
from sendEmail import sendEmail

import plotly.offline as pyo
import plotly.graph_objects as go
from utils import save_json
import constant


def predict(df,ticker):

    #create a new dataframe with only the close column

    data = df.filter(['Close'])
    dataset = data.values
    #dataset = data.values

    training_data_len = math.ceil(len(dataset) * 1)

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




    test_data = scaled_data[training_data_len-30: ,:]

    x_test = np.array(test_data)

    x_test = x_test[np.newaxis, ...]

    predictionList =[]
    for i in range(7):

        x_test = np.array(x_test)
        x_test = np.reshape(x_test,(x_test.shape[0], x_test.shape[1], 1))

        predictions = model.predict(x_test[-30:])


        predictions_ = np.squeeze(predictions)
        predictionList.append(predictions_)

        x_test_ = np.squeeze(x_test)

        x_test=np.append(x_test_,predictions_)
        x_test = np.reshape(x_test,(1, x_test.shape[0], 1))


    predictionList = np.array(predictionList)
    predictionList = predictionList.reshape(predictionList.shape[0],1)
    predictionList = scaler.inverse_transform(predictionList)
    predictionList = np.squeeze(predictionList)


    print(predictionList)


    train = data[:training_data_len]
    valid = data[training_data_len:]
    #numpy array

    #print(valid)
    #valid['Predictions'] = predictions
    #print(valid)
    graphJSON = plotly_stock(data, predictionList)
    os.makedirs(constant.GRAPH_DIR, exist_ok=True)
    save_json(graphJSON, os.path.join(constant.GRAPH_DIR, f"{ticker}.json"))


    # plt.figure(figsize = (16,8))

    # graph = list(np.squeeze(data.values))

    # graph.append(predictionList[0])

    # fig1 =plt.gcf()

    # plt.plot(graph)

    # plt.plot(np.arange(7)+training_data_len ,predictionList)
    # plt.legend(['Train','Predictions'], loc = 'lower right')
    # plt.show()

    # fig1.savefig("static/graphs/"+ticker+".png")


    return predictionList


def save_image(graph,ticker):
    fig1 =plt.gcf()

    plt.plot(graph)

    plt.plot(np.arange(7)+training_data_len ,predictionList)
    plt.legend(['Train','Predictions'], loc = 'lower right')
    plt.show()

    fig1.savefig("static/graphs/"+ticker+".png")

    return


def insert_prediction(db,ticker,data):

    predictionList = predict(data,ticker)

    for index,prediction in  enumerate(predictionList):
        query = f"""
                INSERT INTO PredictedStock(Ticker, Future_Date, Future_Price)
                VALUES('{ticker}', '{index+1}', '{prediction}')
                ON DUPLICATE KEY
                UPDATE Future_Price = '{prediction}'

        """
        db.cur.execute(query)
        db.con.commit()
    return



def processEmail():
    db = Database()
    stocks = db.get_recommendation()
    emails = db.get_user_emails()

    stocks = [d['Ticker'] for d in stocks]

    for email in emails:
        sendEmail(stocks,email)
        break

def plotly_stock(data, prediction):
    hist_data = go.Scatter(
        x=data.index.values,
        y=data["Close"].values,
        name="Historical Data",
    )

    prediction = np.append(data.values[-1], prediction)
    predict_data = go.Scatter(
        x=np.arange(8) + data.index.values[-1],
        y=prediction,
        mode="lines",
        line=dict(color='firebrick'),
        name="Prediction",
    )

    fig = go.Figure([hist_data, predict_data])
    # Convert the figures to JSON
    graphJSON = fig.to_json()

    return graphJSON



if __name__ == "__main__":
    db = Database()


    result = db.select_stock_with_latest_info()

    for index,row in enumerate(result):

        if index  >2:
            break
        ticker =row['Ticker']
        print(ticker)
        data = db.get_stock_data(ticker)
        if len(data) < 100:
            continue

        insert_prediction(db,ticker,data)

    processEmail()
