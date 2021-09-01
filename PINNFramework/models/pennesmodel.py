from torch import randn
from torch.nn.functional import relu
from torch.autograd import Variable
from torch.nn import Module, Parameter

class PennesHPM(Module):
    """
    Constructor of the Pennes model:
        du/dt = convection + linear(u) = (a_conv * Δu) + (w * u + b)
    Args:
        config (dict): dictionary defining the configuration of the model. 
            keys: convection, linear_u.
            values: True (include term in the model) or False (do not include).
        u_blood (float): arterial blood temperature.
    """   
    def __init__(self, config, u_blood = 37.): 
        super().__init__()
        self.config = config
        self.u_blood = u_blood
        if config['convection']:
            self.a_conv = Parameter(Variable((randn([640,480]).clone().detach().requires_grad_(True)))) 
        if config['linear_u']:
            self.a_linear_u_w = Parameter(Variable((randn([640,480]).clone().detach().requires_grad_(True))))
            self.a_linear_u_b = Parameter(Variable((randn([640,480]).clone().detach().requires_grad_(True))))
            
    def convection(self, derivatives): 
        """
        Convection term of the model:
            convection = a_conv * Δu
        It is linear mapping of the convection term in the original equation.
        Args:
            derivatives(tensor): tensor of the form [x,y,t,x_indices,y_indices,u,u_xx,u_yy,u_t].
        """
        u_xx = derivatives[:, 6].view(-1)
        u_yy = derivatives[:, 7].view(-1) 
        x_indices = derivatives[:, 3].view(-1).long()
        y_indices = derivatives[:, 4].view(-1).long()
        a_conv = relu(self.a_conv[x_indices,y_indices].view(-1))
        return a_conv * (u_xx + u_yy) 

    def linear_u(self, derivatives):
        """
        Linear term of the model:
            linear(u) = w * u + b
        It is linear mapping of the perfusion term in the original equation.
        Args:
            derivatives(tensor): tensor of the form [x,y,t,x_indices,y_indices,u,u_xx,u_yy,u_t].
        """
        x_indices = derivatives[:, 3].view(-1).long()
        y_indices = derivatives[:, 4].view(-1).long()
        u_values = derivatives[:, 5].view(-1)
        a_linear_u_w = self.a_linear_u_w[x_indices,y_indices].view(-1)
        a_linear_u_b = self.a_linear_u_b[x_indices,y_indices].view(-1)
        return a_linear_u_w*(u_values-self.u_blood) + a_linear_u_b

    def forward(self, derivatives):
        """
        Forward pass of the model.
        Args:
            derivatives(tensor): tensor of the form [x,y,t,x_indices,y_indices,u,u_xx,u_yy,u_t].
                where x,y,t - spatiotemporal coordinates in physical units;
                      x_indices, y_indices - grid coordinates;
                      u, u_xx, u_yy, u_t - temprerature and its derivatives.
        """               
        predicted_u_t = 0
        if self.config['convection']:
            predicted_u_t += self.convection(derivatives)
        if self.config['linear_u']:
            predicted_u_t += self.linear_u(derivatives)
        return predicted_u_t 
    
    def cuda(self):
        """
        Sends the instance of the class to cuda device.
        """
        super().cuda()
        if self.config['convection']:
            self.a_conv = self.a_conv.cuda()
        if self.config['linear_u']:
            self.a_linear_u_w = self.a_linear_u_w.cuda()
            self.a_linear_u_b = self.a_linear_u_b.cuda()
