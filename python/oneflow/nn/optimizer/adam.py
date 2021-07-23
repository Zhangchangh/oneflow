from typing import List, Dict, Callable, Union, Iterator, Tuple
import collections
import oneflow as flow
from oneflow.nn.parameter import Parameter
from oneflow.nn.optimizer.optimizer import Optimizer, ParamGroup


class Adam(Optimizer):
    """Implements Adam algorithm.

    It has been proposed in `Adam: A Method for Stochastic Optimization`_.
    The implementation of the L2 penalty follows changes proposed in
    `Decoupled Weight Decay Regularization`_.

    This algorithm can adjust the learning rate of each parameter dynamically according to the 1st-moment estimates and the 2nd-moment estimates of gradient.

    the equation of parameters updating is:

    .. math::

        & V_t = \\beta_1*V_{t-1} + (1-\\beta_1)*grad

        & S_t = \\beta_2*S_{t-1} + (1-\\beta_2)*{grad} \\odot {grad}

        & \\hat{g} = learning\\_rate*\\frac{{V_t}}{\\sqrt{{S_t}}+\\epsilon}

        & param_{new} = param_{old} - \\hat{g}

    Args:
        params (iterable): iterable of parameters to optimize or dicts defining
            parameter groups
        lr (float, optional): learning rate (default: 1e-3)
        betas (Tuple[float, float], optional): coefficients used for computing
            running averages of gradient and its square (default: (0.9, 0.999))
        eps (float, optional): term added to the denominator to improve
            numerical stability (default: 1e-8)
        weight_decay (float, optional): weight decay (L2 penalty) (default: 0)
        scale (float, optional): the scale factor of loss (default: 1.0)

    .. _Adam\\: A Method for Stochastic Optimization:
        https://arxiv.org/abs/1412.6980
    .. _Decoupled Weight Decay Regularization:
        https://arxiv.org/abs/1711.05101

    """

    def __init__(
        self,
        parameters: Union[Iterator[Parameter], List[Dict]],
        lr: float = 0.001,
        betas: Tuple[float, float] = (0.9, 0.999),
        eps: float = 1e-08,
        weight_decay: float = 0,
        amsgrad: bool = False,
        scale: float = 1.0,
    ):
        super().__init__()
        assert lr >= 0.0, f"Invalid learning rate: {lr}"
        assert eps >= 0.0, f"Invalid epsilon value: {eps}"
        assert (
            betas[0] >= 0.0 and betas[0] < 1.0
        ), f"Invalid beta parameter at index 0: {betas[0]}"
        assert (
            betas[1] >= 0.0 and betas[1] < 1.0
        ), f"Invalid beta parameter at index 1: {betas[1]}"
        assert weight_decay >= 0.0, f"Invalid weight_decay value: {weight_decay}"
        assert scale > 0.0, f"Invalid scale factor: {scale}"
        assert amsgrad is False, "Not support AMSGrad now!"
        self._default_options["lr"] = lr
        self._default_options["eps"] = eps
        self._default_options["betas"] = betas
        self._default_options["weight_decay"] = weight_decay
        self._default_options["amsgrad"] = amsgrad
        self._default_options["scale"] = scale
        if isinstance(parameters, collections.abc.Iterator):
            self.param_groups.append(ParamGroup(parameters, self._default_options))
        else:
            for param in parameters:
                self.param_groups.append(ParamGroup(param, self._default_options))
        for param_group in self.param_groups:
            for param in param_group.parameters:
                assert param.is_leaf, "parameters must be leaf tensor"
                self._state[param] = dict()
                self._state[param]["exp_avg"] = flow.zeros_like(param)
                self._state[param]["exp_avg_sq"] = flow.zeros_like(param)
        self._op = (
            flow.builtin_op("adam_update")
            .Input("model")
            .Input("model_diff")
            .Input("m")
            .Input("v")
            .Attr("l1", 0.0)
            .Attr("weight_decay", 0.0)
            .Build()
        )

    def step(self, closure: Callable = None):
        """Performs a single optimization step.

        Args:
            closure (callable, optional): A closure that reevaluates the model
                and returns the loss.
        """
        with flow.no_grad():
            loss = None
            if closure is not None:
                loss = closure()
            for param_group in self.param_groups:
                kwargs = {
                    "learning_rate_val": param_group["lr"],
                    "scale": param_group["scale"],
                    "l2": param_group["weight_decay"],
                    "beta1": param_group["betas"][0],
                    "beta2": param_group["betas"][1],
                    "epsilon": param_group["eps"],
                }
                for param in param_group.parameters:
                    if param.grad is None:
                        continue
                    m_tensor = self._state[param]["exp_avg"]
                    v_tensor = self._state[param]["exp_avg_sq"]
                    self._op(param, param.grad, m_tensor, v_tensor, **kwargs)
            self._state["step"] = self._state["step"] + 1
            return loss
