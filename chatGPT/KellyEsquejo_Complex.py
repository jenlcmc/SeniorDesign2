# Importing necessary libraries
import pandas as pd  # Library for data manipulation
from sklearn.model_selection import train_test_split, KFold  # For data splitting and K-Fold cross-validation
from tensorflow import keras  # High-level neural networks API
from keras.utils import to_categorical  # Utility function for one-hot encoding

# Reading data from CSV file and preprocessing
data = pd.read_csv("MNIST_HW4.csv")  # Read data from CSV file
X = data.drop('label', axis=1)  # Features
y = data.iloc[:, 0]  # Labels

# Splitting data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=0)

# Normalizing pixel values to be between 0 and 1
X_train = X_train / 255
X_test = X_test / 255

# One-hot encoding of labels
y_train = to_categorical(y_train)
y_test = to_categorical(y_test)

# Define neural network model
KerasModel = keras.Sequential([
    keras.layers.Dense(50, activation='sigmoid', input_shape=(784,)),  # Input layer
    keras.layers.Dense(50, activation='relu'),  # Hidden layer 1
    keras.layers.Dropout(0.3),  # Dropout layer
    keras.layers.Dense(50, activation='relu'),  # Hidden layer 2
    keras.layers.Dropout(0.3),  # Dropout layer
    keras.layers.Dense(10, activation='softmax')  # Output layer
])

# Define hyperparameters for grid search
Optimizer = ['SGD', 'Adam']
Loss_function = ['binary_crossentropy', 'mean_squared_error']
Learning_rate = [0.01, 0.001, 0.0001, 0.00001]
Batch_size = [32, 64, 128]
Max_epochs = [20]

# Perform grid search with K-Fold cross-validation
Grid_search = []  # List to store results
kf = KFold(n_splits=5, shuffle=True, random_state=0)  # K-Fold cross-validator

for optimizer in Optimizer:
    for loss_function in Loss_function:
        for learning_rate in Learning_rate:
            for bs in Batch_size:
                for max_epochs in Max_epochs:
                    print(optimizer, loss_function, learning_rate, bs, max_epochs)  # Print current hyperparameters

                    # Define optimizer based on selected algorithm
                    if optimizer == "SGD":
                        optimizer_ = keras.optimizers.SGD(lr=learning_rate)
                    else:
                        optimizer_ = keras.optimizers.Adam(lr=learning_rate)

                    # Compile the model with selected optimizer and loss function
                    KerasModel.compile(optimizer=optimizer_, loss=loss_function, metrics=['accuracy'])

                    accuracies = []  # List to store accuracies for each fold

                    # K-Fold cross-validation loop
                    for train_index, val_index in kf.split(X_train):
                        X_train_fold, X_val_fold = X_train.iloc[train_index], X_train.iloc[val_index]
                        y_train_fold, y_val_fold = y_train[train_index], y_train[val_index]

                        # Train the model
                        KerasModel.fit(X_train_fold, y_train_fold, epochs=max_epochs, batch_size=bs, verbose=0,
                                       validation_split=0.2)

                        # Evaluate the model on validation data
                        _, accuracy = KerasModel.evaluate(X_val_fold, y_val_fold, verbose=0)
                        accuracies.append(accuracy)

                    # Calculate mean accuracy across all folds
                    mean_accuracy = sum(accuracies) / len(accuracies)
                    print('Mean Accuracy: %.2f' % (mean_accuracy * 100))

                    # Store results in Grid_search list
                    Grid_search.append([optimizer, loss_function, learning_rate, bs, max_epochs, mean_accuracy])

                    # Break loop if mean accuracy exceeds a threshold
                    if mean_accuracy >= 0.86:
                        break

# Create DataFrame to tabulate fold-wise accuracies
KerasDataframe = pd.DataFrame(accuracies).T

# Import tabulate library to format table
from tabulate import tabulate

headers = ["Fold 1", "Fold 2", "Fold 3", "Fold 4", "Fold 5", "mean_accuracy"]

# Format and print the table
table = tabulate(KerasDataframe, headers=headers, tablefmt="pipe", floatfmt=".2f")
print(table)
