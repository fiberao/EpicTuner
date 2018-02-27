import feedback
from tensorboardX import SummaryWriter

if __name__ == '__main__':
    writer = SummaryWriter()
    x, power = feedback.load_experiment_record()
    for i in range(len(x)):
        if (i%100==1 or True):
            print(i/len(x)*100.0)
            scalars = {}
            for j in range(len(x[i])):
                scalars[str(j) + "_act"] = x[i][j]
            writer.add_scalar('data/power', power[i], i)
            writer.add_scalars('data/acturator', scalars, i)

print("okay")
