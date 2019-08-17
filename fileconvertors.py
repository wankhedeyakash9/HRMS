def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        bin_data = file.read()
    return bin_data


def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)
