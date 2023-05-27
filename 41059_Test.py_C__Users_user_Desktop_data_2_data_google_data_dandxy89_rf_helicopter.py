# Purpose: Main Function - Post Training showing Results
#
#   Info: Change the Parameters at the top of the scrip to change how the Agent interacts
#
#   Developed as part of the Software Agents Course at City University
#
#   Dev: Dan Dixey and Enrico Lopedoto
#
#   Updated: 1/3/2016
#
import logging
from time import time

import numpy as np

import matplotlib
import matplotlib.pyplot as plt

from Model import World as W
from Model.Helicopter import helicopter
from Settings import *

matplotlib.style.use('ggplot')


# Logging Controls Level of Printing
logging.basicConfig(format='[%(asctime)s] : [%(levelname)s] : [%(message)s]',
                    level=logging.INFO)


# Model Setting
case = 'case_five'
settings_ = case_lookup[case]
iterations, settings = get_indicies(settings_)

# Plot Settings
plot_settings = dict(print_up_to=-1,
                     end_range=list(range(30,
                                          60)),
                     print_rate=5)

# Training Track=Track1.npy
# Testing Track=Track_Wind_3.npy
HeliWorld = W.helicopter_world(file_name="Track_1.npy")
# file_name=None - Loads a Randomly Generated Track
Helicopter1 = helicopter(world=HeliWorld,
                         settings=settings)

value_iter, model = 0, settings['model']
name = 'model_{}_case_{}_iter_{}'.format(
    settings['model'],
    case.split('_')[1],
    value_iter)
Helicopter1.ai.load_model(name=name)

if settings['model'] == 3:
    Helicopter1.ai.update_rate = 10000000

settings['trials'] = 60
Helicopter1.ai.epsilon = 0
Helicopter1.ai.train = False

a = np.zeros(shape=(HeliWorld.track_height,
                    HeliWorld.track_width))

st = time()
time_metrics = []
b_array = []

results = dict(paths=[[],
                      [],
                      [],
                      [],
                      [],
                      [],
                      [],
                      [],
                      [],
                      []])
path = []

logging.info('Dealing with Case: {}'.format(case))
for value_iter in range(iterations):

    if value_iter > 0:
        settings = get_settings(dictionary=settings_,
                                ind=value_iter)
        HeliWorld = W.helicopter_world(file_name="Track_Wind_3.npy")
        # HeliWorld = W.helicopter_world(file_name="Track_1.npy")
        Helicopter1 = helicopter(world=HeliWorld,
                                 settings=settings)
        a = np.zeros(shape=(HeliWorld.track_height,
                            HeliWorld.track_width))
        name = 'model_{}_case_{}_iter_{}'.format(
            settings['model'],
            case.split('_')[1],
            value_iter)
        Helicopter1.ai.load_model(name=name)

        if settings['model'] == 3:
            Helicopter1.ai.update_rate = 10000000

        settings['trials'] = 60
        Helicopter1.ai.epsilon = 0
        Helicopter1.ai.train = False
        logging.info('Changing Values: {}'.format(settings_['change_values']))

    while HeliWorld.trials <= settings['trials']:
        # On the Last Trail give the Model full control
        if HeliWorld.trials == settings['trials']:
            Helicopter1.ai.epsilon, settings['epsilon'] = 1e-9, 1e-9

        # Print out logging metrics
        if HeliWorld.trials % plot_settings[
                'print_rate'] == 0 and HeliWorld.trials > 0:
            rate = ((time() - st + 0.01) / HeliWorld.trials)
            value = [HeliWorld.trials, rate]
            time_metrics.append(value)
            logging.info(
                "Trials Completed: {} at {:.4f} seconds / trial".format(value[0], value[1]))

        # Inner loop of episodes
        while True:
            output = Helicopter1.update()

            if HeliWorld.trials == settings['trials']:
                b_array.append(Helicopter1.current_location)

            if not output:
                Helicopter1.reset()
                rate = (time() - st + 0.01) / HeliWorld.trials
                value = [HeliWorld.trials,
                         rate]

                if HeliWorld.trials <= plot_settings[
                        'print_up_to'] or HeliWorld.trials in plot_settings['end_range']:
                    results['paths'][value_iter].append(path)
                    path = []

                break

            if HeliWorld.trials <= plot_settings[
                    'print_up_to'] or HeliWorld.trials in plot_settings['end_range']:
                # Primary Title
                rate = (time() - st + 0.01) / HeliWorld.trials
                value = [HeliWorld.trials,
                         rate]
                path.append(Helicopter1.current_location)

            # Update the Q Plot of the Track
            try:
                pos, array_masked = Helicopter1.return_q_view()
                a[:, pos - 1] += array_masked
            except:
                pass

        HeliWorld.trials += 1
    et = time()
    logging.info(
        "Time Taken: {} seconds for Iteration {}".format(
            et - st, value_iter + 1))

mean_values = []
std_values = []

# For each Model in Case
for value_iter in range(iterations):
    sub_set = []

    for path in results['paths'][value_iter]:
        sub_set.append((path[-1][0] / float(HeliWorld.track_width)))

    mean_values.append(np.mean(sub_set))
    std_values.append(np.std(sub_set))

labels = [str(value) for value in np.arange(iterations) + 1]
paired_sorted = sorted(zip(mean_values, std_values, labels),
                       key=lambda x: (-x[0]))
mean_values, std_values, labels = zip(*paired_sorted)

fig, ax = plt.subplots()
plt.title(
    'Completion by each Model in {} - Data Label = Mean Final Location'.format(
        case.title()),
    fontsize=10)
plt.xlabel('Case Model (ordered by Mean location)', fontsize=8)
plt.ylabel('Completion of Track (Std) %', fontsize=8)
index = np.arange(iterations)
bar_width = 0.5
opacity = 0.4
error_config = {'ecolor': '0.3'}
out = plt.bar(index, mean_values, bar_width,
              alpha=opacity,
              color='b',
              yerr=std_values,
              error_kw=error_config,
              label='Case Model')

plt.xticks(index + bar_width / 2, labels)
plt.ylim(0, 1.1)
plt.tight_layout()


def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2., 1.08 * height,
                '{:.3f}'.format(float(height)),
                ha='center', va='bottom')

autolabel(out)
directory = os.path.join(os.getcwd(), 'Results', case)
plt.savefig(directory + '/TEST_Results_Model_{}.png'.format(model))
