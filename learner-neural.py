import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.utils.data

import feedback
from tensorboardX import SummaryWriter

gpu = torch.cuda.is_available()


class VariableSizeInspector(nn.Module):
    def __init__(self):
        super(VariableSizeInspector, self).__init__()

    def forward(self, x):
        # print('after' , x.size())
        return x

    def __repr__(self):
        return 'VariableSizeInspector()'


class FeatureFlaten(nn.Module):
    def __init__(self):
        super(FeatureFlaten, self).__init__()

    def forward(self, x):
        x = x.view(-1, self.num_flat_features(x))
        return x

    def num_flat_features(self, x):
        size = x.size()[1:]  # all dimensions except the batch dimension
        num_features = 1
        for s in size:
            num_features *= s
        return num_features

    def __repr__(self):
        return 'FeatureFlaten()'


def Discriminator(n_acturators_dim, zernike_modes):
    d_net = nn.Sequential(
        nn.ConvTranspose2d(n_acturators_dim, zernike_modes, 10),
        VariableSizeInspector(),
        nn.ReLU(),
        nn.ConvTranspose2d(zernike_modes, 256, 6),
        VariableSizeInspector(),
        nn.ReLU(),
        nn.Conv2d(256, 32, 1),  # mixing layer
        VariableSizeInspector(),
        nn.ReLU(),
        nn.Conv2d(32, 128, 3),
        VariableSizeInspector(),
        nn.ReLU(),
        VariableSizeInspector(),
        nn.Conv2d(128, 64, 3),
        VariableSizeInspector(),
        nn.ReLU(),
        FeatureFlaten(),
        nn.Linear(11 * 11 * 64, 512),
        VariableSizeInspector(),
        nn.ReLU(),
        nn.Dropout(),
        nn.Linear(512, 512),
        nn.Linear(512, 1),
        nn.LeakyReLU(0.01)
    )
    if gpu:
            #g_net = g_net.cuda()
        d_net = d_net.cuda()
    return d_net


if __name__ == '__main__':
    # tensorboard
    writer = SummaryWriter()

    # 开启反馈环
    feedback_loop = feedback.please_just_give_me_a_simple_loop("Memory")
    #feedback = feedback.feedback_loop(None, None)

    def load_experiment_record():
        print("load_experiment_record...")
        # 读取实验结果
        x, power = feedback.load_experiment_record(sample_rate=100, trunc=None)
        data_tensor = torch.FloatTensor(x) * 2.0 - 1.0  # 还原执行器最大最小值
        target_tensor = torch.FloatTensor(power)
        #torch.tanh(torch.FloatTensor(power) / (20.0 * 1000.0) - 0.3)
        if gpu:
            data_tensor = data_tensor.cuda()
            target_tensor = target_tensor.cuda()
        dataset = torch.utils.data.TensorDataset(data_tensor, target_tensor)
        print("okay.")
        return dataset

    def experiment(input_data):
        output_data = []
        for each in input_data:
            percent = feedback_loop.f((each + 1.0) / 2.0, record=False)
            # print(percent)
            output_data.append([percent])
        powersource = torch.FloatTensor(output_data)
        #torch.tanh(torch.FloatTensor(output_data) / (20.0 * 1000.0) - 0.3)
        if gpu:
            powersource = powersource.cuda()
        return Variable(powersource)

    # model info
    # 给generator的噪音维数
    """
    n_noise_dim = 10
    # 真实数据的维度

    g_net = nn.Sequential(
        nn.Linear(n_noise_dim, 128),
        nn.ReLU(),
        nn.Linear(128, 256),
        nn.ReLU(),
        nn.Linear(256, 256),
        nn.ReLU(),
        nn.Linear(256, n_acturators_dim),
        nn.Tanh()
    )
    """
    # create a neural network
    if input("retarin? ") == "yes":
        d_net = Discriminator(
            n_acturators_dim=feedback_loop.vchn_num, zernike_modes=128)
        print("previous parameters are deleted!")
    else:
        d_net = torch.load('d_net.pt')
    n_acturators_dim = feedback_loop.vchn_num
    lr_g = 0.0008
    lr_d = 0.0003
    opt_d = torch.optim.Adam(d_net.parameters(), lr=lr_d)
    #opt_g = torch.optim.SGD(g_net.parameters(), lr=lr_g, momentum=0.1)
    """
    def generator_sample(batch_size):
        # 用G产生一堆实验参数
        noisesource = torch.randn(batch_size, n_noise_dim)
        if gpu:
            noisesource = noisesource.cuda()
        batch_noise = Variable(noisesource)
        g_data = g_net(batch_noise)
        g_perf_real = experiment(g_data.data)
        return g_data, g_perf_real

    def train_generator(g_perf_pred):
        # 训练G
        g_loss = - torch.mean(g_perf_pred)
        # G越高越好
        opt_g.zero_grad()
        g_loss.backward(retain_variables=True)
        opt_g.step()
        g_loss_eval = g_loss.data.cpu().numpy()[0]
        print("generator loss:", g_loss_eval)
        """
    dataset = load_experiment_record()
    try:
        for epoch in range(0, 100):
            batch_size = 100
            # 从其他学习装置中采样数据
            file_teacher = torch.utils.data.DataLoader(
                dataset, batch_size, True)
            for i_batch, sample_batched in enumerate(file_teacher):
                datasource = sample_batched[0]
                powersource = sample_batched[1].float()

                g_data = Variable(datasource, requires_grad=False)
                g_perf_real = Variable(powersource)
                if gpu:
                    g_data = g_data.cuda()
                    g_perf_real = g_perf_real.cuda()
                # 用G的参数机器预测
                g_perf_pred = d_net(g_data.view(-1, n_acturators_dim, 1, 1))

                # D和真实情况越像越好

                d_loss = torch.mean(
                    torch.abs(g_perf_pred - g_perf_real))

                #nn.L1Loss(size_average=True, reduce=True)(g_perf_pred,  g_perf_real)

                # 训练D
                opt_d.zero_grad()
                d_loss.backward(retain_variables=True)
                opt_d.step()
                # 评估D
                writer.add_scalar(
                    'data/d_loss', d_loss.data.cpu().numpy()[0], epoch * batch_size + i_batch)
                if (i_batch % 2 == 1):
                    print('Batch: {}, d_loss: {}, mean_error: {}'.format(
                        int(i_batch),
                        d_loss.data.cpu().numpy()[0],
                        torch.mean(g_perf_real -
                                   g_perf_pred).cpu().data.numpy()[0]
                    ))
                if (i_batch % 5 == 1):
                    print(
                        g_perf_real.cpu().data.numpy()[0],
                        g_perf_pred.cpu().data.numpy()[0]
                    )
                if False:
                    print("====== train generator =====")
                    # train_generator(g_perf_pred)
                    pass
    except KeyboardInterrupt:
        print("saving tarining result...")
        torch.save(d_net, 'd_net.pt')
        print("okay.")
        # d_net.save_state_dict('d_net.pt')

        """
        a_old = Variable(datasource, requires_grad=True)
        a_best_old = torch.max(g_perf_real).data.cpu().numpy()[0]
        # 梯度上升采样

        epochs = 0
        print("==== gradient_ascend =====")
        for epoch in range(epochs):
                a_loss = d_net(a_old.view(-1, n_acturators_dim, 1, 1))
                a_loss.backward(a_loss.data, retain_variables=True)
                #print(a_old.grad)
                lr = 0.0001 / torch.mean(torch.abs(a_old.grad.data))
                a_new = Variable(
                    a_old.data - a_old.grad.data * lr, requires_grad=True)

                # print(a_data)
                # 用G的实验参数做实验
                a_perf_new = experiment(a_new.data)
                a_best_new = torch.max(a_perf_new).data.cpu().numpy()[0]
                improve = max(a_best_new - a_best_old, 0)
                a_best_old = a_best_new
                a_old = a_new
                print('Gradient ascend Epoch: {}, a_best:{},  improve:{} '.format(
                    int(epoch),
                    a_best_new,
                    improve
                ))
        """
