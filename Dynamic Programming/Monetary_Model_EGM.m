%% Compute Policies for the Monetary Model Using EGM
% This script computes the optimal policy functions using the endogenous
% grid method (EGM), computes consumption policies, and then plots the
% policy functions for next‐period money and consumption separately.

clear; close all; clc;

%% 1. Model and Grid Parameters
number_of_states = 2;                 % Number of shock states
% [z, QQ] = tauchen(number_of_states, 0, 0.2, 0.2042, 3);
% theta = exp(z);                       % Shock multipliers

theta = [0.74 1.36];
QQ = [0.73 0.27; 0.27 0.73];


bet   = 0.98;                         % Discount factor
sig   = 2;                            % Risk aversion (CRRA)
y     = 1;                            % Endowment
gama  = 0.02;                         % Inflation rate
msup  = 1;                            % Money supply
tau   = 0.0234;                       % Tau transfer

Np    = 100;                          % Number of grid points for money
mlow  = y + tau;                      % Lower bound for money grid
mup   = 2.5;                          % Upper bound for money grid
mgrid = linspace(mlow, mup, Np)';       % Column vector of money values

Nk    = 1000;                         % Maximum number of EGM iterations
g0    = mgrid;                        % Initial guess for policy (next‐period money)

% Initialize the policy function: dimensions [Np x Nk x number_of_states]
g = zeros(Np, Nk, number_of_states);
for s = 1:number_of_states
    g(:,1,s) = g0;
end

%% 2. EGM Iteration: Compute Optimal Policy Functions
for iter = 1:Nk-1
    % Compute marginal utilities for each state:
    % Consumption: c = m/(1+gama) + y + tau - g(m, theta)
    mc = zeros(Np, number_of_states);
    for s = 1:number_of_states
        mc(:,s) = theta(s) * ( mgrid/(1+gama) + y + tau - g(:,iter,s) ).^(-sig);
    end

    % Compute discounted continuation value:
    vf = bet/(1+gama) * mc * QQ';

    % Invert the Euler equation to obtain candidate next‐period money:
    ms = zeros(Np, number_of_states);
    for s = 1:number_of_states
        ms(:,s) = ((vf(:,s)/theta(s)).^(-1/sig) + mgrid - y - tau) * (1+gama);
    end

    % Update policy function using interpolation over mgrid:
    for i = 1:Np
        for s = 1:number_of_states
            if mgrid(i) <= ms(1,s)
                g(i,iter+1,s) = mgrid(1);
            elseif mgrid(i) >= ms(end,s)
                g(i,iter+1,s) = mgrid(end);
            else
                g(i,iter+1,s) = LIP(ms(:,s), mgrid, mgrid(i));
            end
        end
    end

    % Check convergence based on the last state's policy
    policy_change = abs(g(:,iter+1,number_of_states) - g(:,iter,number_of_states));
    if max(policy_change) <= 1e-8
        fprintf('EGM convergence achieved after %d iterations.\n', iter);
        go = g(:,iter+1,:);
        break;
    end
end

% Extract final optimal policy functions for next-period money.
gopt = zeros(Np, number_of_states);
for s = 1:number_of_states
    gopt(:,s) = go(:,1,s);
end

%% 3. Compute Consumption Policy Functions
% Budget constraint: m' = m/(1+gama) - c + y + tau, hence:
% c = m/(1+gama) + y + tau - m'
cpolicy1 = mgrid/(1+gama) + y + tau - gopt(:,1);
cpolicy2 = mgrid/(1+gama) + y + tau - gopt(:,2);

%% 4. Plot Policy Functions for Next-Period Money (Wealth)
figure;
plot(mgrid, gopt(:,1), 'b-', mgrid, gopt(:,2), 'r-', mgrid, mgrid, 'k--', 'LineWidth',1.5);
grid on;
xlabel('$m$', 'Interpreter', 'latex', 'FontSize', 10);
ylabel('$$m''$$', 'Interpreter', 'latex', 'FontSize', 10);
title('Policy Functions for Next-Period Money');
legend('$g(m,\theta_1)$', '$g(m,\theta_2)$', '45 Line', 'Interpreter','latex', 'Location','Northwest', 'FontSize',10);

% Policy Functions for Consumption
figure;
plot(mgrid, cpolicy1, 'b-', mgrid, cpolicy2, 'r-', 'LineWidth',1.5);
grid on;
xlabel('$m$', 'Interpreter', 'latex', 'FontSize', 10);
ylabel('Consumption, $c$', 'Interpreter', 'latex', 'FontSize', 10);
title('Consumption Policy Functions');
legend('$c(m,\theta_1)$', '$c(m,\theta_2)$', 'Interpreter','latex', 'Location','best', 'FontSize',10);


%% Find the Invariant Distribution


% Implementing discretization of distributions

g1 = gopt(:,1);
g2 = gopt(:,2);

Dp    = 2*Np - 1;               % number of points on grid of F
dgrid = linspace(mlow,mup,Dp);  % grid for distributions (F's)  

Fini  = (dgrid-dgrid(1))/(dgrid(Dp)-dgrid(1)); % initial guess of uniform F

% Solve for ergodic distribution
Prob                     = QQ-eye(number_of_states);
Prob(:,number_of_states) = ones(number_of_states,1);

a                        = zeros(number_of_states,1);
a(number_of_states)      = 1;
epr                      = linsolve(Prob',a);


Dk      = 10000; % maximal number iterations
F1      = zeros(Dp,Dk); 
F1(:,1) = epr(1)*Fini;

F2      = zeros(Dp,Dk);
F2(:,1) = epr(2)*Fini;

for i=1:Dk-1
    for j=1:Dp
        if dgrid(j) < g1(1)
            F1(j,i+1) = 0;
        elseif dgrid(j) > g1(Np)
            F1(j,i+1) = epr(1); % Psi(m, theta1) -> 0.5, m -> inf
        else 
            [g1r, index_1] = unique(g1, 'last');
            F1(j,i+1) = interp1(dgrid, F1(:,i), ...
                interp1(g1r, mgrid(index_1),dgrid(j),'linear'), ...
                "linear");
        end
    end
    h = max(abs(F1(:,i+1)-F1(:,i)));

    if h <= 1e-8
        F1N = F1(:,i+1);
        disp('Distribution convergence achieved');
        disp(i);
        break
    end
end


for i=1:Dk-1
    for j=1:Dp
        if dgrid(j) < g2(1)
            F2(j,i+1) = 0;
        elseif dgrid(j) > g2(Np)
            F2(j,i+1) = epr(2); % Psi(m, theta2) -> ergodicPr(theta2), m -> inf
        else 
            [g2r, index_2] = unique(g2, 'last');
            F2(j,i+1) = interp1(dgrid, F2(:,i), ...
                interp1(g2r, mgrid(index_2),dgrid(j),'linear'), ...
                "linear");
        end
    end
    h = max(abs(F2(:,i+1)-F2(:,i)));

    if h <= 1e-8
        F2N = F2(:,i+1);
        disp('Distribution convergence achieved');
        disp(i);
        break
    end
end


%% Plot the results

figure;

subplot(1,2,1); 
plot(dgrid, F1N, 'r-', 'LineWidth', 1.5);
title('Distribution of $\theta_1$', 'Interpreter', 'latex');
xlabel('$m$', 'Interpreter', 'latex');
ylabel('Shock1 Distribution');
grid on;


% Shock1 - Distribution
subplot(1,2,2);
plot(dgrid, F2N, 'r-', 'LineWidth', 1.5);
title('Distribution of $\theta_2$', 'Interpreter', 'latex');
xlabel('$m$', 'Interpreter', 'latex');
ylabel('Shock1 Distribution');
grid on;


%% Compute the economic distribution

Dk = 1000;

F1 = zeros(Dp,Dk);
F1(:,1) = epr(1)*Fini;


F2 = zeros(Dp,Dk);
F2(:,1) = epr(2)*Fini;

for i=1:Dk-1
    for j = 1:Dp
        if dgrid(j) < g1(1)
            m1 = 0;
        elseif dgrid(j) > g1(Np)
            m1= epr(1);
        else
            [g1r,index_1] = unique(g1,"last");
            m1 = interp1(dgrid,F1(:,i), ...
                interp1(g1r,mgrid(index_1),dgrid(j),"linear"));
        end
        
        if dgrid(j) < g2(1)
            m2 = 0;
        elseif dgrid(j) > g2(Np)
            m2 = epr(2);
        else
            [g2r,index_2] = unique(g2,"last");
            m2 = interp1(dgrid,F2(:,i), ...
                interp1(g2r,mgrid(index_2),dgrid(j),"linear"),"linear");
        end
        
        F1(j,i+1) = m1*QQ(1,1) + m2*QQ(2,1);
        F2(j,i+1) = m1*QQ(1,2) + m2*QQ(2,2);

    end
    h = max(abs(F1(:,i+1)-F1(:,i))+abs(F2(:,i+1)-F2(:,i)));
    if h <= 1e-10
        F1N = F1(:,i+1);
        F2N = F2(:,i+1);
        break
    end
end

%% Plot the results

figure;

subplot(2,1,1);
plot(dgrid, F1N, 'r-', 'LineWidth', 1.5);
title('Distribution of $\theta_1$', 'Interpreter', 'latex');
xlabel('$m$', 'Interpreter', 'latex');
ylabel('Cumulative Probability');
grid on;

subplot(2,1,2);
plot(dgrid, F2N, 'r-', 'LineWidth', 1.5);
title('Distribution of $\theta_2$', 'Interpreter', 'latex');
xlabel('$m$', 'Interpreter', 'latex');
ylabel('Cumulative Probability');
grid on;



%% 5. Compute the Stationary (Long-Run) Money Demand
F_total = F1N + F2N;  % This is the overall (unconditional) CDF of money holdings.

%    E[m] = m_low + ∫_{m_low}^{m_up} [1 - F(m)] dm
money_demand = mlow + trapz(dgrid, 1 - F_total);

fprintf('Money demand (expected money) = %f\n', money_demand);



%% Helper Function


function y0 = LIP(xvec, yvec, x0)
    % LIP - Linear Interpolation Function
    %
    % Computes interpolated values for given query points x0 using 
    % the data (xvec, yvec) with linear interpolation.
    %
    % Inputs:
    %   xvec - A column vector of x-coordinates (sorted in ascending order)
    %   yvec - A column vector of corresponding y-coordinates
    %   x0   - A column vector of points at which to interpolate
    %
    % Output:
    %   y0   - A column vector of interpolated values

    % Validate inputs
    if ~isvector(xvec) || ~isvector(yvec) || ~isvector(x0)
        error('All inputs must be vectors.');
    end
    
    if length(xvec) ~= length(yvec)
        error('xvec and yvec must have the same length.');
    end
    
    xvec = xvec(:); % Ensure column vector
    yvec = yvec(:); % Ensure column vector
    x0   = x0(:);   % Ensure column vector
    
    n = length(xvec);
    m = length(x0);
    y0 = zeros(m, 1);

    for k = 1:m
        if x0(k) < xvec(1) || x0(k) > xvec(n)
            warning('Input out of grid. Returning NaN.');
            y0(k) = NaN; % MATLAB equivalent of miss(1,1)
            continue;
        end
        
        if x0(k) == xvec(1)
            y0(k) = yvec(1);
        elseif x0(k) == xvec(n)
            y0(k) = yvec(n);
        else
            % Find the largest index j such that xvec(j) <= x0(k)
            j = find(xvec <= x0(k), 1, 'last');
            
            % Compute linear interpolation
            y0(k) = yvec(j) + ((yvec(j+1) - yvec(j)) / (xvec(j+1) - xvec(j))) * (x0(k) - xvec(j));
        end
    end
end