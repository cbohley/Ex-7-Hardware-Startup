import os

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation

from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton
from pidev.Joystick import Joystick

from threading import Thread

import spidev
import os
import RPi.GPIO as GPIO
from pidev.stepper import stepper
from time import sleep
spi = spidev.SpiDev()

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
ADMIN_SCREEN_NAME = 'admin'


class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER


Window.clearcolor = (1, 1, 1, 1)  # White
s0 = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
             steps_per_unit=200, speed=8)


class ImageScreen(Screen):
    def ret(self, widg):
        anim = Animation(size=(400, 400)) + Animation(size=(80, 80))
        anim.start(widg)
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME


ifMotorOn = False
bigBrain = 0
ultraBrain = 0.0


class MainScreen(Screen):
    """
    Class to handle the main screen and its associated touch events
    """

    def runMotor(self):
        global ifMotorOn
        global bigBrain
        if ifMotorOn == True:
            s0.stop()
            s0.free()
            ifMotorOn = False
        # runMotor just simply runs the motor if it is ready to go
        else:
            s0.run(bigBrain, self.ids.slider.value * 5)
            ifMotorOn = True

    def changeDirection(self):
        global ifMotorOn
        global bigBrain
        if ifMotorOn:
            if bigBrain == 0:
                bigBrain = 1
                s0.run(bigBrain, self.ids.slider.value * 5)
            else:
                bigBrain = 0
                s0.run(bigBrain, self.ids.slider.value * 5)

    def sliderMotorSpeed(self):
        global ultraBrain
        global ifMotorOn
        global bigBrain
        if ifMotorOn:
            s0.run(bigBrain, self.ids.slider.value * 5)

    def joy_update(self):
        while True:
            joy_x_val = jstick.get_axis('x')
            button_state = str(jstick.get_button_state(0))
            if jstick.get_button_state(i) == 1:
                all_buttons_state = True
                break
            self.ids.all_butts_label.text = str(all_buttons_state)
            self.ids.joystick_label.text = button_state
            self.ids.joy_pos_label.center_y = self.height * -0.5 * (joy_y_val - 1)
            self.ids.coords.text = "{:.3f} {:.3f}".format(jstick.get_axis('x'), jstick.get_axis('y'))
            sleep(.1)

    # def start_joy_thread(self):
    #    Thread(target=self.joy_update).start()

    def switch(self, curr):
        if curr == "on":
            return "off"
        else:
            return "on"

    def count(self, c):
        c_n = int(c) + 1
        return str(c_n)

    def motor_switch(self, c):
        if c == "motor on":
            return "motor off"
        else:
            return "motor on"

    def pressed(self):
        """return
        Function called on button touch event for button with id: testButton
        :return: None
        """
        PauseScreen.pause(pause_scene_name='pauseScene', transition_back_scene='main', text="Test", pause_duration=5)

    def bestFunction(self):

        s0.set_speed(1)
        s0.relative_move(-15)
        s0.stop()
        sleep(10)
        s0.set_speed(5)
        s0.relative_move(-10)

    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'

    def exit(self, widg):
        anim = Animation(size=(600, 200)) + Animation(size=(300, 100))
        anim.start(widg)
        SCREEN_MANAGER.current = 'exit'



class AdminScreen(Screen):
    """80, 80))
        anim.start(widg)
    Class to handle the AdminScreen and its functionality
    """

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(
            ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(
            MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        s0.free_all()
        spi.close()
        GPIO.cleanup()
        quit()


"""
Widget additions
"""

Builder.load_file('main.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(ImageScreen(name='exit'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))

"""
MixPanel
"""


def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    ProjectNameGUI().run()
