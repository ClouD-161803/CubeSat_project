function [accelerations] = getAcceleration(signals,n,t)
%returns accelerations of base plate from random signals
%signals
    %3 by m array with each row representing
        %frequency
        %magnitude
        %phase
%n - number of time steps
%t - time step (s)

%initialise acceleration vector

accelerations = zeros([1,length(signals)]);

for i = 1:n
    a = 0;

    for j = 1:length(signals)

        f = signals(1,j);
        m = signals(2,j);
        p = signals(3,j);

        a = a + m*sin(f*i*t + p);

    end

    accelerations(i) = a;
    
end

end