import streamlit as st
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# Load Iris dataset
data = load_iris()
X, y = data.data, data.target
model = RandomForestClassifier()
model.fit(X, y)

# Streamlit app
st.title("AI Prediction Web App")
st.write("This is a simple AI-based prediction app.")

# Create user inputs for the Iris dataset (sepal length, sepal width, etc.)
sepal_length = st.slider("Sepal Length", float(X[:, 0].min()), float(X[:, 0].max()))
sepal_width = st.slider("Sepal Width", float(X[:, 1].min()), float(X[:, 1].max()))
petal_length = st.slider("Petal Length", float(X[:, 2].min()), float(X[:, 2].max()))
petal_width = st.slider("Petal Width", float(X[:, 3].min()), float(X[:, 3].max()))

# Predict button
if st.button("Predict"):
    features = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
    prediction = model.predict(features)
    st.write(f"The predicted class is: {data.target_names[prediction][0]}")

# To execute the program
# streamlit run ai_app.py