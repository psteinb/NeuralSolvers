from torch.nn import L1Loss, MSELoss


class LossTerm:
    def __init__(self, dataset, norm='L2', weight=1.):
        # cases for standard torch norms
        if norm == 'L2':
            self.norm = MSELoss()
        elif norm == 'L1':
            self.norm = L1Loss()
        else:
            # Case for self implemented norms
            self.norm = norm
        self.dataset = dataset
        self.weight = weight
