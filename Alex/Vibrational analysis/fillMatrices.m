function [Kmatrix,Mmatrix] = fillMatrices(floors,K,m)
%fillMatrices
%sets up matrices for vibrational analysis
Kmatrix = zeros([floors,floors]);
Mmatrix = zeros([floors,floors]);

for i = 1:floors

    for j = 1:floors

        if i==j

            Kmatrix(i,j) = 2*K;
            Mmatrix(i,j) = m;

        end
        
        if j+1==i || j-1 == i
            Kmatrix(i,j) = -K;

        end

        if j==i && i==1
            Kmatrix(i,j) = K;
            Mmatrix(i,j) = m;
        end

        if i==floors && j == floors
            Kmatrix(i,j) = K;
        end
    end
end
end