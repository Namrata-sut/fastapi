data = [
    {"id": 1, "Name": "Namrata"},
    {"id": 1, "Name": "Namrata"},
    {"id": 2, "Name": "Namrata"},
    {"id": 3, "Name": "Namrata"},
    {"id": 3, "Name": "Namrata"},
]

for i in range(len(data)):
    for j in range(i+1, len(data)):
        while data[i]["id"] == data[j]["id"]:
            data[j]["id"] += 1

print(data)
