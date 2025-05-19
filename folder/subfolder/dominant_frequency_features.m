function [maxfreq, maxval, maxratio, sumrange] = dominant_frequency_features(data, fs, cutoff)
% This function estimates the dominant frequency of each channel (COLUMN) of the
% input data.  First, it calculates the power spectrum of the signal.  Then it finds the 
% maximum frequency over as well as the "energy" at that point; options below allow normalization
% by the total or mean energy.  Note this does not restrict the range of frequencies to search 
% for a maximum.
% 
% data         matrix containing data where each COLUMN corresponds to a channel
% fs           sampling rate (Hz)
% cutoff       cutoff frequency (Hz)
% maxfreq      frequency at which the max of the spectrum occurs (Hz) (ROW VECTOR)
% maxratio     ratio of the energy of the maximum to the total energy (ROW VECTOR)
%Copyright (c) 2016, MathWorks, Inc. 


%  nfft = 2^nextpow2(npoints*padfactor);
nfft = 2^nextpow2(length(data)); %2^16;
f = fs/2*linspace(0,1,nfft/2);
cutoffidx = length(find(f <= cutoff));
f = f(1:cutoffidx);

% calculate the power spectrum using FFT method
 data = data-mean(data);
datafft = fft(data,nfft);
ps = abs(datafft/nfft); 
% ps = abs(datafft); 

% keep only the non-redundant portion
ps = ps(1:cutoffidx,:);

% locate max value below cutoff
[maxval(1), maxind] = max(ps(1:round(cutoffidx/5)));
maxfreq(1) = f(maxind);
% calculate peak energy by summing energy from maxfreq-delta to maxfreq+delta
% then normalize by total energy below cutoff
delta = 5;  % Hz
maxratio(1) = 0;
maxrange = f>=maxfreq(1)-delta & f<=maxfreq(1)+delta;
maxratio(1) = sum(ps(maxrange));
sumrange(1)=sum(ps(1:round(cutoffidx/5)));

[maxval(2), maxind] = max(ps(round(cutoffidx/5)+1:round(2*cutoffidx/5)));
maxfreq(2) = f(maxind+round(cutoffidx/5));
% calculate peak energy by summing energy from maxfreq-delta to maxfreq+delta
% then normalize by total energy below cutoff
delta = 5;  % Hz
maxratio(2) = 0;
maxrange = f>=maxfreq(2)-delta & f<=maxfreq(2)+delta;
maxratio(2) = sum(ps(maxrange));
sumrange(2)=sum(ps(round(cutoffidx/5)+1:round(2*cutoffidx/5)));

[maxval(3), maxind] = max(ps(round(2*cutoffidx/5)+1:round(3*cutoffidx/5)));
maxfreq(3) = f(maxind+round(2*cutoffidx/5));
% calculate peak energy by summing energy from maxfreq-delta to maxfreq+delta
% then normalize by total energy below cutoff
delta = 5;  % Hz
maxratio(3) = 0;
maxrange = f>=maxfreq(3)-delta & f<=maxfreq(3)+delta;
maxratio(3) = sum(ps(maxrange));
sumrange(3)=sum(ps(round(2*cutoffidx/5)+1:round(3*cutoffidx/5)));

[maxval(4), maxind] = max(ps(round(3*cutoffidx/5)+1:round(4*cutoffidx/5)));
maxfreq(4) = f(maxind+round(3*cutoffidx/5));
% calculate peak energy by summing energy from maxfreq-delta to maxfreq+delta
% then normalize by total energy below cutoff
delta = 5;  % Hz
maxratio(4) = 0;
maxrange = f>=maxfreq(4)-delta & f<=maxfreq(4)+delta;
maxratio(4) = sum(ps(maxrange));
sumrange(4)=sum(ps(round(3*cutoffidx/5)+1:round(4*cutoffidx/5)));

[maxval(5), maxind] = max(ps(round(4*cutoffidx/5)+1:end-5));
maxfreq(5) = f(maxind+round(4*cutoffidx/5));
% calculate peak energy by summing energy from maxfreq-delta to maxfreq+delta
% then normalize by total energy below cutoff
delta = 5;  % Hz
maxratio(5) = 0;
maxrange = f>=maxfreq(5)-delta & f<=maxfreq(5)+delta;
maxratio(5) = sum(ps(maxrange));
sumrange(5)=sum(ps(round(4*cutoffidx/5)+1:cutoffidx));
