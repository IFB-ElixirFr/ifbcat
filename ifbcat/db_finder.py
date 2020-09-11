import os
import subprocess


def get_db_ip():
    result = subprocess.run(
        [
            "docker",
            "ps",
            "-f",
            "name=%s" % get_guessed_container_name(),
            "-q",
        ],
        stdout=subprocess.PIPE,
    )
    ids = result.stdout.decode('utf-8').strip().split('\n')
    if len(ids) > 1:
        raise Exception("Can't find the DB, too much match")
    if len(ids) == 0 or len(ids[0]) == 0:
        result = subprocess.run(
            [
                "docker",
                "ps",
                "-f",
                "name=_db",
                "-q",
            ],
            stdout=subprocess.PIPE,
        )
        ids = result.stdout.decode('utf-8').strip().split('\n')
        if len(ids) > 1:
            raise Exception(
                "Can't find the DB, couldn't guess container name (tried '%s'), "
                "and too much match with '_db'" % get_guessed_container_name()
            )
        if len(ids) == 0 or len(ids[0]) == 0:
            raise Exception("Can't find the DB")
    result = subprocess.run(
        [
            "docker",
            "inspect",
            "-f",
            "'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'",
            ids[0],
        ],
        stdout=subprocess.PIPE,
    )
    return result.stdout.decode('utf-8').strip().replace("'", "")


def get_guessed_container_name():
    return str(os.path.dirname(__file__).split(os.path.sep)[-2]).lower().replace('-', '') + "_db"


if __name__ == "__main__":
    print(get_db_ip())
