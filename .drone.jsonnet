local PipelineEmvironment(pyversion="2.7", ansibleversion="2.4") = {
    name: "ansible" + ansibleversion,
    image: "python:" + pyversion,
    pull: "always",
    commands: [
      "pip install -q ansible~=" +  ansibleversion,
      "pip install -q -r tests/requirements.txt",
      "pip install -q .",
      "ansible-later -c tests/config/config.ini tests/data/yaml_success.yml"
    ],
    depends_on: [
      "clone",
    ],
};

local PipelineTesting(pyversion="2.7") = {
  kind: "pipeline",
  name: "python-" + pyversion,
  platform: {
    os: "linux",
    arch: "amd64",
  },
  steps: [
    PipelineEmvironment(pyversion, ansibleversion="2.4"),
    PipelineEmvironment(pyversion, ansibleversion="2.5"),
    PipelineEmvironment(pyversion, ansibleversion="2.6"),
    PipelineEmvironment(pyversion, ansibleversion="2.7"),
  ],
};

local PipelineBuild(depends_on=[]) = {
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
  depends_on: depends_on,
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
    status: [ "success", "failure", "skipped" ],
  },
};

[
  PipelineTesting(pyversion="2.7"),
  PipelineTesting(pyversion="3.5"),
  PipelineTesting(pyversion="3.6"),
  PipelineTesting(pyversion="3.7"),
  PipelineBuild(depends_on=[
    'python-2.7',
    'python-3.5',
    'python-3.6',
    'python-3.7',
  ]),
  PipelineNotifications,
]
