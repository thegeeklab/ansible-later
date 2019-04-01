from ansiblelater import settings


def get_settings(args):
    config = settings.Settings(
        args=args,
    )

    return config
