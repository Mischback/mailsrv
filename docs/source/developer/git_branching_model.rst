
###################
Git Branching Model
###################

The repository loosely follows a Git branching model as described by
Vincent Driessen
`here <https://nvie.com/posts/a-successful-git-branching-model/>`_

The repository's default branch is **development**, which will always have the
latest code contributions that have reached a *stable state*.

*Feature Branches* should branch off from ``development`` and be merged back
into ``development`` once they reach a *stable state*.

The repository is set up to use ``dependabot`` for automatic updates of the
app's dependencies. ``dependabot`` will also work against the ``development``
branch.

The repository's ``main`` branch is used to track the actual releases. Commits
in ``main`` should be tagged appropriately ::

  *  [main, tag: v1.0.0]
  |\
  | *  [development]
  | |\
  | | *  [example-feature]
  | | *
  | | *
  | |/
  | *
  | *
  |/
  *

The repository provides Continuous Integration by GitHub Actions.
