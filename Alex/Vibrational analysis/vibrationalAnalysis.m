%Vibrational analysis
%Alex Berresford

clear all
close all
%constants
height = 180*10^(-3);%length of cubesat -mm

mass = 12; %mass of cubesat, distributed evenly between floors - kg
    %estimated off of 1.5kg/1U of cubesat
    
floors = 4; %number of "floors" of the cubesat

props = 4; %vertical supports per layer of depth

I = 3.385*10^-11; %second moment of area of prop - m^4
    %Currently for 5mm x 5mm x 2mm L section

E = 73 * 10^9; %Youngs modulus for prop material - Pa
    %Currenly for aluminium

L = height/(floors - 1); %Length of individual prop - m

K = ((props^2)*(12*E*I))/(L^3); %"Spring constant" per floor - N/m

m = mass/floors; %mass per floor - kg
                             %modelled as each internal "floor" having
                             %twice the weight

%Sets up M and K matrices
[Kmatrix,Mmatrix] = fillMatrices(floors,K,m);

%Finds natural frequencies of the system
natFreqs = sqrt(eig(Kmatrix)/(m))/(2*pi);

%Assign PSD points
%From RocketLab electron user payload guide
PSDpoints = [0 20 50 150 300 800 2000; 
            0.013 0.013 0.03 0.03 0.005 0.005 0.01];

signals = PSDrandom(PSDpoints,1000);

%Simulate

%number of time steps
n = 200000;
%time step
dt = 0.00025;

%Simulation time = n*t

%find accelerations of base plate from random signals
accelerations = getAcceleration(signals,n,dt);

%initialise internalAccel
internalAccel = transpose([0 0 0 0 ]);
vel = [0 0];

%initialise arrays

displacements = zeros([floors,n]);
time = zeros(1,n);
%accelerations = zeros(1,n); %impulse response
%accelerations(1) = 1;
%find displacements 

for step = 1:n

    
     time(step) = step*dt;
     aVector = transpose([accelerations(step) 0 0 0 ]);

    if step == 1

        vel = (internalAccel + aVector)*dt;
        displacements(:,step) = -vel*dt;
        

    end
    
    if step > 1

        internalAccel = (Mmatrix\Kmatrix*displacements(:,step - 1)) ;
        vel = vel - (internalAccel + aVector)*dt; 
        displacements(:,step) = displacements(:,step - 1) + vel*dt -displacements(1,step - 1);
        %displacements(:,step) = displacements(:,step) - displacements(1,step);
        
    end

end




%validation
val_displacements = zeros(1,n);

for step = 1:n

    val_displacements(step) = (m*accelerations(step)*step*dt)/(mass*natFreqs(2)*2*pi);

end




[maxDisplacement,I] = max(abs(displacements),[],"all");


colours = ["c","g","y","m","r","b","k"];
for c = 1:floors
 
     plot(displacements(c,:),time,colours(c));
     hold on
end
xlabel("Displacement/m","FontSize",20)
ylabel("Time/s","FontSize",20)
legend("Floor 1","Floor 2","Floor 3","Floor 4","Floor 5")
title("Simulation of CubeSat floor displacements during Launch","FontSize",22)

%plot validation
%plot(val_displacements,time,"b");

figure

plot(accelerations,time)