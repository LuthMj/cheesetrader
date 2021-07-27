import os
import toml
import threading
import subprocess

import MetaTrader5 as mt5

from PIL import Image, ImageDraw
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

from api import metatrader5 as mt

config_file = 'config.toml'
config_data = toml.load(config_file)

def render_key_image(deck, icon_filename):
    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
    icon = Image.open(icon_filename)
    image = PILHelper.create_scaled_image(deck, icon, margins=[0, 0, 0, 0])

    # Load a custom TrueType font and use it to overlay the key index, draw key
    # label onto the image a few pixels from the bottom of the key.
    draw = ImageDraw.Draw(image)
    draw.text((image.width / 2, image.height - 5),
              text="", anchor="ms", fill="white")

    return PILHelper.to_native_format(deck, image)


def get_key_style(deck, key, state):
    image = config_data['buttonConfig']['button' + str(key + 1)]['imagePath']
    try:
        return {
            "name": config_data['buttonConfig']['button' + str(key + 1)],
            "icon": os.path.abspath(
                os.getcwd()) + '/assets/' + image,
        }
    except Exception:
        print("No Image Found")


def update_key_image(deck, key, state):
    # Determine what icon and label to use on the generated key.
    key_style = get_key_style(deck, key, state)

    # Generate the custom key with the requested image and label.
    image = render_key_image(deck, key_style["icon"])

    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(key, image)


def key_change_callback(deck, key, state):
    # Print new key state
    print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)

    if state:
        if (config_data['buttonConfig']['button' + str(key + 1)]['action'] == "exit"):
            with deck:
                mt5.shutdown()
                deck.reset()
                deck.close()
        elif(
            config_data['buttonConfig']['button' + str(key + 1)]['action'] == 'buy') or (config_data['buttonConfig']['button' + str(key + 1)]['action'] == 'sell'):
                # Symbol configuration. Button specific configuration precedes
                if 'symbol' in config_data['buttonConfig']['button' + str(key + 1)]:
                    if config_data['buttonConfig']['button' + str(key + 1)]['symbol']:
                        symbol = config_data['buttonConfig']['button' + str(key + 1)]['symbol']
                    else:
                        print("The symbol entry exists however it doesn't contain a value, so we try the metatraderConfig symbol")
                        if 'symbol' in config_data['metatraderConfig']:
                            symbol = config_data['metatraderConfig']['symbol']
                            print("Symbol is set to: {}".format(symbol))
                        else:
                            print("No symbol defined in your config.toml file in either the section metatraderConfig or in the button config.")
                            return
                # Symbol configuration. Global symbol config.
                elif 'symbol' in config_data['metatraderConfig']:
                    symbol = config_data['metatraderConfig']['symbol']
                else:
                    print("No symbol defined in your config.toml file in either the section metatraderConfig or in the button config.")
                    return
                if 'lotSize' in config_data['buttonConfig']['button' + str(key + 1)]:
                    lot_size = config_data['buttonConfig']['button' + str(key + 1)]['lotSize']
                else:
                    print("No lotSize Defined in your config.toml file")
                    return
                mt.open_position(
                    symbol,
                    config_data['buttonConfig']['button' + str(key + 1)]['action'],
                    lot_size
                    )
        elif(config_data['buttonConfig']['button' + str(key + 1)]['action'] == "closeall"):
            mt.close_all_positions()
        elif(config_data['buttonConfig']['button' + str(key + 1)]['action'] == ""):
            print("No Action Defined")
        elif(config_data['buttonConfig']['button' + str(key + 1)]['action'] == 'cmd'):
            if config_data['buttonConfig']['button' + str(key + 1)]['command']:
                subprocess.Popen(config_data['buttonConfig']['button' + str(key + 1)]['command'], shell=True)
            else:
                print("The command entry exists however it doesn't contain a value.")


def streamdeck():
    streamdecks = DeviceManager().enumerate()

    print("\nFound {} Stream Deck(s).".format(len(streamdecks)))

    for index, deck in enumerate(streamdecks):
        deck.open()
        deck.reset()

        print("\nOpened '{}' device (serial number: '{}')".format(
            deck.deck_type(), deck.get_serial_number()))

        # Set initial screen brightness to 100%.
        deck.set_brightness(config_data['mainConfig']['brightness'])

        # Set initial key images.
        for key in range(deck.key_count()):
            update_key_image(deck, key, False)

        # Register callback function for when a key state changes.
        deck.set_key_callback(key_change_callback)

        # Wait until all application threads have terminated (for this example,
        # this is when all deck handles are closed).
        for t in threading.enumerate():
            if t is threading.currentThread():
                continue

            if t.is_alive():
                t.join()
