# Import all the necessary toolkits
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from keras import layers
import matplotlib.pyplot as plt

print("Starting the AI model training process...")

# --- Step 1: Load the Processed Data ---
try:
    df = pd.read_csv('processed_dataset.csv')
    print("Successfully loaded 'processed_dataset.csv'.")
except FileNotFoundError:
    print("Error: 'processed_dataset.csv' not found.")
    print("Please run the 'preprocess_data.py' script first.")
    exit()

# --- Step 2: Prepare the Data for the AI ---
# Neural networks work best when all numbers are small, usually between 0 and 1.
# MinMaxScaler is the perfect tool for this.
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(df)

# We will use our "normal" data for both training and testing the reconstruction.
# We split the data so we can train on one part and validate on another unseen part.
X_train, X_test = train_test_split(data_scaled, test_size=0.2, random_state=42)

print(f"Data prepared: {len(X_train)} samples for training, {len(X_test)} for testing.")

# --- Step 3: Build the Autoencoder Model (The Brain's Architecture) ---
# We define the number of features our data has.
n_features = X_train.shape[1]

# The model is built layer by layer.
model = keras.Sequential([
    # Input layer: Takes our data
    layers.Input(shape=(n_features,)),
    # Encoder: This layer compresses the data into a smaller representation
    layers.Dense(4, activation='relu'), # Smaller than n_features
    # Decoder: This layer tries to reconstruct the original data from the compressed version
    layers.Dense(n_features, activation='sigmoid') # Must be same size as input
])

# Compile the model, telling it how to learn.
# 'adam' is a smart learning algorithm.
# 'mae' (Mean Absolute Error) is how we will measure the "reconstruction error".
model.compile(optimizer='adam', loss='mae')
model.summary() # Prints a summary of the model architecture

# --- Step 4: Train the Model ---
print("\nStarting model training... This might take several minutes.")
# We 'fit' the model to our training data.
# epochs=50 means the model will look at the entire dataset 50 times.
# batch_size=32 means it will process data in chunks of 32 rows.
# validation_data allows us to see how well it performs on the test data it hasn't seen.
history = model.fit(
    X_train, X_train, # Note: We are teaching it to reconstruct itself
    epochs=50,
    batch_size=32,
    validation_data=(X_test, X_test),
    shuffle=True,
    verbose=1 # This will show a progress bar
)

# --- Step 5: Visualize the Learning Process ---
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Training History')
plt.ylabel('Loss (Reconstruction Error)')
plt.xlabel('Epoch')
plt.legend()
plt.show()

# --- Step 6: Save the Final Trained Model ---
# The trained "brain" is saved to a single file.
model.save('anomaly_detector.h5')

print("-" * 30)
print("Training complete!")
print("The AI model has been saved as 'anomaly_detector.h5'.")
print("This file is your trained anomaly detector.")