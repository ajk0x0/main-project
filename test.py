import cv2

def close_window_on_button_press():
    # Open the webcam
    cap = cv2.VideoCapture(-1)

    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()

        # Display the frame in a window
        cv2.namedWindow("RECEIVING VIDEO", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("RECEIVING VIDEO", 640, 480)
        cv2.imshow("RECEIVING VIDEO",frame)
        cv2.moveWindow("RECEIVING VIDEO", 40,30)
        cv2.resizeWindow("Resized_Window", 640, 480)

        # Check for key press event
        key = cv2.waitKey(1) & 0xFF

        # If 'q' key is pressed, close the window
        if key == ord('q'):
            break

    # Release the webcam and close all cv2 windows
    cap.release()
    cv2.destroyAllWindows()

# Call the function to start the webcam view
close_window_on_button_press()
