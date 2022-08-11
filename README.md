# Update RabbitMQ users from Beekeeper

This is script syncs nodes in Beekeeper to specific RabbitMQ user accounts on a Beehive. It is primarily intended to be run as a cronjob.

This script expects the following env vars as configuration:

* `BEEKEEPER_STATE_ENDPOINT`: Endpoint for Beekeeper state API.
* `BEEHIVE_NAME`:  Name of Beehive.
* `RABBITMQ_MANAGEMENT_ENDPOINT`: Endpoint for Beehive's RabbitMQ management API.
* `RABBITMQ_USERNAME`:  Beehive's RabbitMQ management username.
* `RABBITMQ_PASSWORD`: Beehive's RabbitMQ management password.
