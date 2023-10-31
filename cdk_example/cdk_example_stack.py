from aws_cdk import (
    Duration,
    Stack,
    App,
    aws_ec2 as ec2,
    aws_ecs as ecs, 
    aws_sqs as sqs,
)
from aws_cdk import aws_ecs_patterns

from constructs import Construct


class FlaskSqsAppStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define an SQS queue
        queue = sqs.Queue(
            self, "FlaskSqsQueue",
            queue_name="FlaskSqsQueue",
            visibility_timeout=Duration.seconds(300),
        )

        # Define an ECS cluster (where your service will be deployed)
        cluster = ecs.Cluster(
            self, "FlaskSqsAppCluster",
            cluster_name="FlaskSqsAppCluster",
            default_cloud_map_namespace=ecs.CloudMapNamespaceOptions(
                name="johns-name-space"
            ),            
        )
 
        task_definition = ecs.Ec2TaskDefinition(self, "QueueProcessingTaskDef")
        task_definition.add_container("QueueProcessingContainer",
            image=ecs.ContainerImage.from_registry("flask-sqs-app"),
            memory_limit_mib=512,  # Specify the memory limit in MiB
        )
        cluster.add_capacity(
            "CapacityId",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
            ),
            min_capacity=1,
            max_capacity=3,
        )

        # # Create the ECS Service with the previously built Docker image
        aws_ecs_patterns.QueueProcessingEc2Service(
            self, "FlaskSqsService",
            cluster=cluster,
            image=ecs.ContainerImage.from_registry("740239033577.dkr.ecr.us-east-1.amazonaws.com/flask-sqs-app:latest"),
            min_scaling_capacity=1,
            environment={
                "QUEUE_NAME": queue.queue_name
            },
            queue=queue,
            memory_limit_mib=512,  # Specify the memory limit in MiB
        )

app = App()
FlaskSqsAppStack(app, "FlaskSqsAppStack")
