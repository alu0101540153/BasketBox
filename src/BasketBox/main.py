import pygame
import cv2
from . import (
    screen, clock, font, space, background,
    box_bodies, box_rotations, draw_box, draw_hand_landmarks_and_lines,
    detect_fist, update_box_rotation, hands
)

def main():
    running = True
    capture = cv2.VideoCapture(0)
    carrying_box = [False, False, False]
    hand_status_text = ["Mano abierta"] * 3

    # Inicializar hands dentro de main para evitar UnboundLocalError
    import mediapipe as mp
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

    # --- Splash screen before game starts ---
    splash_image = pygame.image.load("images/splash.jpg")
    splash_image = pygame.transform.scale(splash_image, (800, 600))
    show_splash = True
    while show_splash:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                show_splash = False
        screen.blit(splash_image, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ret, frame = capture.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        hand_position = None
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index_tip = hand_landmarks.landmark[8]
                hand_position = (int(index_tip.x * 800), int(index_tip.y * 600))

                for i in range(3):
                    if detect_fist(hand_landmarks.landmark):
                        if not carrying_box[i] and hand_position and box_bodies[i].position.get_distance(hand_position) < 50:
                            carrying_box[i] = True
                            update_box_rotation(i, hand_landmarks)
                        hand_status_text[i] = "Mano cerrada"
                    else:
                        carrying_box[i] = False
                        hand_status_text[i] = "Mano abierta"

        for i in range(3):
            if carrying_box[i] and hand_position:
                box_bodies[i].position = hand_position
                box_bodies[i].velocity = (0, 0)
                update_box_rotation(i, results.multi_hand_landmarks[0])

        space.step(1 / 60.0)

        screen.blit(background, (0, 0))
        for i in range(3):
            draw_box(box_bodies[i].position, box_rotations[i])

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                draw_hand_landmarks_and_lines(hand_landmarks.landmark)

        for i in range(3):
            text_surface = font.render(hand_status_text[i], True, (0, 0, 0))
            screen.blit(text_surface, (10, 10 + i * 30))

        pygame.display.flip()
        cv2.imshow("Cámara", frame)
        clock.tick(60)

    del hands
    capture.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()
