import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

# Normalize the dataset
transform = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomCrop(32, padding=4),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

# Load the CIFAR-10 dataset
# It's also important to note that increasing the batch size does not always lead to better performance. In some cases, smaller batch sizes can lead to better generalization and lower test error
# especially if the network is well-regularized and the dataset is not too large.
trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                        download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=100,
                                          shuffle=True, num_workers=2)

testset = torchvision.datasets.CIFAR10(root='./data', train=False,
                                       download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=100,
                                         shuffle=False, num_workers=2)

# Define the classes. There are 10 classes so the finaly layer of the network needs to output 10 values
classes = ('plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck')


# define the convolutional neural network architecture using ReLU activation function, adjust as necessary to improve results
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # convolutional layer 1
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        # convolutional layer 2
        self.conv2 = nn.Conv2d(6, 16, 5)
        # Initial settings: 3 fully connected layers with 120, 84, and 10 neurons respectively. The final layer outputs 10 values for the 10 classes. The first layer takes the output of the second convolutional layer as input. 45%
        # Adjust settings for trial and error. Adding fully connected layers may lead to overfitting. Introduce dropout layers may prevent overfitting
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)        
        self.fc3 = nn.Linear(84, 10)     
        # defining a dropout layer and its probability
        self.dropout = nn.Dropout(p=0.25)   

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        # introduce dropout layer if needed. In general, it's common to introduce dropout after the fully connected layers or after the convolutional layers.
        # x = self.dropout(x)        
        x = self.fc3(x)
        return x

net = Net()

# Define the loss function and optimizer using stochastic gradient descent
# The loss function is the cross entropy loss function. It is commonly used for multi-class classification problems like in this scenario
criterion = nn.CrossEntropyLoss()
#optimizer uses the PyTorch SGD optimizer. Adjust the learning rate and momentum as necessary to improve results
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

# Train the network
if __name__ == "__main__":
    # Define number of epochs, adjust as necessary to improve results
    num_epochs = 20

    for epoch in range(num_epochs):
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            inputs, labels = data

            optimizer.zero_grad()

            outputs = net(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        # Print the average loss for this epoch
        print('Epoch %d loss: %.3f' % (epoch + 1, running_loss / (i + 1)))

    print('Finished Training')

    # Test the network
    correct = 0
    total = 0
    with torch.no_grad():
        for data in testloader:
            images, labels = data
            outputs = net(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    print('Accuracy of the network on the 10000 test images: %d %%' % (100 * correct / total))
    x = input("Press Enter to continue...")