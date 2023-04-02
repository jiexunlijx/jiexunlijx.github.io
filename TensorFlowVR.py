import tensorflow as tf
import matplotlib.pyplot as plt

# Load the CIFAR-10 dataset
(X_train, y_train), (X_test, y_test) = tf.keras.datasets.cifar10.load_data()

# Preprocess the data
X_train = X_train / 255.0
X_test = X_test / 255.0

# Sets training data batch to 128
train_data = tf.data.Dataset.from_tensor_slices((X_train, y_train))
train_data = train_data.shuffle(buffer_size=1024).batch(128)

# Define the model architecture. We will use a simple CNN with 3 convolutional layers, followed by 2 fully connected layers
# Note: We are using the ReLU activation function, which is commonly used in deep learning models
# Note: We are using the MaxPooling2D function to reduce the dimension of the feature maps. This helps to reduce computational cost, improve generalization, and act as a form of regularization to mitigate overfitting
# Note: We are using the Flatten function to flatten the feature maps into a 1D vector
# Note: We are using the Dense function to create a fully connected layer
# Softmax activation function is not used after the final layer because the SparseCategoricalCrossentropy loss function is used instead. 
# The SparseCategoricalCrossentropy loss function applies a softmax activation function to the output of the final layer internally
model = tf.keras.Sequential([
  tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
  tf.keras.layers.Flatten(),
  tf.keras.layers.Dense(64, activation='relu'),
  tf.keras.layers.Dense(10)
])

# Compile the model. Sparse Categorical Crossentropy loss function is used in this case which include softmax activation function internally
# Note: We are using the Adam optimizer, which has advantages over Stochastic Gradient Descent for this problem
model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

# Train the model. The Adam optimizer used calculates an adaptive learning rate for each parameter in the model, based on the first and second moments of the gradients. 
# It also includes a momentum term that helps to smooth out the gradients and speed up convergence. The adaptive learning rates and momentum are updated during training based on the history of the gradients
# This allows the optimizer to adapt to the changing landscape of the loss function.
history = model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test))

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