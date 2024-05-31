import yaml
import threading
import argparse
from sr.robot import Simulator, SimRobot

# Argument parser setup
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', type=argparse.FileType('r'), default='games/two_colours_assignment.yaml')
parser.add_argument('robot_scripts', type=argparse.FileType('r'), nargs='*')
args = parser.parse_args()

# Read configuration file
with args.config as f:
    config = yaml.safe_load(f)

# Initialize the simulator
sim = Simulator(config, background=False)

def read_file(fn):
    with open(fn, 'r') as f:
        return f.read()

robot_scripts = args.robot_scripts
prompt = "Enter the names of the Python files to run, separated by commas: "
while not robot_scripts:
    robot_script_names = input(prompt).split(',')
    if robot_script_names == ['']:
        continue
    robot_scripts = [read_file(s.strip()) for s in robot_script_names]

class RobotThread(threading.Thread):
    def __init__(self, zone, script, *args, **kwargs):
        super(RobotThread, self).__init__(*args, **kwargs)
        self.zone = zone
        self.script = script
        self.daemon = True

    def run(self):
        def robot():
            with sim.arena.physics_lock:
                robot_object = SimRobot(sim)
                robot_object.zone = self.zone
                robot_object.location = sim.arena.start_locations[self.zone]
                robot_object.heading = sim.arena.start_headings[self.zone]
                return robot_object

        exec(self.script, {'Robot': robot})

threads = []
for zone, script in enumerate(robot_scripts):
    thread = RobotThread(zone, script)
    thread.start()
    threads.append(thread)

sim.run()

# Warn users if there are still active threads
threads = [t for t in threads if t.is_alive()]
if threads:
    print("WARNING: {0} robot code threads still active.".format(len(threads)))
    print("If you see the above warning and want to kill your robot code, you can press Ctrl+F2 to re-initialize the interpreter and stop the code running.")

