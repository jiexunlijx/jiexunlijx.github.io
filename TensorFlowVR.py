import time
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow import keras
from keras import regularizers

# Load the CIFAR-10 dataset
(X_train, y_train), (X_test, y_test) = tf.keras.datasets.cifar10.load_data()

# Preprocess the data
X_train = X_train / 255.0
X_test = X_test / 255.0


train_data = tf.data.Dataset.from_tensor_slices((X_train, y_train))
# Sets training data batch
train_data = train_data.shuffle(buffer_size=1024).batch(32)

# Define the model architecture. We will use a simple CNN with 3 convolutional layers, followed by 2 fully connected layers
# Note: We are using the ReLU activation function, which is commonly used in deep learning models
# Note: We are using the MaxPooling2D function to reduce the dimension of the feature maps. This helps to reduce computational cost, improve generalization, and act as a form of regularization to mitigate overfitting
model = tf.keras.Sequential([
  # input shape expects a 32x32 pixel image with 3 color channels (RGB)
  # outputs 32 channels, convolutional kernel/filter size is 3x3 size
  # The filter slides over the input data and performs a dot product between its weights and the corresponding input values.
  tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
  tf.keras.layers.MaxPooling2D((2, 2)),
  # Include L2 regularization to reduce overfitting
  tf.keras.layers.Conv2D(64, (3, 3), activation='relu', kernel_regularizer=regularizers.l2(0.001)),
  tf.keras.layers.Flatten(),
  tf.keras.layers.Dense(64, activation='relu'),
  # Set dropout rate. Dropout is a regularization technique that helps to prevent overfitting by randomly dropping units (along with their connections) from the neural network during training
  tf.keras.layers.Dropout(0.2),  
  # Ensure that the output values are normalized and represent probabilities for each of the 10 classes using Softmax activation function
  tf.keras.layers.Dense(10, activation='softmax')
])

# Note: We are using the Adam optimizer, which has advantages over Stochastic Gradient Descent for this problem
# Adam should adaptively adjust the learning rate and momentum for each parameter in the model, based on the first and second moments of the gradients.
# It also includes a momentum term that helps to smooth out the gradients and speed up convergence. The adaptive learning rates and momentum are updated during training based on the history of the gradients
# This allows the optimizer to adapt to the changing landscape of the loss function.
model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
              metrics=['accuracy'])

# Train the model. Set number of epochs to train. The Adam optimizer will adaptively adjust learning rate and momentum
history = model.fit(X_train, y_train, epochs=15, validation_data=(X_test, y_test))

# Evaluate the model
test_loss, test_acc = model.evaluate(X_test, y_test, verbose=2)
print('Test accuracy:', test_acc)

# Plot the accuracy and loss over time
plt.plot(history.history['accuracy'], label='accuracy')
plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
plt.plot(history.history['loss'], label='loss')
plt.plot(history.history['val_loss'], label = 'val_loss')
plt.xlabel('Epoch')
plt.ylabel('Metric')
plt.legend(loc='lower right')
plt.show()

# Save the trained model
sav = input ("Save trained model? (y/n): ")
if sav == "y" or sav == "Y" or sav == "yes" or sav == "Yes" or sav == "YES":
  model.save('cifar10_model.h5')
  print("Model saved as cifar10_model.h5")
  time.sleep(2)
else:
  print("Model not saved")
  time.sleep(1)

