import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable
import math


def experiment(input_data):

    output_data = Variable(
        -(torch.sin(input_data[:, 0] - 2)
          * torch.cos(input_data[:, 1] - 0.3)
          * (1. / (torch.abs(input_data[:, 2] - 0.5) + 1))
          * (1. / (torch.abs(input_data[:, 3] - 0.1) + 1))
          * (1. / (torch.abs(input_data[:, 4] - 0.3) + 1))
          ),
        requires_grad=False)

    #print (calc)
    # print(input_data)
    # print(output_data)
    return output_data


def main():
    # model info
    # 给generator的噪音维数
    n_noise_dim = 10
    # 真实数据的维度
    n_real_data_dim = 5
    g_net = nn.Sequential(
        nn.Linear(n_noise_dim, 128),
        nn.LeakyReLU(0.01),
        nn.Linear(128, 128),
        nn.LeakyReLU(0.01),
        nn.Linear(128, n_real_data_dim),
        nn.Sigmoid(),
        nn.ReLU()
    ).cuda()
    d_net = nn.Sequential(
        nn.Linear(n_real_data_dim, 256),
        nn.LeakyReLU(0.01),
        nn.Linear(256, 128),
        nn.LeakyReLU(0.01),
        nn.Linear(128, 1),
        nn.Sigmoid()
    ).cuda()
    lr_g = 0.008
    lr_d = 0.003
    opt_d = torch.optim.Adam(d_net.parameters(), lr=lr_d)
    #opt_g =torch.optim.Adam(g_net.parameters(), lr=lr_g)
    opt_g = torch.optim.SGD(g_net.parameters(), lr=lr_g, momentum=0.1)
    #

    batch_size = 50
    epochs = 1000000

    for epoch in range(epochs):
        # 用G产生一堆实验参数
        batch_noise = Variable(torch.randn(batch_size, n_noise_dim).cuda())
        g_data = g_net(batch_noise)
        # 用G的实验参数做实验
        prob_real = experiment(g_data.data)
        prob_fake = d_net(g_data)

        if (epoch % 100 == 1):
            print(g_data.data[0])
            print(prob_real[0])
        # D和真实情况越像越好

        d_loss = nn.L1Loss(size_average=True, reduce=True)(
            prob_fake, prob_real)
        # 训练D
        opt_d.zero_grad()

        d_loss.backward(retain_variables=True)
        opt_d.step()
        # G越高越好
        g_goodness = -torch.max(prob_real)
        g_loss = -torch.mean(prob_fake)
        # 训练G
        opt_g.zero_grad()
        g_loss.backward(retain_variables=True)
        opt_g.step()
        if (epoch % 100 == 1):
            print('Run: {} minutes, d_loss: {}, g_loss: {}, g_good: {}'.format(int(epoch * batch_size / 100 / 60), d_loss.data.cpu().numpy()[0],
                                                                               g_loss.data.cpu().numpy()[
                0],
                g_goodness.data.cpu().numpy()[
                0]
            ))


if __name__ == '__main__':
    main()
