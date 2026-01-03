import cv2
import numpy as np
import time

from mediapipe import Image, ImageFormat
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions

from logic import clamp, ema, finger_is_up, point_in_rect
from strokes import StrokeHistory


def find_camera(max_index=5):
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cap.release()
            return i
        cap.release()
    return None


def main():
    cam_index = find_camera()
    if cam_index is None:
        return

    cap = cv2.VideoCapture(cam_index)

    base_options = BaseOptions(
        model_asset_path="models/hand_landmarker.task"
    )

    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6,
    )

    landmarker = vision.HandLandmarker.create_from_options(options)

    canvas = None
    draw_mask = None
    smooth_point = None
    alpha = 0.35

    history = StrokeHistory()
    current_stroke = None

    colors = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
    }

    color_names = list(colors.keys())
    color_index = 0
    current_color = colors[color_names[color_index]]

    tool = "draw"

    min_size = 4
    max_size = 24
    current_size = 10

    panel_width = 160
    btn_x1, btn_x2 = 20, panel_width - 20
    btn_h = 56
    btn_gap = 14

    y = 40
    buttons = {}

    for name in ["undo", "redo", "clear"]:
        buttons[name] = (btn_x1, y, btn_x2, y + btn_h)
        y += btn_h + btn_gap

    y += 10
    buttons["color"] = (btn_x1, y, btn_x2, y + btn_h)
    y += btn_h + btn_gap

    buttons["erase"] = (btn_x1, y, btn_x2, y + btn_h)
    y += btn_h + 30

    slider_y = y
    slider_bar = (btn_x1 + 10, slider_y, btn_x2 - 10, slider_y)

    hover_start = {name: None for name in buttons}
    hold_time = 0.6

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.flip(frame, 1)

        if canvas is None:
            canvas = np.zeros_like(frame, dtype=np.uint8)
            draw_mask = np.zeros(frame.shape[:2], dtype=np.uint8)

        h, w, _ = frame.shape

        frame[:, :panel_width] = (245, 245, 245)
        cv2.line(frame, (panel_width, 0), (panel_width, h), (200, 200, 200), 2)

        def draw_button(rect, label, color):
            x1, y1, x2, y2 = rect
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
            text_color = (0, 0, 0) if sum(color) > 500 else (255, 255, 255)
            cv2.putText(
                frame,
                label,
                (x1 + 18, y2 - 18),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                text_color,
                2,
            )

        draw_button(buttons["undo"], "UNDO", (90, 90, 90))
        draw_button(buttons["redo"], "REDO", (90, 90, 90))
        draw_button(buttons["clear"], "CLEAR", (70, 70, 70))
        draw_button(buttons["color"], "COLOR", current_color)

        erase_color = (210, 210, 210) if tool == "erase" else (160, 160, 160)
        draw_button(buttons["erase"], "ERASE", erase_color)

        cv2.putText(
            frame,
            "SIZE",
            (btn_x1, slider_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (80, 80, 80),
            1,
        )

        x1, y1, x2, _ = slider_bar
        cv2.line(frame, (x1, y1), (x2, y1), (120, 120, 120), 4)
        slider_x = int(x1 + (current_size - min_size) / (max_size - min_size) * (x2 - x1))
        cv2.circle(frame, (slider_x, y1), 8, (80, 80, 80), -1)

        interacting = False

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = Image(
            image_format=ImageFormat.SRGB,
            data=rgb,
        )

        result = landmarker.detect(mp_image)

        if result.hand_landmarks:
            hand = result.hand_landmarks[0]
            tip = hand[8]
            joint = hand[6]

            raw_x = int(tip.x * w)
            raw_y = int(tip.y * h)

            smooth_point = ema(smooth_point, (raw_x, raw_y), alpha)
            x, y = smooth_point

            indicator_color = current_color if tool == "draw" else (120, 120, 120)
            radius = current_size if tool == "draw" else current_size * 2
            cv2.circle(frame, (x, y), radius, indicator_color, 2)

            for name, rect in buttons.items():
                if point_in_rect((x, y), rect):
                    interacting = True
                    if hover_start[name] is None:
                        hover_start[name] = time.time()
                    elif time.time() - hover_start[name] > hold_time:
                        if name == "undo":
                            history.undo()
                        elif name == "redo":
                            history.redo()
                        elif name == "clear":
                            history.clear()
                        elif name == "color":
                            color_index = (color_index + 1) % len(color_names)
                            current_color = colors[color_names[color_index]]
                            tool = "draw"
                        elif name == "erase":
                            tool = "erase"
                        hover_start[name] = None
                else:
                    hover_start[name] = None

            if abs(y - slider_y) < 20 and x1 <= x <= x2:
                interacting = True
                ratio = clamp((x - x1) / (x2 - x1), 0.0, 1.0)
                current_size = int(min_size + ratio * (max_size - min_size))

            if finger_is_up(tip.y * h, joint.y * h) and not interacting and x > panel_width:
                if current_stroke is None:
                    current_stroke = history.start_stroke(
                        current_color, current_size, tool
                    )
                history.add_point(current_stroke, (x, y))
            else:
                current_stroke = None
        else:
            smooth_point = None
            current_stroke = None

        canvas[:] = 0
        draw_mask[:] = 0

        for stroke in history.strokes:
            pts = stroke.points
            for i in range(1, len(pts)):
                if stroke.tool == "draw":
                    cv2.line(canvas, pts[i - 1], pts[i], stroke.color, stroke.size)
                    cv2.line(draw_mask, pts[i - 1], pts[i], 255, stroke.size)
                else:
                    cv2.line(draw_mask, pts[i - 1], pts[i], 0, stroke.size * 2)

        output = frame.copy()
        output[draw_mask == 255] = canvas[draw_mask == 255]

        cv2.imshow("Scribbly", output)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()