import preprocessing

fortnox = {'Authorization-Code': '',
           'Client-Secret': ''}

preprocessing_queue = [preprocessing.scale_and_center,
                       preprocessing.dot_reduction,
                       preprocessing.connect_lines]
use_anonymous = True

