#!/usr/bin/env python3
import os
import requests


BEEKEEPER_STATE_ENDPOINT = os.environ["BEEKEEPER_STATE_ENDPOINT"]
BEEHIVE_NAME = os.environ["BEEHIVE_NAME"]
RABBITMQ_MANAGEMENT_ENDPOINT = os.environ['RABBITMQ_MANAGEMENT_ENDPOINT']
RABBITMQ_USERNAME = os.environ["RABBITMQ_USERNAME"]
RABBITMQ_PASSWORD = os.environ["RABBITMQ_PASSWORD"]


def geturl(path):
    return f"{RABBITMQ_MANAGEMENT_ENDPOINT}{path}"


def get_rabbitmq_node_users(session):
    r = session.get(geturl("/users"))
    r.raise_for_status()
    return {item["name"] for item in r.json() if item["name"].startswith("node-")}


def add_rabbitmq_users(session, users):
    definitions = {"users": [], "permissions": []}

    for user in users:
        definitions["users"].append({
            "name": user,
            "password_hash": "",
            "tags": ""
        })

        definitions["permissions"].append({
            "user": user,
            "vhost": "/",
            "configure": "^$",
            "read": "^$",
            "write": "^waggle.msg$",
        })

    r = session.post(geturl("/definitions"), json=definitions)
    r.raise_for_status()


def delete_rabbitmq_users(session, users):
    r = session.post(geturl("/users/bulk-delete"), json={
        "users": users,
    })
    r.raise_for_status()


def get_node_users_for_beehive():
    r = requests.get(BEEKEEPER_STATE_ENDPOINT)
    r.raise_for_status()
    items = r.json()["data"]
    return {"node-"+item["id"].lower() for item in items if item["beehive"] == BEEHIVE_NAME}


def main():
    with requests.Session() as session:
        session.auth = (RABBITMQ_USERNAME, RABBITMQ_PASSWORD)

        want_users = get_node_users_for_beehive()
        has_users = get_rabbitmq_node_users(session)
        delete_users = has_users - want_users

        print("want:", sorted(want_users), flush=True)
        print("has:", sorted(has_users), flush=True)
        print("add:", sorted(want_users - has_users), flush=True)
        print("delete:", sorted(delete_users), flush=True)

        add_rabbitmq_users(session, sorted(want_users))
        delete_rabbitmq_users(session, sorted(delete_users))


if __name__ == "__main__":
    main()
