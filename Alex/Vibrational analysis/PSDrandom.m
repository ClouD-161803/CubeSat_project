function [randomSignals] = PSDrandom(points,num)
%Returns a set of random frequencies, phases and powers based on the input
%points of a PSD
%points 2*n array representing points on a PSD 
%num an int representing number of desired random signals


randomSignals = zeros([3,num]);
g = 9.81;

%Find maximum frequency to test
range = points(1,length(points));

for i = 1:num
    
    j = 1;

    %find random frequency in range of PSD
    frequency = range*rand;
    %convert to radians and assign to signal
    randomSignals(1,i) = 2*pi*frequency;

    while j >= 1
        
        if frequency >= points(1,j) && frequency <= points(1,j+1)

            %linearly interpolates acceleration from PSD points 
            acceleration = g *(points(2,j)+ ((frequency-points(1,j))/(points(1,j+1)-points(1,j))) * (points(2,j+1)-points(2,j)));
            
            randomSignals(2,i) = sqrt(acceleration);

            break
        end
        j = j + 1;
        

    end

    %random phase
    phase = 2*pi*rand;
    randomSignals(3,i) = phase;

end


end