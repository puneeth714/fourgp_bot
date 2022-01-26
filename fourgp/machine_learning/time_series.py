from prophet import Prophet
import pandas as pd

# load csv file
df = pd.read_csv('data/time_series.csv', header=None)
print(df.tail())

# remove column 1,2,4,5,6,7,8,9,10,11 from dataframe
df = df.drop([1, 2, 4, 5, 6, 7, 8, 9, 10, 11], axis=1)

# set column names ds,y in place of 0 and 3 columns
df.columns = ['ds', 'y']
print(df.tail())

# convert unix time to date time in ds coloumn
df['ds'] = pd.to_datetime(df['ds'], unit='ms')
print(df.tail())

# initialize prophet object
model = Prophet()
# fit data into prophet object model
model.fit(df)
# predict future dates
future = model.make_future_dataframe(periods=10)
print(future.tail())
# predict future values
forecast = model.predict(future)
print(forecast.tail())
# plot forecast
model.plot(forecast)
# plot forecast components
model.plot_components(forecast)
