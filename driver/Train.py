# -*- coding: utf-8 -*-
import time
import torch.optim as optim
import torch.nn.functional as F
from driver.DataLoader import *


def train(model, train_data, dev_data, test_data, vocab_srcs, vocab_tgts, config):
    model.train()
    # optimizer
    parameters = filter(lambda p: p.requires_grad, model.parameters())
    if config.learning_algorithm == 'sgd':
        optimizer = optim.SGD(parameters, lr=config.lr, weight_decay=config.weight_decay)

    elif config.learning_algorithm == 'adagrad':
        optimizer = optim.Adagrad(parameters, lr=config.lr, weight_decay=config.weight_decay)

    elif config.learning_algorithm == 'adadelta':
        optimizer = optim.Adadelta(parameters, lr=config.lr, weight_decay=config.weight_decay)

    elif config.learning_algorithm == 'adam':
        optimizer = optim.Adam(parameters, lr=config.lr, weight_decay=config.weight_decay)
    else:
        raise RuntimeError("Invalid optim method: " + config.learning_algorithm)

    # train
    global_step = 0
    best_f1 = 0
    print('\nstart training...')
    for iter in range(config.epochs):
        iter_start_time = time.time()
        print('Iteration: ' + str(iter))

        batch_num = int(np.ceil(len(train_data) / float(config.batch_size)))
        batch_iter = 0
        for batch in create_batch_iter(train_data, config.batch_size, shuffle=True):
            start_time = time.time()
            feature, target, feature_lengths = pair_data_variable(batch, vocab_srcs, vocab_tgts, config)

            optimizer.zero_grad()
            logit = model(feature, feature_lengths)
            loss = F.cross_entropy(logit, target)
            loss_value = loss.data.cpu().numpy()
            loss.backward()
            optimizer.step()

            correct = (torch.max(logit, 1)[1].view(target.size()).data == target.data).sum()
            accuracy = 100.0 * correct / len(batch)

            during_time = float(time.time() - start_time)
            print("Step:{}, Iter:{}, batch:{}, accuracy:{:.4f}({}/{}), time:{:.2f}, loss:{:.6f}"
                  .format(global_step, iter, batch_iter, accuracy, correct, len(batch), during_time, loss_value[0]))

            batch_iter += 1
            global_step += 1

            if batch_iter % config.test_interval == 0 or batch_iter == batch_num:
                dev_acc = evaluate(model, dev_data, global_step, vocab_srcs, vocab_tgts, config)
                test_acc = evaluate(model, test_data, global_step, vocab_srcs, vocab_tgts, config)

                if dev_acc > best_acc:
                    print("Exceed best acc: history = %.2f, current = %.2f" % (best_acc, dev_acc))
                    best_acc = dev_acc
                    if config.save_after > 0 and iter > config.save_after:
                        torch.save(model.state_dict(), config.save_model_path + '.' + str(global_step))
        during_time = float(time.time() - iter_start_time)
        print('one iter using time: time:{:.2f}'.format(during_time))


def evaluate(model, data, step, vocab_srcs, vocab_tgts, config):
    model.eval()
    start_time = time.time()
    corrects, size = 0, 0

    for batch in create_batch_iter(data, config.batch_size):
        feature, label, feature_lengths = pair_data_variable(batch,
                                    vocab_srcs, vocab_tgts, config)
        logit = model(feature, feature_lengths)
        correct = (torch.max(logit, 1)[1].view(label.size()).data == label.data).sum()
        corrects += correct
        size += len(batch)
    accuracy = 100.0 * corrects / size
    during_time = float(time.time() - start_time)
    print("\nevaluate result: ")
    print("Step:{}, accuracy:{:.4f}({}/{}), time:{:.2f}"
          .format(step, accuracy, corrects, size, during_time))
    model.train()
    return accuracy