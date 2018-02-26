import torch
import torch.nn as nn
from torch.autograd import Variable
import feedback

gpu = False
real = True


class VariableSizeInspector(nn.Module):
    def __init__(self):
        super(VariableSizeInspector, self).__init__()

    def forward(self, x):
        #print('after' , x.size())
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
    if real:
        feedback = feedback.please_just_give_me_a_simple_loop("Memory")

        def experiment(input_data):
            output_data = []
            for each in input_data:
                percent = feedback.f((each+1.0)/2.0) / (20.0 * 1000.0) - 0.2
                # print(percent)
                output_data.append([percent])
            var = Variable(torch.tanh(torch.FloatTensor(output_data)))
            if gpu:
                var = var.cuda()
            return var
        n_acturators_dim = feedback.vchn_num
    else:
        def experiment(input_data):
            output_data = Variable(
                -0.001 * (
                    torch.sin(input_data[:, 0] - 2)
                    * torch.cos(input_data[:, 1] - 0.3)
                    * (1. / (torch.abs(input_data[:, 2] - 0.5) + 1))
                    * (1. / (torch.abs(input_data[:, 3] - 0.1) + 1))
                    * (1. / (torch.abs(input_data[:, 4] - 0.3) + 1))
                ),
                requires_grad=False)
            return output_data
        n_acturators_dim = 5

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
    if gpu:
        g_net = g_net.cuda()
    zernike_modes = 32
    d_net = nn.Sequential(
        nn.ConvTranspose2d(n_acturators_dim, zernike_modes, 8),
        nn.ReLU(),
        nn.ConvTranspose2d(zernike_modes, 128, 8),
        nn.ReLU(),
        nn.Conv2d(128, 1, 1),  # mixing layer
        VariableSizeInspector(),
        nn.ReLU(),
        nn.Conv2d(1, 128, 3),
        VariableSizeInspector(),
        nn.ReLU(),
        VariableSizeInspector(),
        nn.Conv2d(128, 64, 3),
        VariableSizeInspector(),
        nn.ReLU(),
        FeatureFlaten(),
        nn.Linear(11 * 11 * 64, 256),
        VariableSizeInspector(),
        nn.ReLU(),
        nn.Dropout(),
        nn.Linear(256, 1),
        nn.Tanh()
    )

    if gpu:
        d_net = d_net.cuda()
    lr_g = 0.0008
    lr_d = 0.0003
    opt_d = torch.optim.Adam(d_net.parameters(), lr=lr_d)
    opt_g =torch.optim.Adam(g_net.parameters(), lr=lr_g)
    #opt_g = torch.optim.SGD(g_net.parameters(), lr=lr_g, momentum=0.1)
    #

    batch_size = 33
    epochs = 1000000

    for epoch in range(epochs):
        # 用G产生一堆实验参数
        if gpu:
            batch_noise = Variable(torch.randn(batch_size, n_noise_dim).cuda())
        else:
            batch_noise = Variable(torch.randn(batch_size, n_noise_dim))
        g_data = g_net(batch_noise)

        # 用G的实验参数做实验
        prob_real = experiment(g_data.data)
        # 用G的参数机器预测
        reviewed = g_data.view(-1, n_acturators_dim, 1, 1)

        prob_pred = d_net(reviewed)

        if (epoch % 2 == 1):
            # print(g_data.data[0])
            print("--------------")
            print(torch.mean(prob_real))
            print(torch.mean(prob_pred))
            print("--------------")
        # D和真实情况越像越好

        d_loss = nn.MSELoss(size_average=True, reduce=True)(
            prob_pred + 1, prob_real + 1)
        #d_loss= nn.KLDivLoss(size_average=True, reduce=True)(prob_pred, prob_real)*10.0

        # 训练D
        opt_d.zero_grad()

        d_loss.backward(retain_variables=True)
        opt_d.step()
        # G越高越好

        g_loss = - torch.mean(prob_pred)
        # 训练G
        opt_g.zero_grad()
        g_loss.backward(retain_variables=True)
        opt_g.step()
        # 评估G
        g_best = torch.max(prob_real)
        if (epoch % 2 == 1):
            print('Run: {} minutes, d_loss: {}, g_loss: {}, g_best: {}'.format(
                int(epoch * batch_size / 60),
                d_loss.data.cpu().numpy()[0],
                g_loss.data.cpu().numpy()[0],
                g_best.data.cpu().numpy()[0]
            ))
        # 从D中梯度上升采样一个
        """
        d_net.backward()
        ratio = np.abs(img_variable.grad.data.cpu().numpy()).mean()
        learning_rate_use = learning_rate / ratio
        img_variable.data.add_(img_variable.grad.data * learning_rate_use)
        """