import torch
import pandas as pd
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from random import random
from torch.utils.data import Dataset, DataLoader


class myLSTM(torch.nn.Module):
    def __init__(self, hidden_dim=30, input_dim=8, output_dim=1, n_inputs=50, n_outputs=50):        
        super(myLSTM, self).__init__()
        convDim=20
        n_layers=2
        self.device='cpu'
        self.num_layers = n_layers
        self.n_outputs = n_outputs
        self.hidden_dim = hidden_dim

        self.dropout = torch.nn.Dropout(p=0.5)
        self.bn1 = torch.nn.BatchNorm1d(num_features=hidden_dim*n_layers + convDim)
        self.bn2 = torch.nn.BatchNorm1d(num_features=hidden_dim + convDim + 2)
        
        self.hidden_state = torch.nn.Parameter(torch.randn(n_layers, 1, hidden_dim, device = self.device))
        self.cell_state = torch.nn.Parameter(torch.randn(n_layers, 1, hidden_dim, device = self.device))
        self.hidden = (self.hidden_state, self.cell_state)

        self.lstm = torch.nn.LSTM(input_dim, hidden_dim, self.num_layers, dropout=0.5, batch_first=True)
        self.lstm2 = torch.nn.LSTM(hidden_dim * self.num_layers +2 +convDim, hidden_dim, self.num_layers, dropout=0.5, batch_first=True)

        self.conv1 = torch.nn.Conv1d(8, 32, 5) 
        self.conv2 = torch.nn.Conv1d(32, 64, 3)
        self.conv3 = torch.nn.Conv1d(64, 128, 3)
        self.pool = torch.nn.MaxPool1d(2)
        self.fc = torch.nn.Linear(128 * 4, convDim)
        
        self.W = torch.nn.ParameterList([torch.nn.Parameter(torch.randn(self.hidden_dim + convDim + 2, 100, device = self.device)/10) for i in range(self.n_outputs)])
        self.B = torch.nn.ParameterList([torch.nn.Parameter(torch.randn(100, device = self.device)) for i in range(self.n_outputs)])
        self.U = torch.nn.ParameterList([torch.nn.Parameter(torch.randn(100, output_dim, device = self.device)) for i in range(self.n_outputs)])
        self.C = torch.nn.ParameterList([torch.nn.Parameter(torch.randn(output_dim, device = self.device)) for i in range(self.n_outputs)])
    
    def dropoutOn(self):
        for m in self.modules():
            if m.__class__.__name__.startswith('Dropout'):
                m.train()
           
    def to(self, device):
        self.device = device
        super(myLSTM, self).to(device)
    
    # Computa la pasada hacia adelante
    def forward(self, x, y, predict=False, noutputs=50):
        #x [batch, muestras, features]
        # Inputs: input, (h_0, c_0)
        # input of shape (batch, seq_len, input_size)
        # h_0 of shape (batch, num_layers * num_directions, hidden_size)
        # c_0 of shape (batch, num_layers * num_directions, hidden_size)
        y = y[:, 0:noutputs, :]
        out, hidden=self.lstm (x,(self.hidden[0].to(self.device )*torch.ones(1,x.shape[0],self.hidden_dim, device=self.device),self.hidden[1]*torch.ones(1,x.shape[0],self.hidden_dim, device=self.device)))
        y_pred = torch.zeros_like(y)
        # h_n [num_layers * num_directions, batch, hidden_size]
        h_n, c_n = hidden
        # Conv
        # Se transpone para que quede (batch, canal, muestra)
        xConv = torch.transpose(x, 1, 2)
        xConv = self.pool(torch.relu(self.conv1(xConv)))
        xConv = self.pool(torch.relu(self.conv2(xConv)))
        xConv = self.pool(torch.relu(self.conv3(xConv)))
        xConv = xConv.view(xConv.size(0), -1)
        xConv = torch.relu(self.fc(xConv))
        
        # Context
        # union convolucional LSTM
        context= self.bn1(torch.cat((h_n[0,:,:],h_n[1,:,:],xConv), 1))
        y_in = torch.unsqueeze(x[:,-1,0],1)
        t_in = torch.unsqueeze(x[:,-1,-1],1)       
        

        for i in range(noutputs):
            #se une contexto, tiempor y salida anterior, además se agrega la dimención seq_len
            t_in = torch.fmod(t_in + 15, 1440)
            input2 = torch.unsqueeze(torch.cat((context, t_in, y_in), 1),1)
            output2, hidden = self.lstm2(input2,hidden)
            
            # union convolucional LSTM
            lstmConv = torch.cat((torch.squeeze(output2, dim=1),xConv, t_in, y_in),1)
            inter = torch.relu(self.dropout(self.bn2(lstmConv)) @ self.W[i] + self.B[i])
            y_in = inter @ self.U[i] + self.C[i]
            y_pred[:,i,:] = y_in            
            if (not predict):
                y_in.copy_(y[:,i,:])
        return y_pred



# carga de modelo
def load_model(path="./model/"):
    red = myLSTM()
    optimizador = torch.optim.Adam(red.parameters(), 1e-3)

    """checkpoint = torch.load('./checkpoint.pth.tar')
    red.load_state_dict(checkpoint['model_state_dict'])
    optimizador.load_state_dict(checkpoint['optimizer_state_dict'])"""

    checkpoint = torch.load(path + 'checkpoint.pth.tar', map_location=torch.device("cpu"))
    red.load_state_dict(checkpoint['model_state_dict'])
    optimizador.load_state_dict(checkpoint['optimizer_state_dict'])

    red.to('cpu')
    red.eval()
    red.dropoutOn()
    return red

def predict(df, red, device='cpu'):
    l=20 # cantidad de fordwards
    # Estoy suponiendo que hay 50 filas
    # Las columnas deben quedar así ['temp', 'hum', 'vel.vin', 'precip', 'rad.sol', 'p.atm', 'Dia', 'Minuto']
    
    # Se crea columna tiempo 
    df['Tiempo'] = pd.to_datetime(df.datetimehrs)
    # Se eliminan las columnas que no se utilizan
    df2=df.drop(['code', 'date','time', 'dir.vin', 'datetimehrs', 'date+14hrs'], axis=1)
    # Se agregan dias y minutos y se elimina la columna tiempo
    df2['Dia']=df2['Tiempo'].dt.strftime('%j').astype(int)
    df2['Minuto']=df2['Tiempo'].dt.hour*60+df['Tiempo'].dt.minute
    df2=df2.drop(['Tiempo'], axis=1)
    
    #Conversión a numpy
    array=df2.to_numpy(dtype=float)
                       
    x=torch.as_tensor(array, dtype=torch.float32, device=device)
    ################
    predicts = []    
    for i in range(l):
        y_pred = red.forward(torch.unsqueeze(x,0), torch.zeros((1,50,1)), predict=True)
        predicts.append(torch.squeeze(y_pred.cpu()).detach().numpy())
    mean = np.zeros_like(torch.squeeze(y_pred.cpu()).detach().numpy())
    for yp in predicts:
        mean += yp
    mean = mean/len(predicts)
    
    return mean 
                     
    