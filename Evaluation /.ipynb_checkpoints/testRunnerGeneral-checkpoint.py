import os
import json

if __name__ == '__main__':
    print('Hi, testrunner')

    current_directory = os.getcwd()

    narrative_mode_input = input('Please type "n" if you are here to evaluate narratives, if not, type anything different: ')
    narrative_mode = narrative_mode_input == 'n'

    mac_mode_input = input('Please type "m" if you are on a mac, if not, type anything different: ')
    mac_mode = mac_mode_input == 'm'

    suffix = '_narrative_testSets' if narrative_mode else '_testSets'

    json_file_name = ''
    # Possible improvement: adapt so that name of folder can be changed or at least expanded at the end

    # note: file name operations might not work on linux
    if mac_mode:
        json_file_name = os.path.join(current_directory, current_directory.split('/')[-1][:-len(suffix)] + '_testControl.json')
    else:
        json_file_name = os.path.join(current_directory, current_directory.split('\\')[-1][:-len(suffix)] + '_testControl.json')

    print(current_directory, current_directory.split('\\'), suffix)
    print('fn', json_file_name)
    with open(json_file_name, 'r') as fp:
        control_info = json.load(fp)

    unseen_test_sets = control_info['unseen_test_sets']
    if not unseen_test_sets:
        print('You already answered all test sets! Thank you :)')
        exit()

    name = input('Please enter your alias: ')

    seen_test_sets = control_info['seen_test_sets']
    results = control_info['results']

    new_unseen_test_sets = unseen_test_sets.copy()
    new_seen_test_sets = seen_test_sets.copy()

    # iteratively present test set to user
    for i in range(len(unseen_test_sets)):
        current_ts = unseen_test_sets[i]
        with open(current_ts + '.json') as fp:
            test_set = json.load(fp)
            shuffled_claims = test_set['shuffled_claims']
            actual_intruder_index = test_set['intruder_index']
            correct_indices = test_set['correct_indices']

        for i in range(len(shuffled_claims)):
            print(i, '  ', shuffled_claims[i])

        selected_intruder_index = input('Please type the number of the claim which fits the least into the group: ')

        result = {'test_set_name': current_ts,
                  'selected_intruder_index': selected_intruder_index,
                  'actual_intruder_index': actual_intruder_index,
                  'user_name': name}

        new_unseen_test_sets.remove(current_ts)

        new_seen_test_sets.append(current_ts)

        results.append(result)

        new_json = {'results': results,
                    'seen_test_sets': new_seen_test_sets,
                    'unseen_test_sets': new_unseen_test_sets}

        with open(json_file_name, 'w') as fp:
            json.dump(new_json, fp)

    print('That were all test sets! Thank you a lot for your input! :))')
    exit()