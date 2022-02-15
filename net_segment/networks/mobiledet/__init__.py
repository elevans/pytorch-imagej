import os
import torch.nn as nn
from timm.models.efficientnet_blocks import *
from tucker_conv.conv import TuckerConv

# Target: Pixel-4 DSP
class MobileDetDSP(nn.Module):
    def __init__(self):
        super(MobileDetDSP, self).__init__()
        
        # First block
        self.conv1 = nn.Conv2d(3, 32, 3, stride = 2)
        self.bn1 = nn.BatchNorm2d(32)
        self.act1 = nn.ReLU6()
        self.ibn_ne = DepthwiseSeparableConv(32, 24, act_layer = nn.ReLU6)
        
        # Second block
        self.fused1 = EdgeResidual(24, 32, exp_ratio = 4, stride = 2, act_layer = nn.ReLU6)
        self.fused2 = EdgeResidual(32, 32, exp_ratio = 4, act_layer = nn.ReLU6)
        self.ibn1 = InvertedResidual(32, 32, exp_ratio = 4)
        self.tucker1 = TuckerConv(32, 32)
        
        # Third block
        self.fused3 = EdgeResidual(32, 64, exp_ratio = 8, stride = 2, act_layer = nn.ReLU6)
        self.ibn2 = InvertedResidual(64, 64, exp_ratio = 4)
        self.fused4 = EdgeResidual(64, 64, exp_ratio = 4, act_layer = nn.ReLU6)
        self.fused5 = EdgeResidual(64, 64, exp_ratio = 4, act_layer = nn.ReLU6)
        
        # Fourth block
        self.fused6 = EdgeResidual(64, 120, exp_ratio = 8, stride = 2, act_layer = nn.ReLU6)
        self.ibn3 = InvertedResidual(120, 120, exp_ratio = 4)
        self.ibn4 = InvertedResidual(120, 120, exp_ratio = 8)
        self.ibn5 = InvertedResidual(120, 120, exp_ratio = 8)
        
        self.fused7 = EdgeResidual(120, 144, exp_ratio = 8, act_layer = nn.ReLU6)
        self.ibn6 = InvertedResidual(144, 144, exp_ratio = 8)
        self.ibn7 = InvertedResidual(144, 144, exp_ratio = 8)
        self.ibn8 = InvertedResidual(144, 144, exp_ratio = 8)
        
        # Fifth block
        self.ibn9 = InvertedResidual(144, 160, exp_ratio = 4, stride = 2)
        self.ibn10 = InvertedResidual(160, 160, exp_ratio = 4)
        self.fused8 = EdgeResidual(160, 160, exp_ratio = 4, act_layer = nn.ReLU6)
        self.tucker2 = TuckerConv(160, 160, in_comp_ratio = 0.75)        
        self.ibn11 = InvertedResidual(160, 240, exp_ratio = 8)

        
    def forward(self, x):
        # First block
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.act1(x)
        x = self.ibn_ne(x)
        c1 = x
        
        # Second block
        x = self.fused1(x)
        x = self.fused2(x)
        x = self.ibn1(x)
        x = self.tucker1(x)
        c2 = x
        
        # Third block
        x = self.fused3(x)
        x = self.ibn2(x)
        x = self.fused4(x)
        x = self.fused5(x)
        c3 = x
        
        # Fourth block
        x = self.fused6(x)
        x = self.ibn3(x)
        x = self.ibn4(x)
        x = self.ibn5(x)
        x = self.fused7(x)
        x = self.ibn6(x)
        x = self.ibn7(x)
        x = self.ibn8(x)
        c4 = x
        
        # Fifth block
        x = self.ibn9(x)
        x = self.ibn10(x)
        x = self.fused8(x)
        x = self.tucker2(x)
        x = self.ibn11(x)
        c5 = x
        
        return c1, c2, c3, c4, c5


# Target: Jetson Xavier GPU
class MobileDetGPU(nn.Module):
    def __init__(self):
        super(MobileDetGPU, self).__init__()
        
        # First block
        self.conv1 = nn.Conv2d(3, 32, 3, stride = 2)
        self.bn1 = nn.BatchNorm2d(32)
        self.act1 = nn.ReLU6()
        self.tucker1 = TuckerConv(32, 16, residual = False)
        
        # Second block
        self.fused1 = EdgeResidual(16, 32, exp_ratio = 8, stride = 2, act_layer = nn.ReLU6)
        self.tucker2 = TuckerConv(32, 32, out_comp_ratio = 0.25)
        self.tucker3 = TuckerConv(32, 32, out_comp_ratio = 0.25)
        self.tucker4 = TuckerConv(32, 32, out_comp_ratio = 0.25)
        
        # Third block
        self.fused2 = EdgeResidual(32, 64, exp_ratio = 8, stride = 2, act_layer = nn.ReLU6)
        self.fused3 = EdgeResidual(64, 64, exp_ratio = 8, act_layer = nn.ReLU6)
        self.fused4 = EdgeResidual(64, 64, exp_ratio = 8, act_layer = nn.ReLU6)
        self.fused5 = EdgeResidual(64, 64, exp_ratio = 4, act_layer = nn.ReLU6)
        
        # Fourth block
        self.fused6 = EdgeResidual(64, 128, exp_ratio = 8, stride = 2, act_layer = nn.ReLU6)
        self.fused7 = EdgeResidual(128, 128, exp_ratio = 4, act_layer = nn.ReLU6)
        self.fused8 = EdgeResidual(128, 128, exp_ratio = 4, act_layer = nn.ReLU6)
        self.fused9 = EdgeResidual(128, 128, exp_ratio = 4, act_layer = nn.ReLU6)
        
        self.fused10 = EdgeResidual(128, 128, exp_ratio = 8, act_layer = nn.ReLU6)
        self.fused11 = EdgeResidual(128, 128, exp_ratio = 8, act_layer = nn.ReLU6)
        self.fused12 = EdgeResidual(128, 128, exp_ratio = 8, act_layer = nn.ReLU6)
        self.fused13 = EdgeResidual(128, 128, exp_ratio = 8, act_layer = nn.ReLU6)
        
        # Fifth block
        self.fused14 = EdgeResidual(128, 128, exp_ratio = 4, stride = 2, act_layer = nn.ReLU6)
        self.fused15 = EdgeResidual(128, 128, exp_ratio = 4, act_layer = nn.ReLU6)
        self.fused16 = EdgeResidual(128, 128, exp_ratio = 4, act_layer = nn.ReLU6)
        self.fused17 = EdgeResidual(128, 128, exp_ratio = 4, act_layer = nn.ReLU6)
        self.ibn1 = InvertedResidual(128, 384, exp_ratio = 8)
    
    def forward(self, x):
        # First block
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.act1(x)
        x = self.tucker1(x)
        c1 = x
        
        # Second block
        x = self.fused1(x)
        x = self.tucker2(x)
        x = self.tucker3(x)
        x = self.tucker4(x)
        c2 = x
        
        # Third block
        x = self.fused2(x)
        x = self.fused3(x)
        x = self.fused4(x)
        x = self.fused5(x)
        c3 = x
        
        # Fourth block
        x = self.fused6(x)
        x = self.fused7(x)
        x = self.fused8(x)
        x = self.fused9(x)        
        x = self.fused10(x)
        x = self.fused11(x)
        x = self.fused12(x)
        x = self.fused13(x)
        c4 = x
        
        # Fifth block
        x = self.fused14(x)
        x = self.fused15(x)
        x = self.fused16(x)
        x = self.fused17(x)
        x = self.ibn1(x)
        c5 = x
        
        return c1, c2, c3, c4, c5


# Target: Pixel-4 EdgeTPU
class MobileDetTPU(nn.Module):
    def __init__(self):
        super(MobileDetTPU, self).__init__()
        
        # First block
        self.conv1 = nn.Conv2d(3, 32, 3, stride = 2)
        self.bn1 = nn.BatchNorm2d(32)
        self.act1 = nn.ReLU6()
        self.tucker1 = TuckerConv(32, 16, residual = False)
        
        # Second block
        self.fused1 = EdgeResidual(16, 16, exp_ratio = 8, stride = 2, act_layer = nn.ReLU6)
        self.fused2 = EdgeResidual(16, 16, exp_ratio = 4, act_layer = nn.ReLU6)
        self.fused3 = EdgeResidual(16, 16, exp_ratio = 8, act_layer = nn.ReLU6)
        self.fused4 = EdgeResidual(16, 16, exp_ratio = 4, act_layer = nn.ReLU6)
        
        # Third block
        self.fused5 = EdgeResidual(16, 40, exp_kernel_size = 5, exp_ratio = 8, stride = 2, act_layer = nn.ReLU6)
        self.fused6 = EdgeResidual(40, 40, exp_ratio = 4, act_layer = nn.ReLU6)
        self.fused7 = EdgeResidual(40, 40, exp_ratio = 4, act_layer = nn.ReLU6)
        self.fused8 = EdgeResidual(40, 40, exp_ratio = 4, act_layer = nn.ReLU6)
        
        # Fourth block
        self.ibn1 = InvertedResidual(40, 72, exp_ratio = 8, stride = 2)
        self.ibn2 = InvertedResidual(72, 72, exp_ratio = 8)
        self.fused9 = EdgeResidual(72, 72, exp_ratio = 4, act_layer = nn.ReLU6)
        self.fused10 = EdgeResidual(72, 72, exp_ratio = 4, act_layer = nn.ReLU6)
       
        self.ibn3 = InvertedResidual(72, 96, dw_kernel_size = 5, exp_ratio = 8)
        self.ibn4 = InvertedResidual(96, 96, dw_kernel_size = 5, exp_ratio = 8)
        self.ibn5 = InvertedResidual(96, 96, exp_ratio = 8)
        self.ibn6 = InvertedResidual(96, 96, exp_ratio = 8)
        
        # Fifth block
        self.ibn7 = InvertedResidual(96, 120, dw_kernel_size = 5, exp_ratio = 8, stride = 2)
        self.ibn8 = InvertedResidual(120, 120, exp_ratio = 8)
        self.ibn9 = InvertedResidual(120, 120, dw_kernel_size = 5, exp_ratio = 4)
        self.ibn10 = InvertedResidual(120, 120, exp_ratio = 8)
        self.ibn11 = InvertedResidual(120, 384, dw_kernel_size = 5, exp_ratio = 8)
    
    def forward(self, x):
        # First block
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.act1(x)
        x = self.tucker1(x)
        c1 = x
        
        # Second block
        x = self.fused1(x)
        x = self.fused2(x)
        x = self.fused3(x)
        x = self.fused4(x)
        c2 = x
        
        # Third block
        x = self.fused5(x)
        x = self.fused6(x)
        x = self.fused7(x)
        x = self.fused8(x)
        c3 = x
        
        # Fourth block
        x = self.ibn1(x)
        x = self.ibn2(x)
        x = self.fused9(x)
        x = self.fused10(x)
        x = self.ibn3(x)
        x = self.ibn4(x)
        x = self.ibn5(x)
        x = self.ibn6(x)
        c4 = x
        
        # Fifth block
        x = self.ibn7(x)
        x = self.ibn8(x)
        x = self.ibn9(x)
        x = self.ibn10(x)
        x = self.ibn11(x)        
        c5 = x
        
        return c1, c2, c3, c4, c5

class MobileDetNet():
    def construct_model():
        model = MobileDetDSP()
        return model