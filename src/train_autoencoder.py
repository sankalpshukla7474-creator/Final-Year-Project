import pandas as pd
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam

# Load processed data
data = pd.read_csv("data/processed/processed_data.csv")
X = data.values

# Autoencoder architecture
input_dim = X.shape[1]

input_layer = Input(shape=(input_dim,))
encoded = Dense(16, activation="relu")(input_layer)
encoded = Dense(8, activation="relu")(encoded)

decoded = Dense(16, activation="relu")(encoded)
decoded = Dense(input_dim, activation="sigmoid")(decoded)

autoencoder = Model(inputs=input_layer, outputs=decoded)

# Compile model
autoencoder.compile(
    optimizer=Adam(learning_rate=0.001),
    loss="mae"
)

# Train model
history = autoencoder.fit(
    X, X,
    epochs=50,
    batch_size=64,
    validation_split=0.2,
    shuffle=True,
    callbacks=[
        EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True
        )
    ]
)

# Save trained model
autoencoder.save("models/autoencoder_model.keras")

print("✅ Autoencoder training completed and model saved.")
