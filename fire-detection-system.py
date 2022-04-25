#from logging import exception
#from cv2 import blur
#from matplotlib.pyplot import hsv
import cv2, numpy, playsound, smtplib, json

with open("mail_settings.json", 'r') as mail_settings_file:
    mail_settings = json.load (mail_settings_file)

with open("system_settings.json", 'r') as system_settings_file:
    system_settings_file = json.load (system_settings_file)

fires_reported = 0
alarm_status = False

video = cv2.VideoCapture(system_settings_file["flame_video"])

while True:

    ret, frame = video.read()
    frame = cv2.resize(frame, (1000, 600))
    blur = cv2.GaussianBlur(frame, (15, 15), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    lower = numpy.array([18, 50, 50], dtype = 'uint8')
    upper = numpy.array([35, 255, 255], dtype = 'uint8')

    mask = cv2.inRange(hsv, lower, upper)

    output = cv2.bitwise_and(frame, hsv, mask = mask)

    size = cv2.countNonZero(output)

    if int(size) > 15000:
        fires_reported += 1

        if (fires_reported >= 1) and not alarm_status:
            playsound.playsound(system_settings_file["alarm_audio"])
            alarm_status = True

            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.ehlo()
                server.starttls()
                server.login(mail_settings["systemEmailAddress"], mail_settings["systemEmailPassword"])
                server.sendmail(mail_settings["mail"]["subject"], mail_settings["recipientMail"], mail_settings["mail"]["body"])
                print ("Sent to", mail_settings["recipientMail"])
                server.close()
            except Exception as e:
                print (e)

    if not ret:
        break

    cv2.imshow("output", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()

video.release()