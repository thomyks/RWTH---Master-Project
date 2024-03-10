import pandas as pd
import random
from os import listdir
import os
from os.path import isfile, join
import string
import json

def get_filenames (path, non_relevant_filenames):
    # get all filenames in folder
    filenames = [f for f in listdir(path) if isfile(join(path, f))]

    # delete those starting with outlier file name indicator
    filenames = [f for f in filenames if not f in non_relevant_filenames]

    filenames = [path + '/' + f for f in filenames]
    return filenames

def get_random_claims(file_name, number):
    df = pd.read_csv(file_name)
    claims = df.text
    len_df = len(df)
    selected_claims = []
    already_selected_idx = []
    for i in range(number):
        e = random.randint(0, len_df - 1)
        # generate new random index if index already present
        while e in already_selected_idx:
            e = random.randint(0, len_df - 1)
        already_selected_idx.append(e)
        selected_claim = claims[e]
        selected_claims.append(selected_claim)
    return selected_claims

def get_random_name(length=15):
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_test_sets (domain_name, filenames, use_all_topics = False, no_test_sets = 25):
    # set use_all_topics to false and specify no_test_sets if not one testset per topic is wanted

    test_set_names = []
    test_sets_folder_name = domain_name + '_testSets'

    remaining_filenames = filenames.copy()

    if use_all_topics:
        no_test_sets = len(filenames)


    for i in range(no_test_sets):

        # randomly choose correct file name
        iteration_filenames = remaining_filenames.copy()
        correct_file_name = iteration_filenames[random.randint(0, len(iteration_filenames)-1)]

        # remove correct file name -> assuming that each file name is unique
        iteration_filenames.remove(correct_file_name)

        # pick intruder file name randomly from all filenames, except the correct filename
        intruder_file_name = correct_file_name
        while (intruder_file_name == correct_file_name):
            intruder_file_name = filenames[random.randint(0, len(filenames)-1)]

        correct_claims = get_random_claims(correct_file_name, 5)
        intruder_claims = get_random_claims(intruder_file_name, 1)

        # remove correct file name for subsequent iterations so that each narrative is tested only once
        remaining_filenames.remove(correct_file_name)

        test_set_dict = {'correct_claims': correct_claims,
                         'intruder_claims': intruder_claims,
                         'correct_file_name': correct_file_name,
                         'intruder_file_name': intruder_file_name}

        all_claims = correct_claims + intruder_claims
        random.shuffle(all_claims)

        test_set_dict['shuffled_claims'] = all_claims

        # get intruder index by search for text of intruder claim -> assuming that each claim text is unique
        intruder_index = all_claims.index(intruder_claims[0])
        correct_indices = list(filter(lambda idx: idx != intruder_index, range(len(all_claims))))

        test_set_dict['intruder_index'] = intruder_index
        test_set_dict['correct_indices'] = correct_indices

        test_set_id = get_random_name()
        test_set_name = '_'.join([domain_name, 'testSet', test_set_id])
        test_set_names.append(test_set_name)

        with open(test_sets_folder_name + '/' + test_set_name + '.json', 'w') as fp:
            json.dump(test_set_dict, fp)

    test_control_dict = {'unseen_test_sets': test_set_names, 'seen_test_sets': [], 'results': []}

    test_control_json_name = domain_name + '_testControl.json'
    with open(test_sets_folder_name + '/' + test_control_json_name, 'w') as fp:
        json.dump(test_control_dict, fp)

    return


if __name__ == '__main__':
    print('Hi, testGenerator')

    # Possible Improvement: implement some check that each file contains at least 5 claims

    # replace and uncomment path_to_dataset_folder
    path_to_dataset_folder = r'C:\Users\sebbo\COVID\COVID\BERTopic_run_1'

    # replace, add or remove non relevant filenames if neccessary
    non_relevant_filenames = ['BERTopic_run_1_Outliers.csv', 'BERTopic_run_1_TopicLabels.csv', 'BERTopic_run_1_TopicNames.npy', 'BERTopic_run_1_Topics_Results.csv']

    # note: based on windows os naming conventions. probably doesn't run on other os
    domain_name = path_to_dataset_folder.split('\\')[-1]

    # make new folder for test sets
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, domain_name + '_testSets')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    else:
        # exit if folder already exists to ensure there a no test sets append which are not tracked in testControl.json
        print('folder already exists: ', final_directory)
        exit()

    filenames = get_filenames(path_to_dataset_folder, non_relevant_filenames)

    generate_test_sets(domain_name, filenames)

    exit()