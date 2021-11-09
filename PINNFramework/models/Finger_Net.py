import torch
import torch.nn as nn

class FingerNet(nn.Module):
    def __init__(self, lb, ub, inputSize, outputSize, numFeatures = 500, num_finger_layers = 3,numLayers = 8, activation = torch.relu, normalize=True, scaling=1.):
        torch.manual_seed(1234)
        super(FingerNet, self).__init__()
        self.input_size = inputSize
        self.num_finger_layers= 3
        self.numFeatures = numFeatures
        self.numLayers = numLayers 
        self.lin_layers = nn.ModuleList()
        self.lb = torch.tensor(lb).float()
        self.ub = torch.tensor(ub).float()
        self.activation = activation
        self.normalize = normalize
        self.scaling = scaling
        self.output_size = outputSize
        self.init_layers()


    def init_layers(self):
        """
        This function creates the torch layers and initialize them with xavier
        :param self:
        :return:
        """
        lenInput = 1  # FingerNet Scales slices input
        self.finger_nets = []
        self.lin_layers = nn.ModuleList()
        for i in range(self.input_size):
            self.finger_nets.append(nn.ModuleList())
            self.in_x.append(nn.Linear(lenInput, self.numFeatures))
            for _ in range(self.num_finger_layers):
                self.finger_nets[i].append(nn.Linear(self.numFeatures, self.numFeatures))
            for m in self.finger_nets[i]:
                if isinstance(m, nn.Linear):
                    nn.init.xavier_uniform_(m.weight)

        self.lin_layers.append(nn.Linear(self.input_size * self.numFeatures, self.numFeatures))
        for i in range(self.numLayers):
            inFeatures = self.numFeatures
            self.lin_layers.append(nn.Linear(inFeatures, self.numFeatures))
        inFeatures = self.numFeatures
        self.lin_layers.append(nn.Linear(inFeatures, self.outut_size))
        for m in self.lin_layers:
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0)
                
    def forward(self, x_in):
        if self.normalize:
            x_in = 2.0 * (x_in - self.lb) / (self.ub - self.lb) - 1.0

        input_tensors = []
        for i in range(self.input_size):
            self.input_tensors.append(x_in[:,i].view(-1,1))

        output_tensors = []
        for finger_idx in range(self.input_size):
            x_in = input_tensors[finger_idx]
            for i in range(0,len(self.finger_nets[finger_idx])):
                x_in = self.in_x[i](x_in)
                x_in = self.activation(x_in)
            output_tensors.append(x_in)

        x = torch.cats(output_tensors, 1)

        for i in range(0, len(self.lin_layers)-1):
            x = self.lin_layers[i](x)
            x = self.activation(x)
        x = self.lin_layers[-1](x)

        return self.scaling * x

    def cuda(self):
        super(FingerNet, self).cuda()
        self.lb = self.lb.cuda()
        self.ub = self.ub.cuda()

    def cpu(self):
        super(FingerNet, self).cpu()
        self.lb = self.lb.cpu()
        self.ub = self.ub.cpu()
        
    def to(self, device):
        super(FingerNet, self).to(device)
        self.lb = self.lb.to(device)
        self.ub = self.ub.to(device)