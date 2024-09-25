def menu():
    print("[1] Vcenter Info ")
    print("[2] Session Details")
    print("[3] VM Details")
    print("[0] Exit")

menu()
option = int(input("Enter Option Number:"))

while option != 0:
    if option == 1:
        # Option 1 function here
        print("option 1")
    elif option == 2:
        # Option 2 function here
        print ("option 2")
    elif option == 3:
        #option 3 function here
        print ("option 3")
    else:
        print("Invalid Option - Please choose from the list above")

    menu()
    option = int(input("Enter Option Number:"))

print ("Deuces")