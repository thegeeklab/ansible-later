local PythonVersions(pyversion="2.7", py="27") = {
    name: "python" + pyversion,
    image: "python:" + pyversion,
    pull: "always",
    commands: [
      "pip install tox -q",
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
    PythonVersions(pyversion="2.7"),
    PythonVersions(pyversion="3.5"),
    PythonVersions(pyversion="3.6"),
    PythonVersions(pyversion="3.7"),
  ],
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
    },
    {
      name: "publish-github",
      image: "plugins/github-release",
      pull: "always",
      settings: {
        api_key: { "from_secret": "github_token"},
        files: ["dist/*", "sha256sum.txt"],
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
    event: [ "push", "tag" ],
    status: [ "success", "failure" ],
  },
};

[
  PipelineTesting,
  PipelineBuild,
  PipelineNotifications,
]
