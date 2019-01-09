function [J, grad] = costFunctionReg(theta, X, y, lambda)
%COSTFUNCTIONREG Compute cost and gradient for logistic regression with regularization
%   J = COSTFUNCTIONREG(theta, X, y, lambda) computes the cost of using
%   theta as the parameter for regularized logistic regression and the
%   gradient of the cost w.r.t. to the parameters. 

% Initialize some useful values
m = length(y); % number of training examples

% You need to return the following variables correctly 
J = 0;
grad = zeros(size(theta));

% ====================== YOUR CODE HERE ======================
% Instructions: Compute the cost of a particular choice of theta.
%               You should set J to the cost.
%               Compute the partial derivatives and set grad to the partial
%               derivatives of the cost w.r.t. each parameter in theta

t = 1/m;
ltm = lambda / (2 * m);
sum = 0;
gradt = grad;
for i = 1:m,
    hxi = sigmoid(theta' * X(i,:)');
    term1 = -y(i) * log(hxi);
    term2 = (1 - y(i)) * log(1 - hxi);
    term = term1 - term2;
    sum = sum + term;
    prod = (hxi - y(i)) * X(i,:)';
    gradt = gradt + prod;
end;
J = t * sum;
grad = t * gradt;

L = 0;
n = size(theta,1);
for k = 1:n,
   L = L + (theta(k))^2;
end
 
J = J + (ltm * L);

J = round(J/0.001) * 0.001;

lm = lambda / m;

for k = 2:n,
    grad(k) = grad(k) + (lm * theta(k));    
end

% =============================================================

end
