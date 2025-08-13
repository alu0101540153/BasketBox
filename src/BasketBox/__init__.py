import pygame
import pymunk
import mediapipe as mp
import math

# ============================
# Constants
# ============================
WIDTH, HEIGHT = 800, 600
SKIN_COLOR = (241, 194, 125)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# ============================
# Pygame Initialization
# ============================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# ============================
# Pymunk Physics Setup
# ============================
space = pymunk.Space()
space.gravity = (0, 900)  # Gravity pointing downwards

# Ground and walls (static objects)
static_lines = [
    pymunk.Segment(space.static_body, (0, 540), (800, 540), 5),  # Ground
    pymunk.Segment(space.static_body, (0, 0), (0, 600), 5),      # Left wall
    pymunk.Segment(space.static_body, (800, 0), (800, 600), 5)   # Right wall
]
for line in static_lines:
    line.elasticity = 1.5
    space.add(line)

# ============================
# Create Physical Boxes
# ============================
box_bodies = []
box_shapes = []
box_rotations = []

for i in range(3):
    body = pymunk.Body(1, pymunk.moment_for_box(1, (80, 80)))
    body.position = (400 + (i * 100), 250)
    shape = pymunk.Poly.create_box(body, (80, 80))
    shape.elasticity = 0.5
    space.add(body, shape)
    box_bodies.append(body)
    box_shapes.append(shape)
    box_rotations.append(0)

# ============================
# Load Images
# ============================
image = pygame.image.load("images/caja.png")
image = pygame.transform.scale(image, (80, 80))

background = pygame.image.load("images/cancha.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# ============================
# Mediapipe Hands Setup
# ============================
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# ============================
# Helper Functions
# ============================

def draw_box(position, rotation):
    """
    Draws a box at a given position with a given rotation.
    """
    rotated_image = pygame.transform.rotate(image, rotation)
    new_rect = rotated_image.get_rect(center=position)
    screen.blit(rotated_image, new_rect.topleft)

def detect_fist(landmarks):
    """
    Detects if the hand is forming a fist based on the distance between
    the thumb tip and the index finger tip.
    """
    if not landmarks:
        return False
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
    return distance < 0.1

def get_hand_rotation(landmarks):
    """
    Calculates the rotation angle of the hand in degrees.
    """
    wrist = landmarks[mp_hands.HandLandmark.WRIST]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    dx = index_tip.x - wrist.x
    dy = index_tip.y - wrist.y
    return -math.degrees(math.atan2(dy, dx))

def draw_hand_landmarks_and_lines(hand_landmarks):
    """
    Draws the hand landmarks and connections on the screen.
    """
    connections = [
        (mp_hands.HandLandmark.WRIST, mp_hands.HandLandmark.THUMB_CMC),
        (mp_hands.HandLandmark.WRIST, mp_hands.HandLandmark.PINKY_MCP),
        (mp_hands.HandLandmark.THUMB_CMC, mp_hands.HandLandmark.THUMB_MCP),
        (mp_hands.HandLandmark.THUMB_MCP, mp_hands.HandLandmark.THUMB_IP),
        (mp_hands.HandLandmark.THUMB_IP, mp_hands.HandLandmark.THUMB_TIP),
        (mp_hands.HandLandmark.INDEX_FINGER_MCP, mp_hands.HandLandmark.INDEX_FINGER_PIP),
        (mp_hands.HandLandmark.INDEX_FINGER_PIP, mp_hands.HandLandmark.INDEX_FINGER_DIP),
        (mp_hands.HandLandmark.INDEX_FINGER_DIP, mp_hands.HandLandmark.INDEX_FINGER_TIP),
        (mp_hands.HandLandmark.MIDDLE_FINGER_MCP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
        (mp_hands.HandLandmark.MIDDLE_FINGER_PIP, mp_hands.HandLandmark.MIDDLE_FINGER_DIP),
        (mp_hands.HandLandmark.MIDDLE_FINGER_DIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP),
        (mp_hands.HandLandmark.RING_FINGER_MCP, mp_hands.HandLandmark.RING_FINGER_PIP),
        (mp_hands.HandLandmark.RING_FINGER_PIP, mp_hands.HandLandmark.RING_FINGER_DIP),
        (mp_hands.HandLandmark.RING_FINGER_DIP, mp_hands.HandLandmark.RING_FINGER_TIP),
        (mp_hands.HandLandmark.PINKY_MCP, mp_hands.HandLandmark.PINKY_PIP),
        (mp_hands.HandLandmark.PINKY_PIP, mp_hands.HandLandmark.PINKY_DIP),
        (mp_hands.HandLandmark.PINKY_DIP, mp_hands.HandLandmark.PINKY_TIP),
    ]

    # Draw connections
    for start_idx, end_idx in connections:
        start = hand_landmarks[start_idx]
        end = hand_landmarks[end_idx]
        pygame.draw.line(
            screen, SKIN_COLOR,
            (int(start.x * WIDTH), int(start.y * HEIGHT)),
            (int(end.x * WIDTH), int(end.y * HEIGHT)), 12
        )

    # Draw points
    for landmark in hand_landmarks:
        pygame.draw.circle(
            screen, SKIN_COLOR,
            (int(landmark.x * WIDTH), int(landmark.y * HEIGHT)), 3
        )

def update_box_rotation(i, hand_landmarks):
    """
    Updates the rotation of a box based on the hand's rotation.
    """
    rotation = get_hand_rotation(hand_landmarks.landmark)
    box_rotations[i] = rotation
