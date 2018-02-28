import scipy.cluster.vq
import feedback
import numpy as np
from tensorboardX import SummaryWriter


def learn(features, power, classes=20):
    whitened = scipy.cluster.vq.whiten(features)
    #book = array((whitened[0], whitened[2]))
    clustered = scipy.cluster.vq.kmeans2(
        whitened, classes, iter=25, minit="points")[1]
    print(clustered)
    num_classes = np.zeros(classes)
    avg_classes = np.zeros(classes)
    for i in range(len(clustered)):
        num_classes[clustered[i]] += 1
        avg_classes[clustered[i]] += power[i]
    avg_classes = avg_classes / num_classes
    print(avg_classes)
    evaluate = np.zeros(len(clustered))
    for i in range(len(clustered)):
        evaluate[i] = np.abs(power[i] - avg_classes[clustered[i]])
    print(np.mean(evaluate))
    print(num_classes)


if __name__ == '__main__':
    # tensorboard
    writer = SummaryWriter()
    print("load_experiment_record...")
    # 读取实验结果
    x, power = feedback.load_experiment_record(sample_rate=25, trunc=None)
    data_tensor = np.array(x)
    target_tensor = np.array(power)
    learn(data_tensor, power=target_tensor)
