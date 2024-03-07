import torch.nn as nn
import torch.nn.functional as F
import torch
from torchvision import datasets, models, transforms
import pretrainedmodels

import torch.nn as nn


class Self_Attn(nn.Module):
    """ Self attention Layer"""
    def __init__(self,in_dim,activation):
        super(Self_Attn,self).__init__()
        self.chanel_in = in_dim
        self.activation = activation

        self.query_conv = nn.Conv2d(in_channels = in_dim , out_channels = in_dim//8 , kernel_size= 1)
        self.key_conv = nn.Conv2d(in_channels = in_dim , out_channels = in_dim//8 , kernel_size= 1)
        self.value_conv = nn.Conv2d(in_channels = in_dim , out_channels = in_dim , kernel_size= 1)
        self.gamma = nn.Parameter(torch.zeros(1))

        self.softmax  = nn.Softmax(dim=-1) #
    def forward(self,x):
        """
            inputs :
                x : input feature maps( B X C X W X H)
            returns :
                out : self attention value + input feature
                attention: B X N X N (N is Width*Height)
        """
        m_batchsize,C,width ,height = x.size()
        proj_query  = self.query_conv(x).view(m_batchsize,-1,width*height).permute(0,2,1) # B X CX(N)
        proj_key =  self.key_conv(x).view(m_batchsize,-1,width*height) # B X C x (*W*H)
        energy =  torch.bmm(proj_query,proj_key) # transpose check
        attention = self.softmax(energy) # BX (N) X (N)
        proj_value = self.value_conv(x).view(m_batchsize,-1,width*height) # B X C X N

        out = torch.bmm(proj_value,attention.permute(0,2,1) )
        out = out.view(m_batchsize,C,width,height)

        out = self.gamma*out + x
        return out,attention

class Resnet50(nn.Module):
    def __init__(self, pretrained, ch_in):
        super(Resnet50, self).__init__()

        self.net = models.resnet50(pretrained=pretrained) # pretrained=False just for debug reasons

        if pretrained:
            if ch_in != 3:
                first_layer_weights = self.net.conv1.weight

                wa = (first_layer_weights[:,0,...] + first_layer_weights[:,1,...] + first_layer_weights[:,2,...]) / 3
                wa = wa.unsqueeze(1).repeat(1,ch_in,1,1)


                first_conv = nn.Conv2d(ch_in, 64, kernel_size=7, stride=2, padding=3,
                                       bias=False)
                first_conv.weight = torch.nn.Parameter(wa, requires_grad=True)
                self.net.conv1 = first_conv
        else:
            if ch_in != 3:
                self.net.conv1 = nn.Conv2d(ch_in, 64, kernel_size=7, stride=2, padding=3,
                                       bias=False)
        num_ftrs = self.net.fc.in_features
        self.net.fc = torch.nn.Linear(num_ftrs, 2)

    def forward(self, x):
        x = self.net(x)
        return x

class XCeption(nn.Module):
    def __init__(self, pretrained, ch_in):
        super(XCeption, self).__init__()
        # print(pretrainedmodels.model_names)

        # self.net = models.resnet50(pretrained=pretrained) # pretrained=False just for debug reasons
        self.net = pretrainedmodels.__dict__['xception'](num_classes=1000, pretrained='imagenet')

        if pretrained:
            if ch_in != 3:
                first_layer_weights = self.net.conv1.weight

                wa = (first_layer_weights[:,0,...] + first_layer_weights[:,1,...] + first_layer_weights[:,2,...]) / 3
                wa = wa.unsqueeze(1).repeat(1,ch_in,1,1)


                first_conv = nn.Conv2d(ch_in, 64, kernel_size=7, stride=2, padding=3,
                                       bias=False)
                first_conv.weight = torch.nn.Parameter(wa, requires_grad=True)
                self.net.conv1 = first_conv
        else:
            if ch_in != 3:
                self.net.conv1 = nn.Conv2d(ch_in, 64, kernel_size=7, stride=2, padding=3,
                                       bias=False)
        # print(self.net)
        num_ftrs = self.net.last_linear.in_features
        self.net.last_linear = torch.nn.Linear(num_ftrs, 2)

    def forward(self, x):
        x = self.net(x)
        return x


class Resnet50_2(nn.Module):
    def __init__(self, pretrained, ch_in):
        super(Resnet50_2, self).__init__()

        self.net = models.resnet50(pretrained=pretrained) # pretrained=False just for debug reasons

        if pretrained:
            if ch_in != 3:
                first_layer_weights = self.net.conv1.weight

                wa = (first_layer_weights[:,0,...] + first_layer_weights[:,1,...] + first_layer_weights[:,2,...]) / 3
                wa = wa.unsqueeze(1).repeat(1,ch_in,1,1)


                first_et.conv1 = first_conv
        else:
            if ch_in != 3:
                self.net.conv1 = nn.Conv2d(ch_in, 64, kernel_size=7, stride=2, padding=3,
                                       bias=False)
        # num_ftrs = self.net.fc.in_features + 1024 + 512 + 256
        num_ftrs = 1024 + 512 + 256

        for param in self.net.parameters():
            param.requires_grad = False

        # self.net.fc = torch.nn.Linear(num_ftrs, 2)
        self.fc = torch.nn.Linear(num_ftrs, 2)

        self.b1 = torch.nn.Sequential(*list(self.net.children())[:4])
        self.b2 = torch.nn.Sequential(*list(self.net.children())[4])
        self.b3 = torch.nn.Sequential(*list(self.net.children())[5])
        self.b4 = torch.nn.Sequential(*list(self.net.children())[6])
        self.b5 = torch.nn.Sequential(*list(self.net.children())[7])
        self.ap = torch.nn.AdaptiveAvgPool2d(output_size=(1, 1))

        self.attn1 = Self_Attn( 256, 'relu')
        self.attn2 = Self_Attn( 512, 'relu')
        self.attn3 = Self_Attn( 1024, 'relu')

    def forward(self, x):
        x1 = self.b1(x)

        x2 = self.b2(x1)
        x3 = self.b3(x2)
        x4 = self.b4(x3)

        x5 = self.b5(x4)

        x2, p1 = self.attn1(x2)
        x2 = self.ap(x2)
        x2 = torch.flatten(x2, 1)

        x3, p2 = self.attn2(x3)
        x3 = self.ap(x3)
        x3 = torch.flatten(x3, 1)

        x4, p3 = self.attn3(x4)
        x4 = self.ap(x4)
        x4 = torch.flatten(x4, 1)
        #
        # x5 = self.ap(x5)
        # x5 = torch.flatten(x5, 1)

        x_cat = torch.cat((x2, x3, x4), dim=-1)
        fc = self.fc(x_cat)
        return fc

class Resnet50_dual(nn.Module):
    def __init__(self, pretrained, ch_in):
        super(Resnet50_dual, self).__init__()

        self.net_rgb = models.resnet50(pretrained=pretrained) # pretrained=False just for debug reasons

        self.net_flow = models.resnet50(pretrained=pretrained) # pretrained=False just for debug reasons

        if pretrained:
            if ch_in != 3:
                first_layer_weights = self.net_flow.conv1.weight

                wa = (first_layer_weights[:,0,...] + first_layer_weights[:,1,...] + first_layer_weights[:,2,...]) / 3
                wa = wa.unsqueeze(1).repeat(1,ch_in,1,1)


                first_conv = nn.Conv2d(ch_in, 64, kernel_size=7, stride=2, padding=3,
                                       bias=False)
                first_conv.weight = torch.nn.Parameter(wa, requires_grad=True)
                self.net_flow.conv1 = first_conv
        else:
            if ch_in != 3:
                self.net_flow.conv1 = nn.Conv2d(ch_in, 64, kernel_size=7, stride=2, padding=3,
                                       bias=False)

        num_ftrs =  self.net_rgb.fc.in_features + self.net_flow.fc.in_features

        self.removed_rgb = list(self.net_rgb.children())[:-1]
        self.net_rgb= torch.nn.Sequential(*self.removed_rgb)

        self.removed_flow = list(self.net_flow.children())[:-1]
        self.net_flow= torch.nn.Sequential(*self.removed_flow)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))

        self.fc = torch.nn.Linear(num_ftrs, 2)

    def forward(self, x1, x2):
        x1 = self.net_rgb(x1)
        x2 = self.net_flow(x2)
        x1 = self.avgpool(x1)
        x1 = torch.flatten(x1, 1)
        x2 = self.avgpool(x2)
        x2 = torch.flatten(x2, 1)
        x = torch.cat((x1, x2), dim=-1)
        x = self.fc(x)
        return x
