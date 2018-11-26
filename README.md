# Room-Presence-detection
A cloud-based application for detecting presence in a room using Raspberry pi.

How the System works
1.The pi (client) is placed at a site (In this case a room) and the server side which receives the information from the pi and does the processing and displays the result to the user.
2.The pi (client) is placed at the site and is on a listening mode. The client consists of a buffer and voice is recognized in terms of 0s for no sound and 1s for sound.
Description of process:
The device is passively listening to voice. If voice is detected, the device enters “Phase 1” in which it listens for a set amount of time for voice - if more than 50% of voice is present in that time interval, it classifies the room as occupied and enters “Phase 2”. In that phase it listens for another set interval of time - if less than 10% of voice is present it considers the room free and resets to the passive listening. If voice is greater than 10% then it loops back into Phase 2.
3.When the room is classified as occupied, a HTTP request will be sent to the server side with the room number and the room status.
4.The server receives the HTTP request and updates the visual interface for the room and stores the information in the database to be used for logging purposes later.
5. When the room is classified as free, the device updates the room status and sends a record of occupation (date and time occupied to date and time freed)
