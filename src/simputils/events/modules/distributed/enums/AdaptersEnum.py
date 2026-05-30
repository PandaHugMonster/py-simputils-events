from enum import StrEnum


class AdaptersEnum(StrEnum):

	GCP_PUB_SUB = "gcp-pub-sub"
	AWS_SQS = "aws-sqs"
	RABBIT_MQ = "rmq-rmqp"
