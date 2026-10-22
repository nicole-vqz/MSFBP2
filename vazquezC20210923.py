"""
Práctica 2: Sistema cardiovascular 

Departamento de Ingeniería Eléctrica y Electrónica, Ingeniería Biomédica
Tecnológico Nacional de México [TecNM - Tijuana]
Blvd. Alberto Limón Padilla s/n, C.P. 22454, Tijuana, B.C., México

Nombre del alumno: Nicole Vazquez Alvear
Número de control: C20210923
Correo institucional: lC20210923@tectijuana.edu.mx

Asignatura: Modelado de Sistemas Fisiológicos
Docente: Dr. Paul Antonio Valle Trujillo; paul.valle@tectijuana.edu.mx
"""
# Instalar librerias en consola
#!pip install control
#!pip install slycot


# Librerías para cálculo numérico y generación de gráficas
import control as ctrl
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd

# Datos de la simulación 
u = pd.read_excel(r'C:\Users\nicky\Downloads\P2\signal.xlsx', header=None).to_numpy().flatten()
x0, t0, tend, dt, w, h = 0, 0, 15, 1E-3, 10, 5
N = round((tend - t0) / dt) + 1
t = np.linspace(t0, tend, N)              
u = np.reshape(signal.resample(u, N), -1)    
signals = ['Respuestas: Hipotenso, Normotenso e Hipertenso', 'Respuestas Normotenso, Hipotenso y Controlador', 'Respuestas: Normotenso, Hipertenso y Controlador']

# Componentes del sistema cardiovascular y función de transferencia
def cardio(Z, L, R, C):
    num = [L * R, R * Z]
    den = [C * L * R * Z, L * R + L * Z, R * Z]
    sys = ctrl.tf(num, den)
    poles = np.roots(den)
    return sys, poles 

# 1. Hipotenso (caso 1)
Z, L_val, R, C = 0.010, 0.001, 1.00, 3.500
syshipo, L_hipo = cardio(Z, L_val, R, C)
print(f"Función de transferencia del hipotenso (caso 1): {syshipo}\n")
print(f"Polos del sistema: L1 = {L_hipo[0]:.3e}, L2 = {L_hipo[1]:.3e}\n")

# 2. Normotenso (control)
Z, L_val, R, C = 0.010, 0.001, 1.00, 1.500
sysnormo, L_normo = cardio(Z, L_val, R, C)
print(f"Función de transferencia del normotenso (control): {sysnormo}\n")
print(f"Polos del sistema: L1 = {L_normo[0]:.3e}, L2 = {L_normo[1]:.3e}\n")

# 3. Hipertenso (caso 2)
Z, L_val, R, C = 0.010, 0.001, 1.00, 1.000
syshiper, L_hiper = cardio(Z, L_val, R, C)
print(f"Función de transferencia del hipertenso (caso 2): {syshiper}\n")
print(f"Polos del sistema: L1 = {L_hiper[0]:.3e}, L2 = {L_hiper[1]:.3e}\n")

# Componentes del controlador PID
def controlador(kP, kI, kD, sys):
    Cr = 1E-6
    Re = 1 / (Cr * kI)
    Rr = kP * Re
    Ce = kD / Rr
    numPID = [Re * Rr * Ce * Cr, Re * Ce + Rr * Cr, 1]
    denPID = [Re * Cr, 0]
    PID = ctrl.tf(numPID, denPID)
    sysPID = ctrl.feedback(ctrl.series(PID, sys), 1, sign=-1)
    return sysPID

# Controlador Hipotenso
hipoPID = controlador(458.483, 1112094.736, 0.00627, syshipo)
print(f"Función de transferencia del hipotenso en lazo cerrado: {hipoPID}\n")

# Controlador Hipertenso
hiperPID = controlador(126.595, 293327.703, 0.00140, syshiper)
print(f"Función de transferencia del hipertenso en lazo cerrado: {hiperPID}\n")

# Paleta de colores
clr_normo = np.array([139, 30, 45]) / 255   # Normotenso
clr_hipo  = np.array([51, 104, 160]) / 255  # Hipotenso
clr_hiper = np.array([18, 84, 79]) / 255    # Hipertenso
clr_pid   = np.array([215, 110, 20]) / 255  # Controlador PID

# Funciones del sistema en lazo abierto y lazo cerrado
def openloop(t, sys, u):
    _, PAu = ctrl.forced_response(sys, t, u, x0)
    return PAu

def closedloop(t, sysPID, u):
    _, PIDu = ctrl.forced_response(sysPID, t, u, x0)
    return PIDu

# Respuesta de lazo abierto
_, PpN = ctrl.forced_response(sysnormo, t, u, x0)
_, PpL = ctrl.forced_response(syshipo, t, u, x0)
_, PpH = ctrl.forced_response(syshiper, t, u, x0)

# Controlador para lazo cerrado
_, PIDL = ctrl.forced_response(hipoPID, t, PpN, x0)
_, PIDH = ctrl.forced_response(hiperPID, t, PpN, x0)

plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']

# Figura 1: Hipotenso, Normotenso e Hipertenso
fg1 = plt.figure(1, figsize=(w, h))
plt.plot(t, PpL, '-', linewidth=0.5, color=clr_hipo, label=r'$P_p(t)$: Hipotenso')
plt.plot(t, PpN, '-', linewidth=0.5, color=clr_normo, label=r'$P_p(t)$: Normotenso')
plt.plot(t, PpH, '-', linewidth=0.5, color=clr_hiper, label=r'$P_p(t)$: Hipertenso')
plt.grid(False)
plt.xlim(0, 15)
plt.xticks(np.arange(0, 16, 1))
plt.ylim(-0.6, 1.6)
plt.yticks(np.round(np.arange(-0.6, 1.8, 0.2), 1))
plt.xlabel('t [s]')
plt.ylabel('Vi(t) [V]')
plt.legend(bbox_to_anchor=(0.5, 1.08), loc='center', ncol=3, frameon=False)
fg1.savefig('individuos_python.pdf', bbox_inches='tight')  
plt.show()

# Figura 2: Normotenso, Hipotenso y Controlador
fg2 = plt.figure(2, figsize=(w, h))
plt.plot(t, PpN, '-', linewidth=0.5, color=clr_normo, label=r'$P_p(t)$: Normotenso')
plt.plot(t, PpL, '-', linewidth=0.5, color=clr_hipo, label=r'$P_p(t)$: Hipotenso')
plt.plot(t, PIDL, ':', linewidth=2, color=clr_pid, label=r'$PID(t)$: Hipotenso')
plt.grid(False)
plt.xlim(0, 15)
plt.xticks(np.arange(0, 16, 1))
plt.ylim(-0.6, 1.6)
plt.yticks(np.round(np.arange(-0.6, 1.8, 0.2), 1))
plt.xlabel('t [s]')
plt.ylabel('Vi(t) [V]')
plt.legend(bbox_to_anchor=(0.5, 1.08), loc='center', ncol=3, frameon=False)
fg2.savefig('hipotenso_python.pdf', bbox_inches='tight')
plt.show()

# Figura 3: Normotenso, Hipertenso y Controlador
fg3 = plt.figure(3, figsize=(w, h))
plt.plot(t, PpN, '-', linewidth=0.5, color=clr_normo, label=r'$P_p(t)$: Normotenso')
plt.plot(t, PpH, '-', linewidth=0.5, color=clr_hiper, label=r'$P_p(t)$: Hipertenso')
plt.plot(t, PIDH, ':', linewidth=2, color=clr_pid, label=r'$PID(t)$: Hipertenso')
plt.grid(False)
plt.xlim(0, 15)
plt.xticks(np.arange(0, 16, 1))
plt.ylim(-0.6, 1.6)
plt.yticks(np.round(np.arange(-0.6, 1.8, 0.2), 1))
plt.xlabel('t [s]')
plt.ylabel('Vi(t) [V]')
plt.legend(bbox_to_anchor=(0.5, 1.08), loc='center', ncol=3, frameon=False)
fg3.savefig('hipertenso_python.pdf', bbox_inches='tight')
plt.show()