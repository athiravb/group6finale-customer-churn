import numpy as np
import pandas as pd
import pickle
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import confusion_matrix,accuracy_score,precision_score,recall_score,f1_score

from sklearn.preprocessing import LabelEncoder

#from sklearn.preprocessing import LabelEncoder


from sklearn.model_selection import train_test_split
df = pd.read_excel(r"D:/ecommerce_churn/E Commerce Dataset.xlsx",sheet_name=1)
# Correct values of column PreferredLoginDevice, WarehouseToHome, PreferredPaymentMode and PreferedOrderCat
df['PreferredLoginDevice'].replace({'Mobile Phone':'Mobile', 'Phone':'Mobile'}, inplace=True)
df['WarehouseToHome'].replace({126:26, 127:27}, inplace=True)
df['PreferredPaymentMode'].replace({'Credit Card':'CC', 'Cash on Delivery':'COD', 'Debit Card':'DC'}, inplace=True)
df['PreferedOrderCat'].replace({'Mobile Phone':'Mobile', 'Laptop & Accessory':'Laptop'}, inplace=True)
# Fill missing values ith mean and median
df.fillna({'HourSpendOnApp':round(df.HourSpendOnApp.mean()),
           'Tenure':round(df.Tenure.mean()),
           'OrderAmountHikeFromlastYear':round(df.OrderAmountHikeFromlastYear.mean()),
           'WarehouseToHome':round(df.WarehouseToHome.mean()),
           'CouponUsed':df.CouponUsed.median(),
           'OrderCount':df.OrderCount.median(),
           'DaySinceLastOrder':df.DaySinceLastOrder.median()}, inplace=True)
percentile = df.Tenure.quantile([0.99]).values
df['Tenure'] = df['Tenure'].apply(lambda x : percentile[0] if x > percentile[0] else x)
percentile = df.DaySinceLastOrder.quantile([0.99]).values
df['DaySinceLastOrder'] = df['DaySinceLastOrder'].apply(lambda x : percentile[0] if x > percentile[0] else x)
percentile = df.CashbackAmount.quantile([0.01, 0.99]).values
df['CashbackAmount'] = df['CashbackAmount'].apply(lambda x : percentile[0] if x < percentile[0] else percentile[1] if x > percentile[1] else x)
# Generating new features from cashback amount divided order count
df['avg_cashbk_per_order'] = df['CashbackAmount'] / df['OrderCount']
df.drop(columns=['CustomerID', 'HourSpendOnApp', 'OrderAmountHikeFromlastYear', 'CouponUsed', 'OrderCount'], axis=1, inplace=True)
le =LabelEncoder()
df['Gender'] =le.fit_transform(df['Gender'])
df['MaritalStatus'] =le.fit_transform(df['MaritalStatus'])
df['PreferredLoginDevice'] =le.fit_transform(df['PreferredLoginDevice'])
cat=['PreferredPaymentMode','PreferedOrderCat']
df_encoded= pd.get_dummies(df,columns=cat)
 # Separate independent and dependent
X= df_encoded.drop('Churn', axis=1)
y = df_encoded['Churn']

# Initialize random oversampler
ros = RandomOverSampler()


# Fit and transform the data
X_resampled, y_resampled = ros.fit_resample(X, y)
# fit predictor and target variable

#Combine balanced X and y
df_encoded = pd.DataFrame(X_resampled, columns=df_encoded.drop('Churn', axis=1).columns)
df_encoded['Churn'] =y_resampled
# Separate dependent and independent variables
X = df_encoded.drop('Churn', axis=1)
y= df_encoded.Churn
print(df_encoded.columns)

# Split train and test data
X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=.15,random_state =100)
# Checking the target rate in the population, train sample and test sample
print("Population risk rate :",
      round(sum(df_encoded.Churn)*100/len(df_encoded), 2),"%")
print("Train set risk rate :",
      round(sum(y_train)*100/len(y_train), 2),"%")
print("Test set risk rate :",
      round(sum(y_test)*100/len(y_test), 2),"%")
#Random Forest
from sklearn.ensemble import RandomForestClassifier
rf_clf = RandomForestClassifier()
rf_clf.fit(X_train,y_train)
model=rf_clf.fit(X_train,y_train)
y_pred=rf_clf.predict(X_test)

print('Accuracy = ',accuracy_score(y_test,y_pred))
rf=round(accuracy_score(y_test,y_pred),2)

print('precision = ',precision_score(y_test,y_pred))
print('Recall = ',recall_score(y_test,y_pred))
print('f1 score =',f1_score(y_test,y_pred))
print(confusion_matrix(y_test,y_pred))
#Created pickle file 
pickle.dump(model,open("rfmodel.pkl","wb"))