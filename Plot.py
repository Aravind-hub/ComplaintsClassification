import matplotlib.pyplot as plt

# Create your dictionary
data = {"Apple": 10, "Banana": 15, "Orange": 8}

# Extract keys and values into separate lists
keys = list(data.keys())
values = list(data.values())

# Choose the plot type (bar chart in this example)
plt.bar(keys, values)  # Keys on x-axis, values on y-axis

# Add labels and title
plt.xlabel("Fruits")
plt.ylabel("Quantity")
plt.title("Fruit Quantity")

# Display the plot
# label_count.png
image_name = "label_count.png"
plt.savefig('label_count.png')
