import oneflow.framework.session_context as session_ctx
import oneflow.framework.scope_util as scope_util


class DistributeStrategy(object):
    def __init__(self, is_mirrored):
        self.is_mirrored_ = is_mirrored
        self.scope_context_ = None
        sess = session_ctx.GetDefaultSession()
        if sess.is_running and (
            not sess.has_empty_is_mirrored_strategy_enabled_stack()
        ):

            def BuildScope(old_scope, builder):
                return builder.BuildScopeWithNewIsMirrored(old_scope, is_mirrored)

            self.scope_context_ = scope_util.ScopeContext(
                scope_util.MakeScope(BuildScope)
            )

    def __enter__(self, *argc, **kwarg):
        PushMirroredStrategyEnabled(self.is_mirrored_)
        if self.scope_context_ is not None:
            self.scope_context_.__enter__(*argc, **kwarg)

    def __exit__(self, *argc, **kwarg):
        PopMirroredStrategyEnabled()
        if self.scope_context_ is not None:
            self.scope_context_.__exit__(*argc, **kwarg)


def PushMirroredStrategyEnabled(val):
    session_ctx.GetDefaultSession().push_mirrored_strategy_enabled(val)


def IsMirroredStrategyEnabled():
    return session_ctx.GetDefaultSession().is_mirrored_strategy_enabled()


def IsConsistentStrategyEnabled():
    return session_ctx.GetDefaultSession().is_consistent_strategy_enabled()


def PopMirroredStrategyEnabled():
    session_ctx.GetDefaultSession().pop_mirrored_strategy_enabled()
