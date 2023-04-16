import cv2
import numpy as np
import pyautogui
import time
import keyboard
import os


def get_image_files(folder_path):
    image_files = [os.path.join(folder_path, file) for file in os.listdir(
        folder_path) if file.endswith(".png")]
    return image_files


def find_image_on_screen(image_path, screen, confidence=0.69):
    template = cv2.imread(image_path, cv2.IMREAD_COLOR)

    if template is None:
        print(f"Failed to load image: {image_path}")
        return None

    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > confidence:
        w, h = template.shape[:-1]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        print(f"Found image at ({center_x}, {center_y})")
        return center_x, center_y

    return None


def move_and_click(x, y):
    coords = (x, y)
    pyautogui.moveTo(coords, duration=0.1)
    time.sleep(0.1)  # Add a small delay between moving the mouse and clicking
    pyautogui.mouseDown(coords)
    time.sleep(0.1)  # Add a small delay between mouseDown and mouseUp events
    pyautogui.mouseUp(coords)
    print(f"Moved mouse to and clicked on {coords}")


def is_esc_pressed():
    return keyboard.is_pressed("esc")


def search_and_click_images(image_names, screen, priority_order):
    for priority in priority_order:
        image_name = image_names[priority]
        coords = find_image_on_screen(image_name, screen)
        if coords:
            move_and_click(coords[0], coords[1])
            print(f"Found and clicked {image_name} on screen.")
            return True
    return False

# Function used for clicks where a new screenshot needs to be grabbed every time


def find_and_click_sequence(image_names, offsets, sleep_times):
    for i, image_name in enumerate(image_names):
        screen = pyautogui.screenshot()
        screen = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
        coords = find_image_on_screen(image_name, screen)
        if coords:
            x_offset, y_offset = offsets[i]
            move_and_click(coords[0] + x_offset, coords[1] + y_offset)
            time.sleep(sleep_times[i])
            print(f"Found {image_name}, clicking on it")
        else:
            print(f"Could not find {image_name} on screen.")
            break


def main():
    image_names = {
        'go_button': 'priority_buttons/go_button.png',
        'claim_button': 'priority_buttons/claim_button.png',
        'recruit_button': 'priority_buttons/recruit_button.png',
        'horse_button': 'priority_buttons/horse_button.png',
        'gem_button': 'priority_buttons/gem_button.png'
    }
    priority_order = ['go_button', 'claim_button',
                      'recruit_button', 'horse_button', 'gem_button']
    excl_point_offset = 75
    exclamation_point_cooldown = 2
    last_exclamation_point_time = 0
    idle_scouting_names = {
        'idle_scout': 'idle_scouting/idle_scout.png',
        'scout_button': 'idle_scouting/scouting_button.png',
        'explore_button': 'idle_scouting/explore_button.png',
        'home_button': 'idle_scouting/home_button.png',
        'scouting_base': 'idle_scouting/scouting_base.png',
        'other_button': 'idle_scouting/other_button.png',
        'visit_button': 'idle_scouting/visit_button.png'
    }

    idle_scout_sequence = [
        (idle_scouting_names['idle_scout'], (0, -30), 5),
        (idle_scouting_names['scout_button'], (0, 0), 3),
        (idle_scouting_names['explore_button'], (0, -50), 1),
        (idle_scouting_names['home_button'], (0, 0), 3),
        (idle_scouting_names['scouting_base'], (0, 0), 1),
        (idle_scouting_names['explore_button'], (0, 0), 1),
        (idle_scouting_names['other_button'], (0, 0), 1),
        (idle_scouting_names['visit_button'], (0, 0), ),
    ]

    print("Starting in 3 seconds. Please switch to the game window.")
    time.sleep(3)
    print("Press 'ESC' key to stop the script.")

    while not is_esc_pressed():
        screen = pyautogui.screenshot()
        screen = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

        # Idle scouting sequence
        image_names, offsets, sleep_times = zip(*idle_scout_sequence)
        find_and_click_sequence(image_names, offsets, sleep_times)

        # Search for and click images based on priority
        if search_and_click_images(image_names, screen, priority_order):
            if is_esc_pressed():  # Check if ESC key pressed after clicking any priority image
                break
            time.sleep(1)
        else:
            print("Could not find any priority images on screen.")

        if time.time() - last_exclamation_point_time >= exclamation_point_cooldown:
            # Replace this with the path to your folder containing the images
            image_folder = "images"
            image_files = get_image_files(image_folder)

            found_exclamation_point = False

            for excl_point_image in image_files:
                coords = find_image_on_screen(excl_point_image, screen)
                if coords:
                    move_and_click(coords[0], coords[1] + excl_point_offset)
                    last_exclamation_point_time = time.time()
                    found_exclamation_point = True
                    break

            if found_exclamation_point:
                time.sleep(1)
            else:
                for image_path in image_files:
                    print(f"Could not find {image_path} on screen.")

        if is_esc_pressed():  # Check if ESC key pressed after the inner loop is done
            break

    print("ESC key pressed. Exiting.")


if __name__ == "__main__":
    main()
