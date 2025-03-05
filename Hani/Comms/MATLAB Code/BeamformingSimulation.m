array = phased.ULA('NumElements', 8, 'ElementSpacing', 0.5); % 8 elements, 0.5-wavelength spacing

fs = 1e3; % Sampling frequency
t = 0:1/fs:1-1/fs; % Time vector
signal = sin(2*pi*100*t); % 100 Hz sine wave

beamformer = phased.Beamformer( ...
    'SensorArray', array, ...
    'OperatingFrequency', 1e9, ... % 1 GHz
    'Direction', [30; 0], ... % 30° azimuth, 0° elevation
    'WeightsOutputPort', true);
outputSignal = beamformer(signal);

pattern(array, 1e9); % Visualize at 1 GHz frequency
