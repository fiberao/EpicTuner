import torch
import torch.nn as nn

from torch.autograd import Variable
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


if __name__ == '__main__':
    feedback = feedback.please_just_give_me_a_simple_loop("Memory")
    #feedback = feedback.feedback_loop(None, None)
    writer = SummaryWriter()
    def experiment(input_data):
        output_data = []
        for each in input_data:
            percent = feedback.f((each + 1.0) / 2.0, record=False)
            # print(percent)
            output_data.append([percent])
        powersource = torch.tanh(torch.FloatTensor(
            output_data) / (20.0 * 1000.0) - 0.3)
        if gpu:
            powersource = powersource.cuda()
        return Variable(powersource)
    #读取实验结果
    x,power = feedback.load_experiment_record()
    datasource = torch.FloatTensor(x) * 2.0 - 1.0  # 还原执行器最大最小值
    powersource = torch.tanh(torch.FloatTensor(power) / (20.0 * 1000.0) - 0.3)
    print(datasource)
    print(powersource)
    def file_teacher(batch_size):
        permutation_generator = torch.randperm(batch_size)
        if gpu:
            permutation_generator.cuda()
        power = powersource[permutation_generator]
        data = datasource[permutation_generator]
        
        if gpu:
            data = data.cuda()
            power = power.cuda()
        return data, power
    n_acturators_dim = feedback.vchn_num
    # model info
    # 给generator的噪音维数

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

    zernike_modes = 128
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
        nn.Linear(512, 1),
        nn.Tanh()
    )

    if gpu:
        g_net = g_net.cuda()
        d_net = d_net.cuda()
    lr_g = 0.0008
    lr_d = 0.0003
    opt_d = torch.optim.Adam(d_net.parameters(), lr=lr_d)
    
    opt_g = torch.optim.SGD(g_net.parameters(), lr=lr_g, momentum=0.1)

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
    epoch = 1
    while True:
        for iiii in range(10):
            epoch+=1
            # 从其他学习装置中采样数据
            datasource, powersource = file_teacher(500)
            g_data = Variable(datasource, requires_grad=False)
            g_perf_real = Variable(powersource)
            # 用G的参数机器预测
            g_perf_pred = d_net(g_data.view(-1, n_acturators_dim, 1, 1))

            if (epoch % 2 == 5):
                # print(g_data.data[0])
                print('Epoch: {}, g_perf_real: {}, g_perf_pred:{}'.format(
                    int(epoch),
                    torch.mean(g_perf_real).cpu().data.numpy()[0],
                    torch.mean(g_perf_pred).cpu().data.numpy()[0]
                ))

            # D和真实情况越像越好

            d_loss = nn.MSELoss(size_average=True, reduce=True)(
                g_perf_pred + 1, g_perf_real + 1)
            # d_loss= nn.KLDivLoss(size_average=True, reduce=True)(g_perf_pred, g_perf_real)*10.0

            # 训练D
            opt_d.zero_grad()
            d_loss.backward(retain_variables=True)
            opt_d.step()
            # 评估D
            writer.add_scalar('data/d_loss', d_loss.data.cpu().numpy()[0],epoch)
            if (epoch % 2 == 1):
                print('Epoch: {}, d_loss: {}'.format(
                    int(epoch),
                    d_loss.data.cpu().numpy()[0]
                ))
            if False:
                print("====== train generator =====")
                # train_generator(g_perf_pred)
                pass
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
