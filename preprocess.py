# -*- coding: utf-8 -*-
import random
import argparse
from driver.Config import Configurable
from driver.IO import *
from driver.Vocab import *


def analysis(sentence_length, feature_dict=None, label_set=None):

    if feature_dict is not None:
        print('单词个数为: ', len(feature_dict))
    if label_set is not None:
        print('标签有: ')
        for i in label_set:
            print(i)


if __name__ == '__main__':
    # random
    random.seed(666)
    np.random.seed(666)

    # parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', default='default.ini', type=str)
    parser.add_argument('--thread', default=1, type=int)
    args, extra_args = parser.parse_known_args()
    config = Configurable(args.config_file, extra_args)

    # data and analysis
    print('\n')
    train_data, train_sentence_len, feature_dict, label_set = read_word_line(
        config.train_file, is_train=True)
    analysis(train_sentence_len, feature_dict, label_set)
    # dev_data, dev_sentence_len = read_word_line(config.dev_file)
    # analysis(train_sentence_len)
    test_data, test_sentence_len = read_word_line(config.test_file)
    analysis(train_sentence_len)

    pickle.dump(train_data, open(config.train_pkl, 'wb'))
    # pickle.dump(dev_data, open(config.dev_pkl, 'wb'))
    pickle.dump(test_data, open(config.test_pkl, 'wb'))

    # vocab
    feature_list = [ite for ite, it in feature_dict.most_common(config.vocab_size)]
    feature_voc = VocabSrc(feature_list)
    label_voc = VocabTgt(label_set)
    pickle.dump(feature_voc, open(config.save_feature_voc, 'wb'))
    pickle.dump(label_voc, open(config.save_label_voc, 'wb'))

    # embedding
    embedding = feature_voc.create_vocab_embs(config.embedding_file)
    pickle.dump(embedding, open(config.embedding_pkl, 'wb'))



















