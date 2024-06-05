def create_and_count(data, key):
  data[key] = data.get(key, 0) + 1
  print(data)
  return data

# Example usage
my_dict = {}

# Add or increment count for different keys
my_dict = create_and_count(my_dict, "apple")
my_dict = create_and_count(my_dict, "orange")
my_dict = create_and_count(my_dict, "apple")  # Increase apple count

print(my_dict.get("apple",0))

