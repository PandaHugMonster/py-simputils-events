#!/bin/env python3
import logging

from simputils.events.helpers.generic import create_distributed_event_manager
from simputils.events.modules.gcp.adapters.GooglePubSubAdapter import GooglePubSubAdapter

# log_level = logging.DEBUG
log_level = logging.INFO

logging.basicConfig(level=log_level)


if __name__ == "__main__":
	proj_name = "experiments"
	proj_id = "497610"
	channel_name = "exp-events"

	channel = f"projects/{proj_name}-{proj_id}/subscriptions/{channel_name}"

	# em = create_distributed_event_manager(AdaptersEnum.GCP_PUB_SUB, sub_channel=channel)
	em = create_distributed_event_manager(
		GooglePubSubAdapter(subscription=channel).init()
	)

	em.on_event("after-collapse-duplicates", )

	try:
		em.start()
	except KeyboardInterrupt:
		logging.info("Finishing the client app")
