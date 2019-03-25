local PythonVersions(pyversion="2.7", py="27") = {
    name: "python" + pyversion + "-ansible",
    image: "python:" + pyversion,
    pull: "always",
    environment: {
      PY_COLORS: 1
    },
    commands: [
      "pip install tox -qq",
      "tox -e $(tox -l | grep py" + py + " | xargs | sed 's/ /,/g') -q",
    ],
    depends_on: [
      "clone",
    ],
};

local PipelineTesting = {
  kind: "pipeline",
  name: "testing",
  platform: {
    os: "linux",
    arch: "amd64",
  },
  steps: [
    PythonVersions(pyversion="2.7", py="27"),
    PythonVersions(pyversion="3.5", py="35"),
    PythonVersions(pyversion="3.6", py="36"),
    PythonVersions(pyversion="3.7", py="37"),
    {
      name: "python-flake8",
      image: "python:3.7",
      pull: "always",
      environment: {
        PY_COLORS: 1
      },
      commands: [
        "pip install -r test-requirements.txt -qq",
        "pip install -qq .",
        "flake8 ./ansiblelater",
      ],
      depends_on: [
        "clone",
      ],
    },
    {
      name: "python-bandit",
      image: "python:3.7",
      pull: "always",
      environment: {
        PY_COLORS: 1
      },
      commands: [
        "pip install -r test-requirements.txt -qq",
        "pip install -qq .",
        "bandit -r ./ansiblelater",
      ],
      depends_on: [
        "clone",
      ],
    },
    {
      name: "codecov",
      image: "python:3.7",
      pull: "always",
      environment: {
        PY_COLORS: 1,
        CODECOV_TOKEN: { "from_secret": "codecov_token" },
      },
      commands: [
        "pip install codecov",
        "coverage combine .tox/py*/.coverage",
        "codecov --required"
      ],
      depends_on: [
        "python2.7-ansible",
        "python3.5-ansible",
        "python3.6-ansible",
        "python3.7-ansible"
      ],
    }
  ],
  trigger: {
    ref: ["refs/heads/master", "refs/tags/**", "refs/pull/**"],
  },
};

local PipelineBuild = {
  kind: "pipeline",
  name: "build",
  platform: {
    os: "linux",
    arch: "amd64",
  },
  steps: [
    {
      name: "build",
      image: "python:3.7",
      pull: "always",
      commands: [
        "python setup.py sdist bdist_wheel",
      ]
    },
    {
      name: "checksum",
      image: "alpine",
      pull: "always",
      commands: [
        "apk add --no-cache coreutils",
        "sha256sum -b dist/* > sha256sum.txt"
      ],
    },
    {
      name: "gpg-sign",
      image: "plugins/gpgsign:1",
      pull: "always",
      settings: {
        key: { "from_secret": "gpgsign_key" },
        passphrase: { "from_secret": "gpgsign_passphrase" },
        detach_sign: true,
        files: [ "dist/*" ],
      },
      when: {
        event: {
          exclude: ['pull_request'],
        },
      },
    },
    {
      name: "publish-github",
      image: "plugins/github-release",
      pull: "always",
      settings: {
        api_key: { "from_secret": "github_token"},
        overwrite: true,
        files: ["dist/*", "sha256sum.txt"],
        title: "${DRONE_TAG}",
        note: "CHANGELOG.md",
      },
      when: {
        event: [ "tag" ],
      },
    },
    {
      name: "publish-pypi",
      image: "plugins/pypi",
      pull: "always",
      settings: {
        username: { "from_secret": "pypi_username" },
        password: { "from_secret": "pypi_password" },
        repository: "https://upload.pypi.org/legacy/",
        skip_build: true
      },
      when: {
        event: [ "tag" ],
      },
    },
  ],
  depends_on: [
    "testing",
  ],
  trigger: {
    ref: ["refs/heads/master", "refs/tags/**", "refs/pull/**"],
  },
};

local PipelineNotifications = {
  kind: "pipeline",
  name: "notifications",
  platform: {
    os: "linux",
    arch: "amd64",
  },
  steps: [
    {
      name: "matrix",
      image: "plugins/matrix",
      settings: {
        homeserver: "https://matrix.rknet.org",
        roomid: "MtidqQXWWAtQcByBhH:rknet.org",
        template: "Status: **{{ build.status }}**<br/> Build: [{{ repo.Owner }}/{{ repo.Name }}]({{ build.link }}) ({{ build.branch }}) by {{ build.author }}<br/> Message: {{ build.message }}",
        username: { "from_secret": "matrix_username" },
        password: { "from_secret": "matrix_password" },
      },
    },
  ],
  depends_on: [
    "build",
  ],
  trigger: {
    ref: ["refs/heads/master", "refs/tags/**"],
    status: [ "success", "failure" ],
  },
};

[
  PipelineTesting,
  PipelineBuild,
  PipelineNotifications,
]
