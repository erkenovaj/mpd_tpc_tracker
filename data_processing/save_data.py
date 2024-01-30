def save_data(tracks):
    # Saving new tracks
    with open("data/new_event.txt", "w") as f:
        for track in tracks:
            temp = ""
            for hit in track:
                for characteristic in hit:
                    temp += str(characteristic) + ", "
            temp = temp[:-2] + "\n"
            f.write(temp)
