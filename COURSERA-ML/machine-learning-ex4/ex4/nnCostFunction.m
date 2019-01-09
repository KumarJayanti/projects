function [J grad] = nnCostFunction(nn_params, ...
                                   input_layer_size, ...
                                   hidden_layer_size, ...
                                   num_labels, ...
                                   X, y, lambda)
%NNCOSTFUNCTION Implements the neural network cost function for a two layer
%neural network which performs classification
%   [J grad] = NNCOSTFUNCTON(nn_params, hidden_layer_size, num_labels, ...
%   X, y, lambda) computes the cost and gradient of the neural network. The
%   parameters for the neural network are "unrolled" into the vector
%   nn_params and need to be converted back into the weight matrices. 
% 
%   The returned parameter grad should be a "unrolled" vector of the
%   partial derivatives of the neural network.
%

% Reshape nn_params back into the parameters Theta1 and Theta2, the weight matrices
% for our 2 layer neural network
Theta1 = reshape(nn_params(1:hidden_layer_size * (input_layer_size + 1)), ...
                 hidden_layer_size, (input_layer_size + 1));

Theta2 = reshape(nn_params((1 + (hidden_layer_size * (input_layer_size + 1))):end), ...
                 num_labels, (hidden_layer_size + 1));

% Setup some useful variables
m = size(X, 1);
         
% You need to return the following variables correctly 
J = 0;
Theta1_grad = zeros(size(Theta1));
Theta2_grad = zeros(size(Theta2));

% ====================== YOUR CODE HERE ======================
% Instructions: You should complete the code by working through the
%               following parts.
%
% Part 1: Feedforward the neural network and return the cost in the
%         variable J. After implementing Part 1, you can verify that your
%         cost function computation is correct by verifying the cost
%         computed in ex4.m
%
% Part 2: Implement the backpropagation algorithm to compute the gradients
%         Theta1_grad and Theta2_grad. You should return the partial derivatives of
%         the cost function with respect to Theta1 and Theta2 in Theta1_grad and
%         Theta2_grad, respectively. After implementing Part 2, you can check
%         that your implementation is correct by running checkNNGradients
%
%         Note: The vector y passed into the function is a vector of labels
%               containing values from 1..K. You need to map this vector into a 
%               binary vector of 1's and 0's to be used with the neural network
%               cost function.
%
%         Hint: We recommend implementing backpropagation using a for-loop
%               over the training examples if you are implementing it for the 
%               first time.
%
% Part 3: Implement regularization with the cost function and gradients.
%
%         Hint: You can implement this around the code for
%               backpropagation. That is, you can compute the gradients for
%               the regularization separately and then add them to Theta1_grad
%               and Theta2_grad from Part 2.
%
% Add ones to the X data matrix
% 5000 X 401 matrix
X = [ones(m, 1) X];

% 25 x 401 * 401 : 5000 = 25 x 5000
z2 = Theta1 * X'
a2 = sigmoid(z2);

% add ones to  a2
ones_row = ones(size(a2,2),1)';
a2 = [ones_row; a2];
z3 = Theta2 * a2;
z3Trans = z3';

% hx = 5000 x 10
hx = sigmoid(z3Trans);

delta3 = zeros(num_labels, m);
delta2 = zeros(hidden_layer_size + 1,m);

for k = 1:num_labels,
        yik = (y == k);
        J = J + sum(-yik' * log(hx(:,k)) - (1 - yik')*log(1 - hx(:,k)));
% BackPropagation
        delta3(k,:) = hx(:,k) - yik;
end

J = J / m;
reg =  sum(sum(Theta1(:,2:end).^2)) + sum(sum(Theta2(:,2:end).^2));
reg = lambda * reg / (2*m);
J = J + reg;

% delta3 : 10 x 5000 
% Theta2 : 10 x 26
% d2temp = 26 x 5000
d2temp = Theta2' * delta3;

% delta2 = 25 x 5000
delta2 = d2temp(2:end,:) .* sigmoidGradient(z2);

Theta1_grad = delta2 * X;
Theta2_grad = delta3 * a2';

Theta1_grad =  Theta1_grad / m;
Theta2_grad =  Theta2_grad / m;

% regularize
T1g_temp = [zeros(size(Theta1_grad,1),1) Theta1_grad(:,2:end)];
Theta1_grad =  Theta1_grad +  (lambda/m) .* T1g_temp;

T2g_temp = [zeros(size(Theta2_grad,1),1) Theta2_grad(:,2:end)];
Theta2_grad =  Theta2_grad +  (lambda /m)  .* T2g_temp;

% -------------------------------------------------------------

% =========================================================================

% Unroll gradients
grad = [Theta1_grad(:) ; Theta2_grad(:)];


end
