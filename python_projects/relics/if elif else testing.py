import random
while True:
    try:
        height = int(input("Enter your height to be judged by a clanker:"))
        height_1 = ["u tall🗿",
                    "you are deemed worthy by the clanker👍", "finally someone worthy"]
        choice = random.choice(height_1)
        if (height > 170):
            print(choice)
        elif (height > 160):
            print("ok respectable👍")
        elif (height > 150):
            print("lol cant see you")
        else:
            print("you are not seen by anyone🤣👇")
        break
    except ValueError:
        print("type a number previous input was invalid")
