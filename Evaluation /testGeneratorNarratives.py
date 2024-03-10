import pandas as pd
import random
from os import listdir
import os
from os.path import isfile, isdir, join
import string
import json

def get_filenames(path, outlier_file_start):
    # get all filenames in folder
    filenames = [f for f in listdir(path) if isfile(join(path, f))]
    # delete those starting with outlier file name indicator
    filenames = [f for f in filenames if not f.startswith(outlier_file_start)]
    filenames = [path + '/' + f for f in filenames]
    return filenames

def get_foldernames(path):
    # get all foldernames in folder
    foldernames = [f for f in listdir(path) if isdir(join(path, f))]
    foldernames = [path + '/' + f for f in foldernames]
    return foldernames

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

def get_narrative_length(file_name):
    df = pd.read_csv(file_name)
    return len(df)

def get_random_name(length=15):
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_test_sets (domain_name, filenames, use_all_topics = False, no_test_sets = 20):
    test_sets_folder_name = domain_name + '_narrative_testSets'

    remaining_filenames = filenames.copy()

    if use_all_topics:
        no_test_sets = len(filenames)

    i = 0

    while i < no_test_sets:

        # randomly choose correct file name
        iteration_filenames = remaining_filenames.copy()
        correct_file_name = iteration_filenames[random.randint(0, len(iteration_filenames)-1)]

        # remove correct file name -> assuming that each file name is unique
        iteration_filenames.remove(correct_file_name)

        # pick intruder file name randomly from all filenames, except the correct filename
        intruder_file_name = correct_file_name
        while (intruder_file_name == correct_file_name):
            intruder_file_name = filenames[random.randint(0, len(filenames) - 1)]

        # remove correct file name for subsequent iterations so that each narrative is tested only once
        remaining_filenames.remove(correct_file_name)

        if get_narrative_length(correct_file_name) < 2:
            # narratives of length are skipped
            continue
        elif get_narrative_length(correct_file_name) < 5:
            # length between 2 and 5: only that many correct claims can be selected
            correct_claims = get_random_claims(correct_file_name, get_narrative_length(correct_file_name))
        else:
            correct_claims = get_random_claims(correct_file_name, 5)

        intruder_claims = get_random_claims(intruder_file_name, 1)

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

        with open(test_sets_folder_name + '/' + test_set_name + '.json', 'w') as fp:
            # add testset as own file
            json.dump(test_set_dict, fp)


        test_control_json_name = domain_name + '_testControl.json'
        with open(test_sets_folder_name + '/' + test_control_json_name, 'r+') as fp:
            # add id of new testset to testControl file
            test_control_data = json.load(fp)
            test_sets = test_control_data['unseen_test_sets']
            test_sets.append(test_set_name)
            test_control_data['unseen_test_sets'] = test_sets
            fp.seek(0)
            json.dump(test_control_data, fp)

        i += 1

    return

def create_testControl_json(domain_name):
    test_sets_folder_name = domain_name + '_narrative_testSets'
    test_control_dict = {'unseen_test_sets': [], 'seen_test_sets': [], 'results': []}
    test_control_json_name = domain_name + '_testControl.json'
    with open(test_sets_folder_name + '/' + test_control_json_name, 'w') as fp:
        json.dump(test_control_dict, fp)

if __name__ == '__main__':
    print('Hi, testGenerator')

    # Possible Improvement: implement some check that each file contains at least 5 claims

    # replace and uncomment path_to_dataset_folder
    path_to_dataset_folder = r"C:\Users\sebbo\COVID\COVID\BERTopic_run_1\Narratives Results"

    outlier_file_start = '-1'

    # note: based on windows os naming conventions. probably doesn't run on other os
    domain_name = path_to_dataset_folder.split('\\')[-1]

    # make new folder for test sets
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, domain_name + '_narrative_testSets')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    else:
        # exit if folder already exists to ensure there a no test sets append which are not tracked in testControl.json
        print('folder already exists: ', final_directory)
        exit()

    # decide whether to evaluate narratives that all belong to one topic, or narratives coming from different topics
    single_topic = False

    no_test_sets = 25

    create_testControl_json(domain_name)

    if single_topic:
        # single topic -> path_to_dataset_folder points to a folder with a csv for each narrative within one topic

        filenames = get_filenames(path_to_dataset_folder, outlier_file_start)

        generate_test_sets(domain_name, filenames, no_test_sets=no_test_sets)

    else:
        # multiple topics -> path_to_dataset_folder points to a folder with subfolder for each topic within one context
        foldernames = get_foldernames(path_to_dataset_folder)
        print(foldernames)

        selected_foldernames = random.sample(foldernames, no_test_sets)

        # for simplicity choose no_test_sets folder and generate only one testset per topic
        for fn in selected_foldernames:
            filenames = get_filenames(fn, 'something')

            generate_test_sets(domain_name, filenames, no_test_sets=1)




    exit()