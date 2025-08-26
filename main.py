#!/usr/bin/env python3
import argparse
import os
import requests


BEEKEEPER_STATE_ENDPOINT = os.environ["BEEKEEPER_STATE_ENDPOINT"]
BEEHIVE_NAME = os.environ["BEEHIVE_NAME"]
RABBITMQ_MANAGEMENT_ENDPOINT = os.environ["RABBITMQ_MANAGEMENT_ENDPOINT"]
RABBITMQ_USERNAME = os.environ["RABBITMQ_USERNAME"]
RABBITMQ_PASSWORD = os.environ["RABBITMQ_PASSWORD"]


def geturl(path):
    return f"{RABBITMQ_MANAGEMENT_ENDPOINT}/api{path}"


def get_rabbitmq_node_users(session):
    r = session.get(geturl("/users"))
    r.raise_for_status()
    return {item["name"] for item in r.json() if item["name"].startswith("node-")}


def add_rabbitmq_users(session, users):
    definitions = {"users": [], "permissions": []}

    for user in users:
        definitions["users"].append({"name": user, "password_hash": "", "tags": ""})

        definitions["permissions"].append(
            {
                "user": user,
                "vhost": "/",
                "configure": "^$",
                "read": "^$",
                "write": "^waggle.msg$",
            }
        )

    r = session.post(geturl("/definitions"), json=definitions)
    r.raise_for_status()


def delete_rabbitmq_users(session, users):
    r = session.post(
        geturl("/users/bulk-delete"),
        json={
            "users": users,
        },
    )
    r.raise_for_status()


def get_node_users_for_beehive():
    users = set()

    # Get node users from beekeeper.
    r = requests.get(BEEKEEPER_STATE_ENDPOINT)
    r.raise_for_status()
    items = r.json()["data"]
    for item in items:
        if item["beehive"] != BEEHIVE_NAME:
            continue
        user = "node-" + item["id"].lower()
        users.add(user)

    # Get node user from admin database.
    r = requests.get("https://auth.sagecontinuum.org/service-node-users")
    r.raise_for_status()
    items = r.json()
    for item in items:
        if item["active"]:
            users.add(item["user"])
        else:
            try:
                users.remove(item["user"])
            except KeyError:
                pass

    return users


def main(dry_run: bool):
    with requests.Session() as session:
        session.auth = (RABBITMQ_USERNAME, RABBITMQ_PASSWORD)

        want_users = get_node_users_for_beehive()
        has_users = get_rabbitmq_node_users(session)
        add_users = want_users - has_users
        remove_users = has_users - want_users

        if len(add_users) == 0:
            print("No users to add.")
        else:
            print("Adding users:")
            for user in sorted(add_users):
                print(user)
            print()

        if len(remove_users) == 0:
            print("No users to remove.")
        else:
            print("Removing users:")
            for user in sorted(remove_users):
                print(user)
            print()

        if dry_run:
            print("Run in dry run mode. Will not make changes!")
            return

        add_rabbitmq_users(session, sorted(want_users))
        delete_rabbitmq_users(session, sorted(remove_users))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    main(
        dry_run=args.dry_run,
    )
